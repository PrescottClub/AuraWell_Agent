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
    HealthPlanDB,
    HealthPlanModuleDB,
    HealthPlanProgressDB,
    HealthPlanFeedbackDB,
    HealthPlanTemplateDB,
)
from .family_models import (
    FamilyDB,
    FamilyMemberDB,
    FamilyInvitationDB,
    FamilyActivityLogDB,
    FamilyPermissionDB,
)
from .family_interaction_models import (
    FamilyMemberLikeDB,
    FamilyHealthAlertDB,
    FamilyInteractionStatsDB,
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
    "HealthPlanDB",
    "HealthPlanModuleDB",
    "HealthPlanProgressDB",
    "HealthPlanFeedbackDB",
    "HealthPlanTemplateDB",
    "FamilyDB",
    "FamilyMemberDB",
    "FamilyInvitationDB",
    "FamilyActivityLogDB",
    "FamilyPermissionDB",
    "FamilyMemberLikeDB",
    "FamilyHealthAlertDB",
    "FamilyInteractionStatsDB",
]
