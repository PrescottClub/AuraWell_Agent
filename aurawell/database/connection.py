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
    # 在June082025的修复中添加如下方法，启用实例级别的监听器，方便未来的测试
    def has_sqlite_listener(self) -> bool:
        """检查是否已注册SQLite监听器"""
        if not self.engine:
            return False

        # 检查实例级别的事件监听器
        listeners = event.get(self.engine.sync_engine, "connect")
        return any(
            "set_sqlite_pragma" in str(listener).lower()
            for listener in listeners
        )

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

    # 在June082025的修复中，修改 _configure_sqlite 方法，使得其可以适配内存数据库级别的测试，理论上不会影响实际数据库的使用
    def _configure_sqlite(self) -> None:
        """配置 SQLite 数据库，区分内存和文件数据库"""
        if not self.engine:
            return

        # 对于内存数据库，只设置必要的 PRAGMA，使得内存数据库的测试可以进行下去
        if ":memory:" in self.database_url:
            logger.debug("Configuring in-memory SQLite")

            @event.listens_for(self.engine.sync_engine, "connect")
            def set_memory_pragma(dbapi_connection, connection_record):
                """设置内存数据库的 PRAGMA"""
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
        else:
            logger.debug("Configuring persistent SQLite")

            @event.listens_for(self.engine.sync_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                """设置 SQLite PRAGMA 以获得更好性能"""
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA foreign_keys=ON")
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
        # 进行了适当修改，在释放引擎时重置其相关属性
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
            self._initialized = False
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
