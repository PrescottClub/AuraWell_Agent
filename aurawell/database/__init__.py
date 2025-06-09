"""
AuraWell Database Layer

Provides SQLAlchemy-based database integration for persistent data storage.
Supports SQLite (development), PostgreSQL (production), and in-memory (testing).
"""

from .connection import DatabaseManager, get_database_manager
from .base import Base
from .models import (
    UserProfileDB,
    ActivitySummaryDB,
    SleepSessionDB,
    HeartRateSampleDB,
    NutritionEntryDB,
    AchievementProgressDB,
    PlatformConnectionDB,
)
# 移除循环导入 - 对话模型将在需要时单独导入

__all__ = [
    "DatabaseManager",
    "get_database_manager",
    "Base",
    "UserProfileDB",
    "ActivitySummaryDB",
    "SleepSessionDB",
    "HeartRateSampleDB",
    "NutritionEntryDB",
    "AchievementProgressDB",
    "PlatformConnectionDB",
]
