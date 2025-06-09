"""
FastAPI Request/Response Models

Pydantic models for API request validation and response serialization.
"""

import re
import uuid
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator


class ResponseStatus(str, Enum):
    """API response status enumeration"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


# Generic type for data payload
T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API endpoints"""
    success: bool = True
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseResponse[None]):
    """Error response model"""
    success: bool = False
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            success=False,
            status=ResponseStatus.ERROR,
            message=message,
            error_code=error_code,
            details=details,
            **kwargs
        )


class SuccessResponse(BaseResponse[T]):
    """Success response model with data"""
    success: bool = True
    status: ResponseStatus = ResponseStatus.SUCCESS

    def __init__(
        self,
        data: T,
        message: str = "Operation completed successfully",
        **kwargs
    ):
        super().__init__(
            success=True,
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            **kwargs
        )


# Authentication Models
class LoginRequest(BaseModel):
    """User login request"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric and underscore only)"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Password (6-128 characters)"
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()  # Normalize to lowercase

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v.strip()) != len(v):
            raise ValueError('Password cannot start or end with whitespace')
        if v.lower() == v:
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class TokenData(BaseModel):
    """JWT token data"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds


class TokenResponse(SuccessResponse[TokenData]):
    """JWT token response"""
    pass


# Chat Models
class ChatRequest(BaseModel):
    """Chat conversation request"""
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = None


class ChatData(BaseModel):
    """Chat response data"""
    reply: str
    user_id: str
    conversation_id: Optional[str] = None
    tools_used: Optional[List[str]] = None


class ChatResponse(SuccessResponse[ChatData]):
    """Chat conversation response"""
    pass


