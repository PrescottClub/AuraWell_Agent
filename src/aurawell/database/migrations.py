"""
Database Migration Utilities

Provides tools for database schema initialization and migration.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from .base import Base
from .connection import DatabaseManager

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """
    Handles database schema migrations and initialization
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize migrator
        
        Args:
            database_manager: DatabaseManager instance
        """
        self.db_manager = database_manager
    
    async def initialize_database(self) -> bool:
        """
        Initialize database with all tables
        
        Returns:
            True if initialization was successful
        """
        try:
            await self.db_manager.initialize()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    async def create_tables(self) -> bool:
        """
        Create all tables defined in models
        
        Returns:
            True if tables were created successfully
        """
        try:
            if not self.db_manager.engine:
                await self.db_manager.initialize()
            
            async with self.db_manager.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("All tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            return False
    
    async def drop_tables(self) -> bool:
        """
        Drop all tables (use with caution!)
        
        Returns:
            True if tables were dropped successfully
        """
        try:
            if not self.db_manager.engine:
                await self.db_manager.initialize()
            
            async with self.db_manager.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            
            logger.warning("All tables dropped")
            return True
        except Exception as e:
            logger.error(f"Table dropping failed: {e}")
            return False
    
    async def check_table_exists(self, table_name: str) -> bool:
        """
        Check if a specific table exists
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists
        """
        try:
            if not self.db_manager.engine:
                await self.db_manager.initialize()
            
            async with self.db_manager.engine.connect() as conn:
                # Use SQLAlchemy's inspect to check table existence
                def check_table(sync_conn):
                    inspector = inspect(sync_conn)
                    return table_name in inspector.get_table_names()
                
                exists = await conn.run_sync(check_table)
                return exists
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    async def get_table_info(self) -> dict:
        """
        Get information about existing tables
        
        Returns:
            Dictionary with table information
        """
        try:
            if not self.db_manager.engine:
                await self.db_manager.initialize()
            
            async with self.db_manager.engine.connect() as conn:
                def get_info(sync_conn):
                    inspector = inspect(sync_conn)
                    tables = inspector.get_table_names()
                    
                    table_info = {}
                    for table in tables:
                        columns = inspector.get_columns(table)
                        table_info[table] = {
                            'columns': [col['name'] for col in columns],
                            'column_count': len(columns)
                        }
                    
                    return table_info
                
                return await conn.run_sync(get_info)
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {}
    
    async def reset_database(self) -> bool:
        """
        Reset database by dropping and recreating all tables
        
        Returns:
            True if reset was successful
        """
        logger.warning("Resetting database - all data will be lost!")
        
        try:
            # Drop all tables
            if not await self.drop_tables():
                return False
            
            # Recreate all tables
            if not await self.create_tables():
                return False
            
            logger.info("Database reset completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database reset failed: {e}")
            return False
    
    async def seed_initial_data(self) -> bool:
        """
        Seed database with initial data (if needed)
        
        Returns:
            True if seeding was successful
        """
        try:
            # This method can be extended to add initial data
            # For now, it's just a placeholder
            logger.info("Initial data seeding completed (no data to seed)")
            return True
        except Exception as e:
            logger.error(f"Data seeding failed: {e}")
            return False
    
    async def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Create database backup (SQLite only for now)
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if backup was successful
        """
        try:
            if not self.db_manager.database_url.startswith("sqlite"):
                logger.warning("Backup currently only supported for SQLite databases")
                return False
            
            # For SQLite, we can copy the database file
            import shutil
            import os
            from urllib.parse import urlparse
            
            # Extract database path from URL
            parsed = urlparse(self.db_manager.database_url)
            db_path = parsed.path.lstrip('/')
            
            if not os.path.exists(db_path):
                logger.error(f"Database file not found: {db_path}")
                return False
            
            if backup_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{db_path}.backup_{timestamp}"
            
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    async def validate_schema(self) -> bool:
        """
        Validate that database schema matches expected models
        
        Returns:
            True if schema is valid
        """
        try:
            expected_tables = set(Base.metadata.tables.keys())
            table_info = await self.get_table_info()
            existing_tables = set(table_info.keys())
            
            missing_tables = expected_tables - existing_tables
            extra_tables = existing_tables - expected_tables
            
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                return False
            
            if extra_tables:
                logger.info(f"Extra tables found: {extra_tables}")
            
            logger.info("Database schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False


async def init_database_schema(database_url: Optional[str] = None) -> bool:
    """
    Initialize database schema (convenience function)
    
    Args:
        database_url: Optional database URL
        
    Returns:
        True if initialization was successful
    """
    db_manager = DatabaseManager(database_url)
    migrator = DatabaseMigrator(db_manager)
    
    try:
        success = await migrator.initialize_database()
        if success:
            await migrator.seed_initial_data()
        return success
    finally:
        await db_manager.close()


async def reset_database_schema(database_url: Optional[str] = None) -> bool:
    """
    Reset database schema (convenience function)
    
    Args:
        database_url: Optional database URL
        
    Returns:
        True if reset was successful
    """
    db_manager = DatabaseManager(database_url)
    migrator = DatabaseMigrator(db_manager)
    
    try:
        return await migrator.reset_database()
    finally:
        await db_manager.close()


if __name__ == "__main__":
    import asyncio
    
    async def main():
        """CLI interface for database operations"""
        import sys
        
        if len(sys.argv) < 2:
            print("Usage: python migrations.py [init|reset|validate]")
            return
        
        command = sys.argv[1]
        
        if command == "init":
            success = await init_database_schema()
            print(f"Database initialization: {'SUCCESS' if success else 'FAILED'}")
        elif command == "reset":
            success = await reset_database_schema()
            print(f"Database reset: {'SUCCESS' if success else 'FAILED'}")
        elif command == "validate":
            db_manager = DatabaseManager()
            migrator = DatabaseMigrator(db_manager)
            try:
                success = await migrator.validate_schema()
                print(f"Schema validation: {'PASSED' if success else 'FAILED'}")
            finally:
                await db_manager.close()
        else:
            print(f"Unknown command: {command}")
    
    asyncio.run(main())
