"""
AuraWell Application Settings

This module contains configuration settings for the AuraWell application,
including API configurations, health platform settings, and system defaults.
"""

import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AuraWellSettings:
    """
    Centralized settings configuration for AuraWell
    """

    # Application metadata
    APP_NAME: str = "AuraWell"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "超个性化健康生活方式编排AI Agent"

    # Debug and logging
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # DeepSeek AI Configuration
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv(
        "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"
    )
    DEEPSEEK_DEFAULT_MODEL: str = os.getenv(
        "DEEPSEEK_DEFAULT_MODEL", "deepseek-r1-0528"
    )
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "2048"))
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))

    # Health Platform API Keys
    XIAOMI_HEALTH_API_KEY: Optional[str] = os.getenv("XIAOMI_HEALTH_API_KEY")
    XIAOMI_HEALTH_CLIENT_ID: Optional[str] = os.getenv("XIAOMI_HEALTH_CLIENT_ID")
    XIAOMI_HEALTH_CLIENT_SECRET: Optional[str] = os.getenv(
        "XIAOMI_HEALTH_CLIENT_SECRET"
    )

    APPLE_HEALTH_API_KEY: Optional[str] = os.getenv("APPLE_HEALTH_API_KEY")
    APPLE_HEALTH_CLIENT_ID: Optional[str] = os.getenv("APPLE_HEALTH_CLIENT_ID")
    APPLE_HEALTH_CLIENT_SECRET: Optional[str] = os.getenv("APPLE_HEALTH_CLIENT_SECRET")

    BOHE_HEALTH_API_KEY: Optional[str] = os.getenv("BOHE_HEALTH_API_KEY")
    BOHE_HEALTH_CLIENT_ID: Optional[str] = os.getenv("BOHE_HEALTH_CLIENT_ID")
    BOHE_HEALTH_CLIENT_SECRET: Optional[str] = os.getenv("BOHE_HEALTH_CLIENT_SECRET")

    # Health Data Configuration
    HEALTH_DATA_RETENTION_DAYS: int = int(
        os.getenv("HEALTH_DATA_RETENTION_DAYS", "365")
    )
    HEALTH_DATA_SYNC_INTERVAL_HOURS: int = int(
        os.getenv("HEALTH_DATA_SYNC_INTERVAL_HOURS", "6")
    )

    # AI Analysis Configuration
    MIN_DATA_POINTS_FOR_ANALYSIS: int = int(
        os.getenv("MIN_DATA_POINTS_FOR_ANALYSIS", "7")
    )
    INSIGHT_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("INSIGHT_CONFIDENCE_THRESHOLD", "0.7")
    )
    MAX_DAILY_RECOMMENDATIONS: int = int(os.getenv("MAX_DAILY_RECOMMENDATIONS", "5"))

    # Rate Limiting
    API_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "60"))
    API_RATE_LIMIT_PER_HOUR: int = int(os.getenv("API_RATE_LIMIT_PER_HOUR", "1000"))

    # Security
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")
    JWT_SECRET: Optional[str] = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # Database (if needed)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Default Health Goals
    DEFAULT_DAILY_STEPS: int = int(os.getenv("DEFAULT_DAILY_STEPS", "10000"))
    DEFAULT_SLEEP_HOURS: float = float(os.getenv("DEFAULT_SLEEP_HOURS", "8.0"))
    DEFAULT_WEEKLY_EXERCISE_MINUTES: int = int(
        os.getenv("DEFAULT_WEEKLY_EXERCISE_MINUTES", "150")
    )

    # Notification Settings
    ENABLE_NOTIFICATIONS: bool = (
        os.getenv("ENABLE_NOTIFICATIONS", "True").lower() == "true"
    )
    NOTIFICATION_TIME_MORNING: str = os.getenv("NOTIFICATION_TIME_MORNING", "08:00")
    NOTIFICATION_TIME_EVENING: str = os.getenv("NOTIFICATION_TIME_EVENING", "20:00")

    # External Services
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")

    # --- RAG Service Configuration ---
    ALIBABA_CLOUD_FC_ENDPOINT: Optional[str] = os.getenv("ALIBABA_CLOUD_FC_ENDPOINT")
    ALIBABA_CLOUD_ACCESS_KEY_ID: Optional[str] = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
    ALIBABA_CLOUD_ACCESS_KEY_SECRET: Optional[str] = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    RAG_FC_FUNCTION_NAME: str = os.getenv("RAG_FC_FUNCTION_NAME", "RAGmoudle")
    RAG_REQUEST_TIMEOUT: int = int(os.getenv("RAG_REQUEST_TIMEOUT", "30"))
    RAG_MAX_RETRIES: int = int(os.getenv("RAG_MAX_RETRIES", "3"))

    @classmethod
    def validate_required_settings(cls) -> List[str]:
        """
        Validate that required settings are configured

        Returns:
            List of missing required settings
        """
        missing_settings = []

        # Check critical settings
        if not cls.DEEPSEEK_API_KEY:
            missing_settings.append("DEEPSEEK_API_KEY")

        # Check RAG service settings
        if not cls.ALIBABA_CLOUD_FC_ENDPOINT:
            missing_settings.append("ALIBABA_CLOUD_FC_ENDPOINT")
        if not cls.ALIBABA_CLOUD_ACCESS_KEY_ID:
            missing_settings.append("ALIBABA_CLOUD_ACCESS_KEY_ID")
        if not cls.ALIBABA_CLOUD_ACCESS_KEY_SECRET:
            missing_settings.append("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

        return missing_settings

    @classmethod
    def get_health_platform_config(cls, platform_name: str) -> Dict[str, Optional[str]]:
        """
        Get configuration for a specific health platform

        Args:
            platform_name: Name of the platform (xiaomi, apple, bohe)

        Returns:
            Dictionary with platform configuration
        """
        platform_configs = {
            "xiaomi": {
                "api_key": cls.XIAOMI_HEALTH_API_KEY,
                "client_id": cls.XIAOMI_HEALTH_CLIENT_ID,
                "client_secret": cls.XIAOMI_HEALTH_CLIENT_SECRET,
            },
            "apple": {
                "api_key": cls.APPLE_HEALTH_API_KEY,
                "client_id": cls.APPLE_HEALTH_CLIENT_ID,
                "client_secret": cls.APPLE_HEALTH_CLIENT_SECRET,
            },
            "bohe": {
                "api_key": cls.BOHE_HEALTH_API_KEY,
                "client_id": cls.BOHE_HEALTH_CLIENT_ID,
                "client_secret": cls.BOHE_HEALTH_CLIENT_SECRET,
            },
        }

        return platform_configs.get(platform_name.lower(), {})

    @classmethod
    def get_rag_config(cls) -> Dict[str, Any]:
        """
        Get RAG service configuration

        Returns:
            Dictionary with RAG service configuration
        """
        return {
            "endpoint": cls.ALIBABA_CLOUD_FC_ENDPOINT,
            "access_key_id": cls.ALIBABA_CLOUD_ACCESS_KEY_ID,
            "access_key_secret": cls.ALIBABA_CLOUD_ACCESS_KEY_SECRET,
            "function_name": cls.RAG_FC_FUNCTION_NAME,
            "timeout": cls.RAG_REQUEST_TIMEOUT,
            "max_retries": cls.RAG_MAX_RETRIES,
        }

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Convert settings to dictionary (excluding sensitive data)

        Returns:
            Dictionary representation of settings
        """
        return {
            "app_name": cls.APP_NAME,
            "app_version": cls.APP_VERSION,
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "deepseek_base_url": cls.DEEPSEEK_BASE_URL,
            "deepseek_model": cls.DEEPSEEK_DEFAULT_MODEL,
            "health_data_retention_days": cls.HEALTH_DATA_RETENTION_DAYS,
            "min_data_points": cls.MIN_DATA_POINTS_FOR_ANALYSIS,
            "max_daily_recommendations": cls.MAX_DAILY_RECOMMENDATIONS,
            "default_daily_steps": cls.DEFAULT_DAILY_STEPS,
            "default_sleep_hours": cls.DEFAULT_SLEEP_HOURS,
            "timezone": cls.TIMEZONE,
        }


# Create global settings instance
settings = AuraWellSettings()


def get_settings() -> AuraWellSettings:
    """获取设置实例"""
    return settings


# 为了兼容性，添加redis_url属性
AuraWellSettings.redis_url = property(lambda self: self.REDIS_URL)

# Health platform specific configurations
HEALTH_PLATFORM_CONFIGS = {
    "xiaomi": {
        "base_url": "https://api.mi-health.xiaomi.com/v1",
        "rate_limit_per_minute": 20,
        "rate_limit_per_hour": 300,
        "supported_data_types": ["steps", "heart_rate", "sleep", "workouts"],
    },
    "apple": {
        "base_url": "https://api.apple-health-sync.com/v1",
        "rate_limit_per_minute": 30,
        "rate_limit_per_hour": 500,
        "supported_data_types": [
            "steps",
            "heart_rate",
            "sleep",
            "workouts",
            "nutrition",
        ],
    },
    "bohe": {
        "base_url": "https://api.boohee.com/v2",
        "rate_limit_per_minute": 30,
        "rate_limit_per_hour": 500,
        "supported_data_types": ["nutrition", "weight", "calories"],
    },
}

# AI Analysis Configuration
AI_ANALYSIS_CONFIG = {
    "activity_analysis": {
        "min_days_for_pattern": 7,
        "step_deficit_threshold": 0.8,
        "step_excellence_threshold": 1.2,
        "variance_threshold": 0.5,
    },
    "sleep_analysis": {
        "min_sessions_for_pattern": 5,
        "deficit_threshold_hours": 0.5,
        "efficiency_poor_threshold": 80,
        "efficiency_excellent_threshold": 90,
    },
    "heart_rate_analysis": {
        "min_samples_for_analysis": 10,
        "age_based_zones": True,
        "resting_hr_concern_threshold": 1.2,
    },
}

# Recommendation System Configuration
RECOMMENDATION_CONFIG = {
    "priority_weights": {
        "safety": 1.0,
        "user_goals": 0.9,
        "user_preferences": 0.8,
        "context_relevance": 0.7,
        "novelty": 0.3,
    },
    "frequency_limits": {"low": 2, "medium": 4, "high": 6},
    "category_distribution": {
        "activity": 0.4,
        "nutrition": 0.3,
        "sleep": 0.2,
        "stress": 0.1,
    },
}

# Gamification Configuration
GAMIFICATION_CONFIG = {
    "enabled": True,
    "badge_thresholds": {
        "steps": {"bronze": 5000, "silver": 8000, "gold": 12000, "platinum": 15000},
        "consistency": {
            "bronze": 3,
            "silver": 7,
            "gold": 14,
            "platinum": 30,
        },  # days in a row
        "sleep": {"bronze": 6.5, "silver": 7.5, "gold": 8.0, "platinum": 8.5},  # hours
    },
    "point_system": {
        "step_completed": 1,
        "workout_completed": 10,
        "sleep_goal_met": 5,
        "nutrition_logged": 3,
        "consistency_bonus": 5,
    },
}