# User Profile Models
class UserProfileRequest(BaseModel):
    """User profile update request"""
    display_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Display name (1-100 characters)"
    )
    email: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Valid email address"
    )
    age: Optional[int] = Field(
        None,
        ge=13,
        le=120,
        description="Age (13-120 years)"
    )
    gender: Optional[str] = Field(
        None,
        pattern="^(male|female|other)$",
        description="Gender (male, female, or other)"
    )
    height_cm: Optional[float] = Field(
        None,
        ge=50,
        le=300,
        description="Height in centimeters (50-300 cm)"
    )
    weight_kg: Optional[float] = Field(
        None,
        ge=20,
        le=500,
        description="Weight in kilograms (20-500 kg)"
    )
    activity_level: Optional[str] = Field(
        None,
        pattern="^(sedentary|lightly_active|moderately_active|very_active|extremely_active)$",
        description="Activity level"
    )

    @field_validator('display_name')
    @classmethod
    def validate_display_name(cls, v):
        """Validate display name"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Display name cannot be empty or only whitespace')
            # Check for inappropriate characters
            if re.search(r'[<>"\';\\]', v):
                raise ValueError('Display name contains invalid characters')
        return v

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v):
        """Additional email validation"""
        if v is not None:
            v = v.lower().strip()
            # Check for common email issues
            if '..' in v:
                raise ValueError('Email cannot contain consecutive dots')
            if v.startswith('.') or v.endswith('.'):
                raise ValueError('Email cannot start or end with a dot')
        return v

    @model_validator(mode='after')
    def validate_health_metrics(self):
        """Cross-field validation for health metrics"""
        if self.height_cm is not None and self.weight_kg is not None:
            # Calculate BMI for validation
            height_m = self.height_cm / 100
            bmi = self.weight_kg / (height_m ** 2)
            if bmi < 10 or bmi > 60:
                raise ValueError('Height and weight combination results in unrealistic BMI')

        if self.age is not None and self.age < 13:
            raise ValueError('Users must be at least 13 years old')

        return self


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
    goal_type: str = Field(
        ...,
        pattern="^(weight_loss|weight_gain|fitness|nutrition|sleep|steps)$",
        description="Type of health goal"
    )
    target_value: float = Field(
        ...,
        gt=0,
        description="Target value (must be positive)"
    )
    target_unit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unit of measurement (1-20 characters)"
    )
    target_date: Optional[date] = Field(
        None,
        description="Target completion date (optional)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Goal description (optional, max 500 characters)"
    )

    @field_validator('goal_type')
    @classmethod
    def validate_goal_type(cls, v):
        """Validate goal type"""
        valid_types = ['weight_loss', 'weight_gain', 'fitness', 'nutrition', 'sleep', 'steps']
        if v not in valid_types:
            raise ValueError(f'Goal type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator('target_value')
    @classmethod
    def validate_target_value(cls, v):
        """Validate target value based on reasonable ranges"""
        if v <= 0:
            raise ValueError('Target value must be positive')
        if v > 1000000:  # Reasonable upper limit
            raise ValueError('Target value is unreasonably high')
        return v

    @field_validator('target_unit')
    @classmethod
    def validate_target_unit(cls, v):
        """Validate target unit"""
        if v:
            v = v.strip().lower()
            if not v:
                raise ValueError('Target unit cannot be empty')
            # Common valid units
            valid_units = [
                'kg', 'lbs', 'steps', 'hours', 'minutes', 'calories',
                'km', 'miles', 'sessions', 'days', 'weeks'
            ]
            if v not in valid_units:
                # Allow other units but warn about common ones
                if not re.match(r'^[a-zA-Z/]+$', v):
                    raise ValueError('Target unit can only contain letters and forward slashes')
        return v

    @field_validator('target_date')
    @classmethod
    def validate_target_date(cls, v):
        """Validate target date"""
        if v is not None:
            today = date.today()
            if v < today:
                raise ValueError('Target date cannot be in the past')
            if v > today + timedelta(days=365 * 2):  # 2 years max
                raise ValueError('Target date cannot be more than 2 years in the future')
        return v

    @model_validator(mode='after')
    def validate_goal_combination(self):
        """Cross-field validation for goal combinations"""
        # Validate goal type and target value combinations
        if self.goal_type == 'steps' and self.target_value > 100000:
            raise ValueError('Daily steps goal cannot exceed 100,000')
        elif self.goal_type == 'sleep' and self.target_value > 12:
            raise ValueError('Sleep goal cannot exceed 12 hours')
        elif self.goal_type in ['weight_loss', 'weight_gain'] and self.target_value > 100:
            raise ValueError('Weight change goal cannot exceed 100 kg')
        elif self.goal_type == 'nutrition' and self.target_value > 10000:
            raise ValueError('Nutrition goal cannot exceed 10,000 calories')

        return self


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
    start_date: Optional[date] = Field(
        None,
        description="Start date for data query"
    )
    end_date: Optional[date] = Field(
        None,
        description="End date for data query"
    )
    data_types: Optional[List[str]] = Field(
        None,
        description="Types of data to retrieve"
    )
    limit: Optional[int] = Field(
        None,
        ge=1,
        le=1000,
        description="Maximum number of records to return (1-1000)"
    )

    @field_validator('data_types')
    @classmethod
    def validate_data_types(cls, v):
        """Validate data types"""
        if v is not None:
            valid_types = ['activity', 'sleep', 'nutrition', 'vitals']
            for data_type in v:
                if data_type not in valid_types:
                    valid_types_str = ", ".join(valid_types)
                    raise ValueError(
                        f'Invalid data type "{data_type}". Must be one of: {valid_types_str}'
                    )
        return v

    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate date range"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError('Start date cannot be after end date')

            # Check for reasonable date range
            date_diff = self.end_date - self.start_date
            if date_diff.days > 365:  # 1 year max
                raise ValueError('Date range cannot exceed 1 year')

        # Check dates are not in the future
        today = date.today()
        if self.start_date and self.start_date > today:
            raise ValueError('Start date cannot be in the future')
        if self.end_date and self.end_date > today:
            raise ValueError('End date cannot be in the future')

        return self


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
