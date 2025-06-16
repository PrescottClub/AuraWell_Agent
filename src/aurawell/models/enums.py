"""
Shared Enumerations for AuraWell

This module contains all shared enums used across the AuraWell application
to avoid code duplication and ensure consistency.
"""

from enum import Enum


class Gender(str, Enum):
    """User gender classification"""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, Enum):
    """User activity level classification"""

    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class HealthGoal(str, Enum):
    """Primary health goals"""

    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_GAIN = "muscle_gain"
    IMPROVE_FITNESS = "improve_fitness"
    IMPROVE_SLEEP = "improve_sleep"
    STRESS_REDUCTION = "stress_reduction"
    GENERAL_WELLNESS = "general_wellness"


class HealthPlatform(str, Enum):
    """Supported health data platforms"""

    XIAOMI_HEALTH = "XiaomiHealth"
    APPLE_HEALTH = "AppleHealth"
    BOHE_HEALTH = "BoheHealth"


class DataQuality(str, Enum):
    """Data quality indicators"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class HeartRateType(str, Enum):
    """Types of heart rate measurements"""

    RESTING = "resting"
    ACTIVE = "active"
    RECOVERY = "recovery"
    MAXIMUM = "maximum"
    UNKNOWN = "unknown"


class BMICategory(str, Enum):
    """BMI categories according to WHO standards"""

    UNDERWEIGHT = "underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    OBESE_CLASS_1 = "obese_class_1"
    OBESE_CLASS_2 = "obese_class_2"
    OBESE_CLASS_3 = "obese_class_3"


class HeartRateZone(str, Enum):
    """Heart rate training zones"""

    RECOVERY = "recovery"  # 50-60% of max HR
    AEROBIC_BASE = "aerobic_base"  # 60-70% of max HR
    AEROBIC = "aerobic"  # 70-80% of max HR
    ANAEROBIC = "anaerobic"  # 80-90% of max HR
    MAXIMUM = "maximum"  # 90-100% of max HR


class SleepStage(str, Enum):
    """Sleep stages"""

    AWAKE = "awake"
    LIGHT = "light"
    DEEP = "deep"
    REM = "rem"
    UNKNOWN = "unknown"


class WorkoutType(str, Enum):
    """Types of workouts"""

    RUNNING = "running"
    WALKING = "walking"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    STRENGTH_TRAINING = "strength_training"
    YOGA = "yoga"
    CARDIO = "cardio"
    SPORTS = "sports"
    OTHER = "other"


class NotificationType(str, Enum):
    """Types of notifications"""

    HEALTH_INSIGHT = "health_insight"
    GOAL_REMINDER = "goal_reminder"
    PLAN_UPDATE = "plan_update"
    ACHIEVEMENT = "achievement"
    WARNING = "warning"
    SYSTEM = "system"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AchievementType(str, Enum):
    """Types of achievements in gamification system"""

    DAILY_STEPS = "daily_steps"
    WEEKLY_STEPS = "weekly_steps"
    MONTHLY_STEPS = "monthly_steps"
    WORKOUT_FREQUENCY = "workout_frequency"
    SLEEP_QUALITY = "sleep_quality"
    CONSECUTIVE_DAYS = "consecutive_days"
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GOAL = "weight_goal"
    DISTANCE_MILESTONE = "distance_milestone"
    DISTANCE_COVERED = "distance_covered"
    CALORIE_BURN = "calorie_burn"
    HEART_RATE_ZONE = "heart_rate_zone"
    HEART_RATE_TARGET = "heart_rate_target"
    HEALTH_STREAK = "health_streak"
    HYDRATION = "hydration"
    NUTRITION_BALANCE = "nutrition_balance"
    STRESS_MANAGEMENT = "stress_management"
    SOCIAL_CHALLENGE = "social_challenge"


class AchievementDifficulty(str, Enum):
    """Achievement difficulty levels"""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class InsightType(str, Enum):
    """Types of health insights"""

    ACTIVITY_PATTERN = "activity_pattern"
    SLEEP_QUALITY = "sleep_quality"
    NUTRITION_BALANCE = "nutrition_balance"
    GOAL_PROGRESS = "goal_progress"
    HEALTH_TREND = "health_trend"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"


class InsightPriority(str, Enum):
    """Priority levels for insights"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationCategory(str, Enum):
    """Categories of health recommendations"""

    ACTIVITY = "activity"
    NUTRITION = "nutrition"
    SLEEP = "sleep"
    STRESS = "stress"
    HYDRATION = "hydration"
    RECOVERY = "recovery"
    GENERAL = "general"


class UserPreferenceType(str, Enum):
    """Types of user preferences"""

    COMMUNICATION_STYLE = "communication_style"
    REMINDER_FREQUENCY = "reminder_frequency"
    CHALLENGE_DIFFICULTY = "challenge_difficulty"
    NOTIFICATION_SETTINGS = "notification_settings"
    PRIVACY_SETTINGS = "privacy_settings"
