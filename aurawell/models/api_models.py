"""
FastAPI Request/Response Models

Pydantic models for API request validation and response serialization.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


class ResponseStatus(str, Enum):
    """API response status enumeration"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseModel):
    """Base response model for all API endpoints"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Error response model"""
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Authentication Models
class LoginRequest(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseResponse):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds


# Chat Models
class ChatRequest(BaseModel):
    """Chat conversation request"""
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseResponse):
    """Chat conversation response"""
    reply: str
    user_id: str
    conversation_id: Optional[str] = None
    tools_used: Optional[List[str]] = None


# User Profile Models
class UserProfileRequest(BaseModel):
    """User profile update request"""
    display_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    weight_kg: Optional[float] = Field(None, ge=20, le=500)
    activity_level: Optional[str] = Field(None, pattern="^(sedentary|light|moderate|active|very_active)$")


class UserProfileResponse(BaseResponse):
    """User profile response"""
    user_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Health Goals Models
class HealthGoalRequest(BaseModel):
    """Health goal creation/update request"""
    goal_type: str = Field(..., pattern="^(weight_loss|weight_gain|fitness|nutrition|sleep|steps)$")
    target_value: float = Field(..., gt=0)
    target_unit: str = Field(..., max_length=20)
    target_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)


class HealthGoalResponse(BaseModel):
    """Health goal response"""
    goal_id: str
    goal_type: str
    target_value: float
    target_unit: str
    current_value: Optional[float] = None
    progress_percentage: Optional[float] = None
    target_date: Optional[date] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HealthGoalsListResponse(BaseResponse):
    """Health goals list response"""
    goals: List[HealthGoalResponse]
    total_count: int


# Health Summary Models
class ActivitySummary(BaseModel):
    """Activity summary data"""
    date: date
    steps: Optional[int] = None
    distance_km: Optional[float] = None
    calories_burned: Optional[int] = None
    active_minutes: Optional[int] = None
    exercise_sessions: Optional[int] = None


class SleepSummary(BaseModel):
    """Sleep summary data"""
    date: date
    total_sleep_hours: Optional[float] = None
    deep_sleep_hours: Optional[float] = None
    light_sleep_hours: Optional[float] = None
    rem_sleep_hours: Optional[float] = None
    sleep_efficiency: Optional[float] = None
    bedtime: Optional[datetime] = None
    wake_time: Optional[datetime] = None


class HealthSummaryResponse(BaseResponse):
    """Comprehensive health summary"""
    user_id: str
    period_start: date
    period_end: date
    activity_summary: Optional[ActivitySummary] = None
    sleep_summary: Optional[SleepSummary] = None
    average_heart_rate: Optional[float] = None
    weight_trend: Optional[str] = None
    key_insights: Optional[List[str]] = None


# Achievement Models
class Achievement(BaseModel):
    """Achievement data model"""
    achievement_id: str
    title: str
    description: str
    category: str
    progress: float = Field(..., ge=0, le=100)
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    reward_points: Optional[int] = None


class AchievementsResponse(BaseResponse):
    """Achievements list response"""
    achievements: List[Achievement]
    total_points: int
    completed_count: int
    in_progress_count: int


# Health Data Models
class HealthDataRequest(BaseModel):
    """Health data query request"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    data_types: Optional[List[str]] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)


class ActivityDataResponse(BaseResponse):
    """Activity data response"""
    user_id: str
    data: List[ActivitySummary]
    total_records: int


class SleepDataResponse(BaseResponse):
    """Sleep data response"""
    user_id: str
    data: List[SleepSummary]
    total_records: int


# Pagination Models
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseResponse):
    """Paginated response base"""
    page: int
    page_size: int
    total_pages: int
    total_items: int
    has_next: bool
    has_previous: bool
