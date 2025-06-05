"""
AuraWell Data Models

Contains unified health data models and parsing utilities.
"""

# Explicit imports to avoid circular dependencies
from .health_data_model import (
    UnifiedActivitySummary, UnifiedSleepSession, UnifiedHeartRateSample,
    NutritionEntry, HealthPlatform, DataQuality
)
from .user_profile import (
    UserProfile, UserPreferences, HealthGoal, ActivityLevel, Gender
)