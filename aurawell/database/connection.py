"""
Database Connection Management for AuraWell

Provides unified database connection management supporting multiple backends:
- SQLite (for development and testing)
- PostgreSQL (for production)
- In-memory (for testing)
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseType(str, Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MEMORY = "memory"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    file_path: Optional[str] = None
    connection_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.connection_params is None:
            self.connection_params = {}


class DatabaseManager:
    """
    Unified database connection manager
    
    Provides a consistent interface for different database backends
    with connection pooling, transaction management, and error handling.
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database manager
        
        Args:
            config: Database configuration. If None, uses environment variables
        """
        self.config = config or self._load_config_from_env()
        self._connection = None
        self._is_connected = False
        
        logger.info(f"Database manager initialized for {self.config.db_type}")
    
    def _load_config_from_env(self) -> DatabaseConfig:
        """Load database configuration from environment variables"""
        db_type = os.getenv('AURAWELL_DB_TYPE', 'sqlite').lower()
        
        if db_type == 'sqlite':
            return DatabaseConfig(
                db_type=DatabaseType.SQLITE,
                file_path=os.getenv('AURAWELL_DB_PATH', 'aurawell.db')
            )
        elif db_type == 'postgresql':
            return DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                host=os.getenv('AURAWELL_DB_HOST', 'localhost'),
                port=int(os.getenv('AURAWELL_DB_PORT', '5432')),
                database=os.getenv('AURAWELL_DB_NAME', 'aurawell'),
                username=os.getenv('AURAWELL_DB_USER', 'aurawell'),
                password=os.getenv('AURAWELL_DB_PASSWORD', '')
            )
        elif db_type == 'memory':
            return DatabaseConfig(
                db_type=DatabaseType.MEMORY,
                file_path=':memory:'
            )
        else:
            # Default to SQLite
            return DatabaseConfig(
                db_type=DatabaseType.SQLITE,
                file_path='aurawell.db'
            )
    
    def connect(self) -> bool:
        """
        Establish database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.config.db_type == DatabaseType.SQLITE or self.config.db_type == DatabaseType.MEMORY:
                self._connection = sqlite3.connect(
                    self.config.file_path,
                    check_same_thread=False,
                    **self.config.connection_params
                )
                self._connection.row_factory = sqlite3.Row  # Enable dict-like access
                
            elif self.config.db_type == DatabaseType.POSTGRESQL:
                try:
                    import psycopg2
                    from psycopg2.extras import RealDictCursor
                    
                    self._connection = psycopg2.connect(
                        host=self.config.host,
                        port=self.config.port,
                        database=self.config.database,
                        user=self.config.username,
                        password=self.config.password,
                        cursor_factory=RealDictCursor,
                        **self.config.connection_params
                    )
                except ImportError:
                    logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
                    return False
            
            self._is_connected = True
            logger.info(f"Connected to {self.config.db_type} database")
            
            # Initialize database schema
            self._initialize_schema()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._is_connected = False
            logger.info("Database connection closed")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._is_connected and self._connection is not None
    
    @contextmanager
    def get_cursor(self):
        """
        Get database cursor with automatic cleanup
        
        Usage:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        """
        if not self.is_connected():
            raise RuntimeError("Database not connected")
        
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    @contextmanager
    def transaction(self):
        """
        Database transaction context manager
        
        Usage:
            with db_manager.transaction():
                # Database operations here
                # Automatically commits on success, rolls back on error
        """
        if not self.is_connected():
            raise RuntimeError("Database not connected")
        
        try:
            yield self._connection
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
    
    def execute_query(
        self,
        query: str,
        params: Optional[Union[tuple, dict]] = None,
        fetch_one: bool = False,
        fetch_all: bool = True
    ) -> Optional[Union[Dict[str, Any], list]]:
        """
        Execute a database query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Return only first result
            fetch_all: Return all results
            
        Returns:
            Query results or None
        """
        if not self.is_connected():
            raise RuntimeError("Database not connected")
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return None
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute query with multiple parameter sets
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples/dicts
            
        Returns:
            Number of affected rows
        """
        if not self.is_connected():
            raise RuntimeError("Database not connected")
        
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def _initialize_schema(self) -> None:
        """Initialize database schema with required tables"""
        try:
            # Create tables for different database types
            if self.config.db_type in [DatabaseType.SQLITE, DatabaseType.MEMORY]:
                self._create_sqlite_schema()
            elif self.config.db_type == DatabaseType.POSTGRESQL:
                self._create_postgresql_schema()

            logger.info("Database schema initialized")

        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    def _create_sqlite_schema(self) -> None:
        """Create SQLite database schema"""
        schema_queries = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                email TEXT,
                display_name TEXT,
                age INTEGER,
                gender TEXT,
                height_cm REAL,
                weight_kg REAL,
                activity_level TEXT,
                primary_goal TEXT,
                daily_steps_goal INTEGER,
                sleep_duration_goal_hours REAL,
                timezone TEXT DEFAULT 'UTC',
                preferences TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Health data table
            """
            CREATE TABLE IF NOT EXISTS health_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                data_type TEXT NOT NULL,  -- 'activity', 'sleep', 'heart_rate', 'nutrition'
                date TEXT NOT NULL,
                data_json TEXT NOT NULL,  -- JSON data
                source_platform TEXT,
                data_quality TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,

            # Insights table
            """
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                recommendations TEXT,  -- JSON array
                data_points TEXT,      -- JSON
                confidence_score REAL,
                generated_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,

            # Health plans table
            """
            CREATE TABLE IF NOT EXISTS health_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                goals TEXT,                    -- JSON
                daily_recommendations TEXT,    -- JSON
                weekly_targets TEXT,          -- JSON
                created_at TIMESTAMP NOT NULL,
                valid_until TIMESTAMP NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,

            # Create indexes for better performance
            "CREATE INDEX IF NOT EXISTS idx_users_user_id ON users (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_health_data_user_date ON health_data (user_id, date)",
            "CREATE INDEX IF NOT EXISTS idx_insights_user_id ON insights (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_health_plans_user_id ON health_plans (user_id)"
        ]

        with self.transaction():
            for query in schema_queries:
                self.execute_query(query, fetch_all=False)

    def _create_postgresql_schema(self) -> None:
        """Create PostgreSQL database schema"""
        schema_queries = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255),
                display_name VARCHAR(255),
                age INTEGER,
                gender VARCHAR(50),
                height_cm REAL,
                weight_kg REAL,
                activity_level VARCHAR(50),
                primary_goal VARCHAR(100),
                daily_steps_goal INTEGER,
                sleep_duration_goal_hours REAL,
                timezone VARCHAR(100) DEFAULT 'UTC',
                preferences JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Health data table
            """
            CREATE TABLE IF NOT EXISTS health_data (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                data_type VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                data_json JSONB NOT NULL,
                source_platform VARCHAR(100),
                data_quality VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,

            # Insights table
            """
            CREATE TABLE IF NOT EXISTS insights (
                id SERIAL PRIMARY KEY,
                insight_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                insight_type VARCHAR(50) NOT NULL,
                priority VARCHAR(50) NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                recommendations JSONB,
                data_points JSONB,
                confidence_score REAL,
                generated_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,

            # Health plans table
            """
            CREATE TABLE IF NOT EXISTS health_plans (
                id SERIAL PRIMARY KEY,
                plan_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                goals JSONB,
                daily_recommendations JSONB,
                weekly_targets JSONB,
                created_at TIMESTAMP NOT NULL,
                valid_until TIMESTAMP NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,

            # Create indexes
            "CREATE INDEX IF NOT EXISTS idx_users_user_id ON users (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_health_data_user_date ON health_data (user_id, date)",
            "CREATE INDEX IF NOT EXISTS idx_insights_user_id ON insights (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_health_plans_user_id ON health_plans (user_id)"
        ]

        with self.transaction():
            for query in schema_queries:
                self.execute_query(query, fetch_all=False)

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for debugging"""
        return {
            "db_type": self.config.db_type.value,
            "is_connected": self.is_connected(),
            "file_path": self.config.file_path if self.config.db_type == DatabaseType.SQLITE else None,
            "host": self.config.host if self.config.db_type == DatabaseType.POSTGRESQL else None,
            "database": self.config.database if self.config.db_type == DatabaseType.POSTGRESQL else None
        }
