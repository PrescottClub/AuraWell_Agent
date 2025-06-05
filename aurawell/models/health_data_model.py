"""
Unified Health Data Models for AuraWell

This module defines Pydantic models for representing standardized health data
from various platforms (Xiaomi Health, Apple Health, Bohe Health).
All timestamps are normalized to UTC and units are standardized.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


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


class UnifiedActivitySummary(BaseModel):
    """
    Unified daily activity summary model
    
    Standardizes activity data from different platforms with consistent units:
    - Distance in meters
    - Calories in kcal
    - Duration in seconds
    """
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    steps: Optional[int] = Field(None, ge=0, description="Total daily steps")
    distance_meters: Optional[float] = Field(None, ge=0, description="Distance in meters")
    active_calories: Optional[float] = Field(None, ge=0, description="Active calories burned (kcal)")
    total_calories: Optional[float] = Field(None, ge=0, description="Total calories burned (kcal)")
    active_minutes: Optional[int] = Field(None, ge=0, description="Active minutes")
    source_platform: HealthPlatform = Field(..., description="Source health platform")
    data_quality: DataQuality = Field(DataQuality.UNKNOWN, description="Data quality indicator")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('date')
    def validate_date_format(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class SleepStage(str, Enum):
    """Sleep stage types"""
    DEEP = "deep"
    LIGHT = "light"
    REM = "rem"
    AWAKE = "awake"
    UNKNOWN = "unknown"


class UnifiedSleepSession(BaseModel):
    """
    Unified sleep session model
    
    Standardizes sleep data with all durations in seconds and UTC timestamps.
    """
    start_time_utc: datetime = Field(..., description="Sleep start time in UTC")
    end_time_utc: datetime = Field(..., description="Sleep end time in UTC")
    total_duration_seconds: Optional[int] = Field(None, ge=0, description="Total sleep duration in seconds")
    deep_sleep_seconds: Optional[int] = Field(None, ge=0, description="Deep sleep duration in seconds")
    light_sleep_seconds: Optional[int] = Field(None, ge=0, description="Light sleep duration in seconds")
    rem_sleep_seconds: Optional[int] = Field(None, ge=0, description="REM sleep duration in seconds")
    awake_seconds: Optional[int] = Field(None, ge=0, description="Awake time during sleep in seconds")
    sleep_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Sleep efficiency percentage")
    source_platform: HealthPlatform = Field(..., description="Source health platform")
    data_quality: DataQuality = Field(DataQuality.UNKNOWN, description="Data quality indicator")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('end_time_utc')
    def validate_sleep_duration(cls, v, values):
        """Validate that end time is after start time"""
        if 'start_time_utc' in values and v <= values['start_time_utc']:
            raise ValueError('End time must be after start time')
        return v


class HeartRateType(str, Enum):
    """Heart rate measurement types"""
    RESTING = "resting"
    ACTIVE = "active"
    PEAK = "peak"
    RECOVERY = "recovery"
    UNKNOWN = "unknown"


class UnifiedHeartRateSample(BaseModel):
    """
    Unified heart rate measurement model
    """
    timestamp_utc: datetime = Field(..., description="Measurement timestamp in UTC")
    bpm: int = Field(..., ge=30, le=220, description="Heart rate in beats per minute")
    measurement_type: HeartRateType = Field(HeartRateType.UNKNOWN, description="Type of heart rate measurement")
    context: Optional[str] = Field(None, description="Measurement context (e.g., 'during_workout', 'at_rest')")
    source_platform: HealthPlatform = Field(..., description="Source health platform")
    data_quality: DataQuality = Field(DataQuality.UNKNOWN, description="Data quality indicator")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkoutType(str, Enum):
    """Workout/exercise types"""
    RUNNING = "running"
    WALKING = "walking"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    STRENGTH_TRAINING = "strength_training"
    YOGA = "yoga"
    CARDIO = "cardio"
    OTHER = "other"


class UnifiedWorkoutSession(BaseModel):
    """
    Unified workout session model
    """
    start_time_utc: datetime = Field(..., description="Workout start time in UTC")
    end_time_utc: datetime = Field(..., description="Workout end time in UTC")
    workout_type: WorkoutType = Field(..., description="Type of workout")
    duration_seconds: int = Field(..., ge=0, description="Workout duration in seconds")
    calories_burned: Optional[float] = Field(None, ge=0, description="Calories burned during workout (kcal)")
    average_heart_rate: Optional[int] = Field(None, ge=30, le=220, description="Average heart rate during workout")
    max_heart_rate: Optional[int] = Field(None, ge=30, le=220, description="Maximum heart rate during workout")
    distance_meters: Optional[float] = Field(None, ge=0, description="Distance covered in meters")
    steps: Optional[int] = Field(None, ge=0, description="Steps taken during workout")
    source_platform: HealthPlatform = Field(..., description="Source health platform")
    data_quality: DataQuality = Field(DataQuality.UNKNOWN, description="Data quality indicator")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NutritionEntry(BaseModel):
    """
    Unified nutrition/food entry model
    """
    timestamp_utc: datetime = Field(..., description="Meal/food entry timestamp in UTC")
    meal_type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = Field(None, description="Type of meal")
    food_name: str = Field(..., description="Name of food item")
    calories: Optional[float] = Field(None, ge=0, description="Calories in kcal")
    protein_grams: Optional[float] = Field(None, ge=0, description="Protein content in grams")
    carbs_grams: Optional[float] = Field(None, ge=0, description="Carbohydrates content in grams")
    fat_grams: Optional[float] = Field(None, ge=0, description="Fat content in grams")
    fiber_grams: Optional[float] = Field(None, ge=0, description="Fiber content in grams")
    serving_size: Optional[str] = Field(None, description="Serving size description")
    source_platform: HealthPlatform = Field(..., description="Source health platform")
    data_quality: DataQuality = Field(DataQuality.UNKNOWN, description="Data quality indicator")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UnifiedHealthProfile(BaseModel):
    """
    Unified user health profile model
    
    Contains aggregated health metrics and goals
    """
    user_id: str = Field(..., description="Unique user identifier")
    age: Optional[int] = Field(None, ge=0, le=150, description="User age")
    gender: Optional[Literal["male", "female", "other"]] = Field(None, description="User gender")
    height_cm: Optional[float] = Field(None, ge=50, le=300, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, ge=20, le=500, description="Weight in kilograms")
    
    # Health goals
    daily_steps_goal: Optional[int] = Field(None, ge=0, description="Daily steps target")
    daily_calories_goal: Optional[float] = Field(None, ge=0, description="Daily calorie burn target")
    sleep_duration_goal_hours: Optional[float] = Field(None, ge=4, le=12, description="Sleep duration target in hours")
    
    # Current averages (last 7 days)
    avg_daily_steps: Optional[int] = Field(None, ge=0, description="Average daily steps (7 days)")
    avg_sleep_hours: Optional[float] = Field(None, ge=0, description="Average sleep hours (7 days)")
    avg_daily_calories: Optional[float] = Field(None, ge=0, description="Average daily calories burned (7 days)")
    
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Utility functions for data conversion

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight and height"""
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def seconds_to_hours(seconds: int) -> float:
    """Convert seconds to hours"""
    return seconds / 3600


def hours_to_seconds(hours: float) -> int:
    """Convert hours to seconds"""
    return int(hours * 3600) 