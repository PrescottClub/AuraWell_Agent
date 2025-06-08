"""
Database Base Classes and Configuration

Provides SQLAlchemy declarative base and common database utilities.
"""
import os
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import DateTime, func, event, create_engine, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.engine import Engine
from sqlalchemy import TypeDecorator


class SQLiteUTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """写入数据库前的时区转换"""
        if value is not None:
            # 带时区时间 → 转换为UTC时间 → 移除时区信息
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            # 无时区时间 → 直接使用（假设已是UTC）
            return value
        return value

    def process_result_value(self, value, dialect):
        """从数据库读取后的时区处理"""
        if dialect.name == "sqlite" and value is not None:
            if isinstance(value, str):
                # SQLite字符串 → 添加UTC时区
                return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
            elif value.tzinfo is None:
                # 无时区对象 → 添加UTC时区
                return value.replace(tzinfo=timezone.utc)
        return value


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models
    
    Provides common fields and utilities for all database models.
    """

    # 在Base类中添加一个连接事件监听器，在数据库连接时覆盖获取时间函数，改为自行定义的，统一为UTC时区的时间函数
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if dbapi_connection.__class__.__module__ == "sqlite3.dbapi2":
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")

            # 覆盖SQLite的时间函数
            def utc_now():
                return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

            dbapi_connection.create_function("now", 0, utc_now)
            cursor.close()

    # Common timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        SQLiteUTCDateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        SQLiteUTCDateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        server_onupdate=func.now()
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        
        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update model instance from dictionary
        
        Args:
            data: Dictionary with field values to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__

        # 检查对象持久化状态
        if hasattr(self, 'id') and self.id is not None:
            # 持久化状态：显示实际ID
            return f"<{class_name} (id={self.id})>"

        # 通过SQLAlchemy内部状态判断对象状态
        from sqlalchemy import inspect
        state = inspect(self)

        if state.transient:
            # 瞬态：完全未关联数据库
            return f"<{class_name} []>"
        elif state.pending:
            # 挂起：已添加到session但未flush
            return f"<{class_name} [pending]>"
        elif state.detached:
            # 分离：已从session移除
            return f"<{class_name} [detached]>"

        # 默认回退
        return f"<{class_name}>"

DeclarativeBase = Base