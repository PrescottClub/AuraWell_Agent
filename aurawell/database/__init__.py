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
# Import conversation models to ensure they're registered with Base
from ..conversation.memory_manager import ConversationHistory
from ..conversation.session_manager import UserSession

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
    "ConversationHistory",
    "UserSession",
]
