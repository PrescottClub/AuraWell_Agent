"""
User Profile Models for AuraWell

This module defines user profile and preference models for personalized health recommendations.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

from .enums import Gender, ActivityLevel, HealthGoal, HealthPlatform


class UserProfile(BaseModel):
    """
    Comprehensive user profile for AuraWell
    """

    # Basic information
    user_id: str = Field(..., description="Unique user identifier")
    email: Optional[str] = Field(None, description="User email address")
    display_name: Optional[str] = Field(None, description="User display name")

    # Demographics
    age: Optional[int] = Field(None, ge=13, le=120, description="User age")
    gender: Optional[Gender] = Field(None, description="User gender")
    height_cm: Optional[float] = Field(None, ge=50, le=300, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, ge=20, le=500, description="Current weight in kg")

    # Activity and goals
    activity_level: ActivityLevel = Field(ActivityLevel.MODERATELY_ACTIVE, description="Current activity level")
    primary_goal: HealthGoal = Field(HealthGoal.GENERAL_WELLNESS, description="Primary health goal")
    secondary_goals: List[HealthGoal] = Field(default_factory=list, description="Additional health goals")

    # Health targets
    target_weight_kg: Optional[float] = Field(None, ge=20, le=500, description="Target weight in kg")
    daily_steps_goal: int = Field(10000, ge=1000, le=50000, description="Daily steps target")
    daily_calories_goal: Optional[int] = Field(None, ge=1000, le=5000, description="Daily calorie intake target")
    sleep_duration_goal_hours: float = Field(8.0, ge=4.0, le=12.0, description="Target sleep duration")
    weekly_exercise_goal_minutes: int = Field(150, ge=0, le=1000, description="Weekly exercise target in minutes")

    # Connected platforms
    connected_platforms: List[HealthPlatform] = Field(default_factory=list, description="Connected health platforms")
    platform_user_ids: Dict[str, str] = Field(default_factory=dict, description="User IDs for each platform")

    # Preferences
    timezone: str = Field("UTC", description="User timezone")
    preferred_units: Literal["metric", "imperial"] = Field("metric", description="Preferred unit system")
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "daily_reminders": True,
            "goal_achievements": True,
            "weekly_reports": True,
            "motivational_messages": True,
        },
        description="Notification preferences",
    )

    # Privacy settings
    data_sharing_consent: bool = Field(False, description="Consent for data sharing")
    analytics_consent: bool = Field(False, description="Consent for analytics")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")


class UserPreferences(BaseModel):
    """
    User preferences for AI recommendations and interactions
    """

    user_id: str = Field(..., description="User identifier")

    # AI interaction preferences
    communication_style: Literal["formal", "casual", "motivational", "supportive"] = Field(
        "supportive", description="Preferred AI communication style"
    )
    reminder_frequency: Literal["low", "medium", "high"] = Field(
        "medium", description="Frequency of reminders and notifications"
    )
    challenge_difficulty: Literal["easy", "moderate", "challenging"] = Field(
        "moderate", description="Preferred challenge difficulty level"
    )

    # Health focus areas
    focus_areas: List[Literal["nutrition", "exercise", "sleep", "stress", "hydration"]] = Field(
        default_factory=lambda: ["exercise", "sleep"], description="Primary health focus areas"
    )

    # Schedule preferences
    preferred_workout_times: List[Literal["morning", "afternoon", "evening"]] = Field(
        default_factory=lambda: ["morning"], description="Preferred workout times"
    )
    available_days: List[Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]] = Field(
        default_factory=lambda: ["monday", "tuesday", "wednesday", "thursday", "friday"],
        description="Days available for planned activities",
    )

    # Restrictions and limitations
    dietary_restrictions: List[str] = Field(default_factory=list, description="Dietary restrictions")
    physical_limitations: List[str] = Field(default_factory=list, description="Physical limitations")
    medical_conditions: List[str] = Field(default_factory=list, description="Relevant medical conditions")

    # Gamification preferences
    gamification_enabled: bool = Field(True, description="Enable gamification features")
    badge_categories: List[str] = Field(
        default_factory=lambda: ["steps", "workouts", "sleep", "consistency"], description="Preferred badge categories"
    )

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserGoalProgress(BaseModel):
    """
    Track user progress towards health goals
    """

    user_id: str = Field(..., description="User identifier")
    goal_type: HealthGoal = Field(..., description="Type of health goal")

    # Goal details
    target_value: Optional[float] = Field(None, description="Target value for the goal")
    current_value: Optional[float] = Field(None, description="Current progress value")
    start_date: datetime = Field(..., description="Goal start date")
    target_date: Optional[datetime] = Field(None, description="Target completion date")

    # Progress tracking
    weekly_progress: List[float] = Field(default_factory=list, description="Weekly progress values")
    milestones_achieved: List[str] = Field(default_factory=list, description="Achieved milestones")

    # Status
    is_active: bool = Field(True, description="Whether goal is currently active")
    completion_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Completion percentage")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def calculate_bmi_from_profile(profile: UserProfile) -> Optional[float]:
    """
    Calculate BMI from user profile

    Args:
        profile: User profile with height and weight

    Returns:
        BMI value or None if height/weight not available
    """
    if profile.height_cm and profile.weight_kg:
        height_m = profile.height_cm / 100
        return profile.weight_kg / (height_m**2)
    return None


def get_recommended_daily_calories(profile: UserProfile) -> Optional[int]:
    """
    Calculate recommended daily calories based on user profile

    Args:
        profile: User profile

    Returns:
        Recommended daily calories or None if insufficient data
    """
    if not all([profile.age, profile.gender, profile.height_cm, profile.weight_kg]):
        return None

    # Simplified Mifflin-St Jeor Equation
    if profile.gender == Gender.MALE:
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
    else:  # female or other
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161

    # Activity multipliers
    activity_multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHTLY_ACTIVE: 1.375,
        ActivityLevel.MODERATELY_ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTREMELY_ACTIVE: 1.9,
    }

    multiplier = activity_multipliers.get(profile.activity_level, 1.55)
    return int(bmr * multiplier)


def create_default_user_profile(user_id: str, email: Optional[str] = None) -> UserProfile:
    """
    Create a default user profile with sensible defaults

    Args:
        user_id: Unique user identifier
        email: Optional user email

    Returns:
        UserProfile with default values
    """
    return UserProfile(
        user_id=user_id,
        email=email,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        primary_goal=HealthGoal.GENERAL_WELLNESS,
        daily_steps_goal=10000,
        sleep_duration_goal_hours=8.0,
        weekly_exercise_goal_minutes=150,
    )


def create_default_user_preferences(user_id: str) -> UserPreferences:
    """
    Create default user preferences

    Args:
        user_id: User identifier

    Returns:
        UserPreferences with default values
    """
    return UserPreferences(
        user_id=user_id,
        communication_style="supportive",
        reminder_frequency="medium",
        challenge_difficulty="moderate",
        focus_areas=["exercise", "sleep"],
        preferred_workout_times=["morning"],
        gamification_enabled=True,
    )
