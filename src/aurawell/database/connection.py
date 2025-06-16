"""
Database Connection Management

Handles SQLAlchemy engine creation, session management, and database initialization.
Supports multiple database backends: SQLite, PostgreSQL, and in-memory.
"""

import os
import logging
from typing import Optional, AsyncGenerator, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy import event, text
from sqlalchemy.pool import StaticPool

from ..config.settings import AuraWellSettings
from .base import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and sessions
    
    Provides async database operations with proper connection pooling
    and session management.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL. If None, uses settings.
        """
        self.database_url = database_url or self._get_database_url()
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._initialized = False
    
    def _get_database_url(self) -> str:
        """
        Get database URL from settings or create default SQLite URL
        
        Returns:
            Database connection URL
        """
        if AuraWellSettings.DATABASE_URL:
            return AuraWellSettings.DATABASE_URL
        
        # Default to SQLite in project directory
        db_path = os.path.join(os.getcwd(), "aurawell.db")
        return f"sqlite+aiosqlite:///{db_path}"
    
    async def initialize(self) -> None:
        """
        Initialize database engine and create tables
        """
        if self._initialized:
            return
        
        # Create async engine with appropriate settings
        engine_kwargs = self._get_engine_kwargs()
        self.engine = create_async_engine(self.database_url, **engine_kwargs)
        
        # Configure SQLite for better concurrency if using SQLite
        if self.database_url.startswith("sqlite"):
            self._configure_sqlite()
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create all tables
        await self._create_tables()
        
        self._initialized = True
        logger.info(f"Database initialized: {self.database_url}")
    
    def _get_engine_kwargs(self) -> Dict[str, Any]:
        """
        Get engine configuration based on database type
        
        Returns:
            Engine configuration dictionary
        """
        kwargs = {
            "echo": AuraWellSettings.DEBUG,
            "future": True,
        }
        
        if self.database_url.startswith("sqlite"):
            # SQLite-specific configuration
            kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 30,
                }
            })
        elif self.database_url.startswith("postgresql"):
            # PostgreSQL-specific configuration
            kwargs.update({
                "pool_size": 10,
                "max_overflow": 20,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            })
        
        return kwargs
    
    def _configure_sqlite(self) -> None:
        """Configure SQLite for better performance and concurrency"""
        if not self.engine:
            return
        
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance"""
            cursor = dbapi_connection.cursor()
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Optimize for speed
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
    
    async def _create_tables(self) -> None:
        """Create all database tables"""
        if not self.engine:
            raise RuntimeError("Database engine not initialized")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session with automatic cleanup
        
        Yields:
            AsyncSession instance
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.session_factory:
            raise RuntimeError("Session factory not initialized")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """
        Check database connectivity
        
        Returns:
            True if database is accessible
        """
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
_database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """
    Get global database manager instance
    
    Returns:
        DatabaseManager instance
    """
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager


async def init_database() -> None:
    """Initialize global database manager"""
    manager = get_database_manager()
    await manager.initialize()


async def close_database() -> None:
    """Close global database manager"""
    global _database_manager
    if _database_manager:
        await _database_manager.close()
        _database_manager = None
