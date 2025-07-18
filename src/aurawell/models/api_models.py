"""
FastAPI Request/Response Models

Pydantic models for API request validation and response serialization.
"""

import re
import uuid
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class ResponseStatus(str, Enum):
    """API response status enumeration"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


# Generic type for data payload
T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API endpoints"""

    success: bool = True
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    model_config = ConfigDict(
        # json_encoders deprecated in Pydantic v2
        # Using default datetime serialization which handles ISO format
    )


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
        **kwargs,
    ):
        super().__init__(
            success=False,
            status=ResponseStatus.ERROR,
            message=message,
            error_code=error_code,
            details=details,
            **kwargs,
        )


class SuccessResponse(BaseResponse[T]):
    """Success response model with data"""

    success: bool = True
    status: ResponseStatus = ResponseStatus.SUCCESS

    def __init__(
        self, data: T, message: str = "Operation completed successfully", **kwargs
    ):
        super().__init__(
            success=True,
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            **kwargs,
        )


# Authentication Models
class LoginRequest(BaseModel):
    """User login request"""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric and underscore only)",
    )
    password: str = Field(
        ..., min_length=6, max_length=128, description="Password (6-128 characters)"
    )


class RegisterRequest(BaseModel):
    """User registration request"""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric and underscore only)",
    )
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Valid email address",
    )
    password: str = Field(
        ..., min_length=6, max_length=128, description="Password (6-128 characters)"
    )
    health_data: Optional[Dict[str, Any]] = Field(
        None, description="Initial health data"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return v.lower()  # Normalize to lowercase

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password - simple and user-friendly rules"""
        if len(v.strip()) != len(v):
            raise ValueError("Password cannot start or end with whitespace")
        # 移除过于严格的要求，只保留基本的长度和空格检查
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
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatData(BaseModel):
    """Chat response data"""

    reply: str
    user_id: str
    conversation_id: Optional[str] = None
    tools_used: Optional[List[str]] = None


class ChatResponse(BaseResponse):
    """Chat conversation response - 保持向后兼容的格式"""

    reply: str
    user_id: str
    conversation_id: Optional[str] = None
    tools_used: Optional[List[str]] = None


# Enhanced Chat Models for Health Management
class HealthChatRequest(BaseModel):
    """Enhanced health chat request with conversation context"""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class HealthSuggestion(BaseModel):
    """Health suggestion card"""

    title: str
    content: str
    action: Optional[str] = None
    action_text: Optional[str] = None


class QuickReply(BaseModel):
    """Quick reply option"""

    text: str


class HealthChatResponse(BaseResponse):
    """Enhanced health chat response with suggestions and quick replies"""

    reply: str
    conversation_id: str
    message_id: str
    timestamp: datetime
    suggestions: Optional[List[HealthSuggestion]] = None
    quick_replies: Optional[List[QuickReply]] = None


# Conversation Management Models
class ConversationCreateRequest(BaseModel):
    """Request to create a new conversation"""

    type: str = Field(default="health_consultation")
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Conversation metadata response"""

    conversation_id: str
    type: str
    created_at: datetime
    title: Optional[str] = None
    status: str = "active"


class ConversationListItem(BaseModel):
    """Conversation list item"""

    id: str
    title: Optional[str] = None
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    status: str = "active"


class ConversationListResponse(BaseResponse):
    """List of user conversations"""

    conversations: List[ConversationListItem] = Field(default_factory=list)


# Message History Models
class ChatMessage(BaseModel):
    """Individual chat message"""

    id: str
    sender: str  # 'user' or 'agent'
    content: str
    timestamp: datetime
    suggestions: Optional[List[HealthSuggestion]] = None
    quick_replies: Optional[List[QuickReply]] = None


class ChatHistoryRequest(BaseModel):
    """Request for chat history"""

    conversation_id: str
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ChatHistoryResponse(BaseResponse):
    """Chat history response"""

    messages: List[ChatMessage]
    total: int
    has_more: bool


# Health Suggestions Models
class HealthSuggestionsResponse(BaseResponse):
    """Health suggestions template response"""

    suggestions: List[str]


# User Profile Models
class UserProfileRequest(BaseModel):
    """User profile update request"""

    display_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Display name (1-100 characters)",
    )
    email: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Valid email address",
    )
    age: Optional[int] = Field(None, ge=13, le=120, description="Age (13-120 years)")
    gender: Optional[str] = Field(
        None,
        pattern="^(male|female|other)$",
        description="Gender (male, female, or other)",
    )
    height_cm: Optional[float] = Field(
        None, ge=50, le=300, description="Height in centimeters (50-300 cm)"
    )
    weight_kg: Optional[float] = Field(
        None, ge=20, le=500, description="Weight in kilograms (20-500 kg)"
    )
    activity_level: Optional[str] = Field(
        None,
        pattern="^(sedentary|lightly_active|moderately_active|very_active|extremely_active)$",
        description="Activity level",
    )

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v):
        """Validate display name"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Display name cannot be empty or only whitespace")
            # Check for inappropriate characters
            if re.search(r'[<>"\';\\]', v):
                raise ValueError("Display name contains invalid characters")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        """Additional email validation"""
        if v is not None:
            v = v.lower().strip()
            # Check for common email issues
            if ".." in v:
                raise ValueError("Email cannot contain consecutive dots")
            if v.startswith(".") or v.endswith("."):
                raise ValueError("Email cannot start or end with a dot")
        return v

    @model_validator(mode="after")
    def validate_health_metrics(self):
        """Cross-field validation for health metrics"""
        if self.height_cm is not None and self.weight_kg is not None:
            # Calculate BMI for validation
            height_m = self.height_cm / 100
            bmi = self.weight_kg / (height_m**2)
            if bmi < 10 or bmi > 60:
                raise ValueError(
                    "Height and weight combination results in unrealistic BMI"
                )

        if self.age is not None and self.age < 13:
            raise ValueError("Users must be at least 13 years old")

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
        description="Type of health goal",
    )
    target_value: float = Field(
        ..., gt=0, description="Target value (must be positive)"
    )
    target_unit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unit of measurement (1-20 characters)",
    )
    target_date: Optional[date] = Field(
        None, description="Target completion date (optional)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Goal description (optional, max 500 characters)",
    )

    @field_validator("goal_type")
    @classmethod
    def validate_goal_type(cls, v):
        """Validate goal type"""
        valid_types = [
            "weight_loss",
            "weight_gain",
            "fitness",
            "nutrition",
            "sleep",
            "steps",
        ]
        if v not in valid_types:
            raise ValueError(f'Goal type must be one of: {", ".join(valid_types)}')
        return v

    @field_validator("target_value")
    @classmethod
    def validate_target_value(cls, v):
        """Validate target value based on reasonable ranges"""
        if v <= 0:
            raise ValueError("Target value must be positive")
        if v > 1000000:  # Reasonable upper limit
            raise ValueError("Target value is unreasonably high")
        return v

    @field_validator("target_unit")
    @classmethod
    def validate_target_unit(cls, v):
        """Validate target unit"""
        if v:
            v = v.strip().lower()
            if not v:
                raise ValueError("Target unit cannot be empty")
            # Common valid units
            valid_units = [
                "kg",
                "lbs",
                "steps",
                "hours",
                "minutes",
                "calories",
                "km",
                "miles",
                "sessions",
                "days",
                "weeks",
            ]
            if v not in valid_units:
                # Allow other units but warn about common ones
                if not re.match(r"^[a-zA-Z/]+$", v):
                    raise ValueError(
                        "Target unit can only contain letters and forward slashes"
                    )
        return v

    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, v):
        """Validate target date"""
        if v is not None:
            today = date.today()
            if v < today:
                raise ValueError("Target date cannot be in the past")
            if v > today + timedelta(days=365 * 2):  # 2 years max
                raise ValueError(
                    "Target date cannot be more than 2 years in the future"
                )
        return v

    @model_validator(mode="after")
    def validate_goal_combination(self):
        """Cross-field validation for goal combinations"""
        # Validate goal type and target value combinations
        if self.goal_type == "steps" and self.target_value > 100000:
            raise ValueError("Daily steps goal cannot exceed 100,000")
        elif self.goal_type == "sleep" and self.target_value > 12:
            raise ValueError("Sleep goal cannot exceed 12 hours")
        elif (
            self.goal_type in ["weight_loss", "weight_gain"] and self.target_value > 100
        ):
            raise ValueError("Weight change goal cannot exceed 100 kg")
        elif self.goal_type == "nutrition" and self.target_value > 10000:
            raise ValueError("Nutrition goal cannot exceed 10,000 calories")

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

    start_date: Optional[date] = Field(None, description="Start date for data query")
    end_date: Optional[date] = Field(None, description="End date for data query")
    data_types: Optional[List[str]] = Field(
        None, description="Types of data to retrieve"
    )
    limit: Optional[int] = Field(
        None, ge=1, le=1000, description="Maximum number of records to return (1-1000)"
    )

    @field_validator("data_types")
    @classmethod
    def validate_data_types(cls, v):
        """Validate data types"""
        if v is not None:
            valid_types = ["activity", "sleep", "nutrition", "vitals"]
            for data_type in v:
                if data_type not in valid_types:
                    valid_types_str = ", ".join(valid_types)
                    raise ValueError(
                        f'Invalid data type "{data_type}". Must be one of: {valid_types_str}'
                    )
        return v

    @model_validator(mode="after")
    def validate_date_range(self):
        """Validate date range"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Start date cannot be after end date")

            # Check for reasonable date range
            date_diff = self.end_date - self.start_date
            if date_diff.days > 365:  # 1 year max
                raise ValueError("Date range cannot exceed 1 year")

        # Check dates are not in the future
        today = date.today()
        if self.start_date and self.start_date > today:
            raise ValueError("Start date cannot be in the future")
        if self.end_date and self.end_date > today:
            raise ValueError("End date cannot be in the future")

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


# Pagination and Filtering Models
class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(1, ge=1, le=1000, description="Page number (1-1000)")
    page_size: int = Field(
        20, ge=1, le=100, description="Number of items per page (1-100)"
    )

    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size


class SortParams(BaseModel):
    """Sorting parameters"""

    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"
    )

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sort field"""
        if v is not None:
            # Common sortable fields
            allowed_fields = [
                "created_at",
                "updated_at",
                "date",
                "timestamp",
                "name",
                "title",
                "value",
                "progress",
                "status",
            ]
            if v not in allowed_fields:
                # Allow other fields but validate format
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
                    raise ValueError("Sort field must be a valid field name")
        return v


class FilterParams(BaseModel):
    """Base filtering parameters"""

    search: Optional[str] = Field(
        None, max_length=100, description="Search term for text fields"
    )
    status: Optional[str] = Field(None, description="Filter by status")
    date_from: Optional[date] = Field(None, description="Filter from date (inclusive)")
    date_to: Optional[date] = Field(None, description="Filter to date (inclusive)")

    @field_validator("search")
    @classmethod
    def validate_search(cls, v):
        """Validate search term"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            # Remove potentially dangerous characters
            if re.search(r'[<>"\';\\]', v):
                raise ValueError("Search term contains invalid characters")
        return v

    @model_validator(mode="after")
    def validate_date_range(self):
        """Validate date range"""
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValueError("date_from cannot be after date_to")

            # Check for reasonable date range
            date_diff = self.date_to - self.date_from
            if date_diff.days > 365:  # 1 year max
                raise ValueError("Date range cannot exceed 1 year")

        return self


# Specific Filter Classes
class HealthGoalFilterParams(FilterParams):
    """Health goal specific filtering parameters"""

    goal_type: Optional[str] = Field(
        None,
        pattern="^(weight_loss|weight_gain|fitness|nutrition|sleep|steps)$",
        description="Filter by goal type",
    )
    is_completed: Optional[bool] = Field(
        None, description="Filter by completion status"
    )
    target_date_from: Optional[date] = Field(
        None, description="Filter goals with target date from this date"
    )
    target_date_to: Optional[date] = Field(
        None, description="Filter goals with target date to this date"
    )


class HealthDataFilterParams(FilterParams):
    """Health data specific filtering parameters"""

    data_types: Optional[List[str]] = Field(
        None, description="Filter by data types (activity, sleep, nutrition, vitals)"
    )
    source_platform: Optional[str] = Field(
        None, description="Filter by source platform"
    )
    quality_threshold: Optional[str] = Field(
        None,
        pattern="^(low|medium|high)$",
        description="Minimum data quality threshold",
    )

    @field_validator("data_types")
    @classmethod
    def validate_data_types(cls, v):
        """Validate data types"""
        if v is not None:
            valid_types = ["activity", "sleep", "nutrition", "vitals"]
            for data_type in v:
                if data_type not in valid_types:
                    valid_types_str = ", ".join(valid_types)
                    raise ValueError(
                        f'Invalid data type "{data_type}". Must be one of: {valid_types_str}'
                    )
        return v


class AchievementFilterParams(FilterParams):
    """Achievement specific filtering parameters"""

    category: Optional[str] = Field(None, description="Filter by achievement category")
    is_unlocked: Optional[bool] = Field(None, description="Filter by unlock status")
    difficulty: Optional[str] = Field(
        None,
        pattern="^(easy|medium|hard|expert)$",
        description="Filter by difficulty level",
    )


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    page: int
    page_size: int
    total_pages: int
    total_items: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> "PaginationMeta":
        """Create pagination metadata"""
        total_pages = (
            (total_items + page_size - 1) // page_size if total_items > 0 else 1
        )

        return cls(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_items=total_items,
            has_next=page < total_pages,
            has_previous=page > 1,
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with data and metadata"""

    success: bool = True
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Data retrieved successfully"
    data: List[T]
    pagination: PaginationMeta
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    model_config = ConfigDict(
        # json_encoders deprecated in Pydantic v2
        # Using default datetime serialization which handles ISO format
    )


# New Paginated Response Models
class PaginatedHealthGoalsResponse(PaginatedResponse[HealthGoalResponse]):
    """Paginated health goals response"""

    pass


class PaginatedActivityDataResponse(PaginatedResponse[ActivitySummary]):
    """Paginated activity data response"""

    pass


class PaginatedSleepDataResponse(PaginatedResponse[SleepSummary]):
    """Paginated sleep data response"""

    pass


class PaginatedAchievementsResponse(PaginatedResponse[Achievement]):
    """Paginated achievements response"""

    pass


# Batch Operation Models
class BatchHealthGoalRequest(BaseModel):
    """Batch health goal operations request"""

    operation: str = Field(
        ..., pattern="^(create|update|delete)$", description="Batch operation type"
    )
    goals: List[HealthGoalRequest] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of health goals (1-50 items)",
    )

    @field_validator("goals")
    @classmethod
    def validate_goals_count(cls, v):
        """Validate goals count"""
        if len(v) > 50:
            raise ValueError("Cannot process more than 50 goals in a single batch")
        return v


class BatchOperationResult(BaseModel):
    """Result of a batch operation"""

    success_count: int = Field(..., description="Number of successful operations")
    error_count: int = Field(..., description="Number of failed operations")
    total_count: int = Field(..., description="Total number of operations")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of errors for failed operations"
    )

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100


class BatchHealthGoalResponse(SuccessResponse[BatchOperationResult]):
    """Batch health goal operations response"""

    pass


# Health Plan Models
class HealthPlanModule(BaseModel):
    """Health plan module"""

    module_type: str = Field(
        ..., description="Module type (diet, exercise, weight, sleep, mental)"
    )
    title: str = Field(..., description="Module title")
    description: str = Field(..., description="Module description")
    content: Dict[str, Any] = Field(..., description="Module content")
    duration_days: int = Field(..., description="Module duration in days")

    # 添加兼容性字段
    @property
    def type(self) -> str:
        """兼容性字段：前端期望的type字段"""
        return self.module_type

    def model_dump(self, **kwargs):
        """重写序列化方法，包含兼容性字段"""
        data = super().model_dump(**kwargs)
        data["type"] = self.module_type
        return data


class HealthPlan(BaseModel):
    """Health plan model"""

    plan_id: str
    title: str
    description: str
    modules: List[HealthPlanModule]
    duration_days: int
    status: str = Field(default="active", description="Plan status")
    progress: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Completion progress"
    )
    created_at: datetime
    updated_at: datetime
    recommendations: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Expert recommendations"
    )

    # 添加兼容性字段
    @property
    def id(self) -> str:
        """兼容性字段：前端期望的id字段"""
        return self.plan_id

    @property
    def duration(self) -> int:
        """兼容性字段：前端期望的duration字段"""
        return self.duration_days

    def model_dump(self, **kwargs):
        """重写序列化方法，包含兼容性字段"""
        data = super().model_dump(**kwargs)
        data["id"] = self.plan_id
        data["duration"] = self.duration_days
        return data


class HealthPlanRequest(BaseModel):
    """Health plan generation request"""

    goals: List[str] = Field(..., description="Health goals")
    modules: List[str] = Field(..., description="Plan modules to include")
    duration_days: int = Field(
        default=30, ge=7, le=365, description="Plan duration in days"
    )
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class HealthPlanResponse(BaseResponse):
    """Health plan response"""

    plan: HealthPlan


class HealthPlansListResponse(BaseResponse):
    """Health plans list response"""

    plans: List[HealthPlan]
    total_count: int


class HealthPlanGenerateRequest(BaseModel):
    """Health plan generation request"""

    goals: List[str] = Field(..., min_length=1, description="Health goals")
    modules: List[str] = Field(..., min_length=1, description="Plan modules")
    duration_days: int = Field(default=30, ge=7, le=365, description="Plan duration")
    user_preferences: Optional[Dict[str, Any]] = Field(
        None, description="User preferences"
    )


class HealthPlanGenerateResponse(BaseResponse):
    """Health plan generation response"""

    plan: HealthPlan
    recommendations: List[str] = Field(
        default=[], description="Additional recommendations"
    )


# User Health Data Models
class UserHealthDataRequest(BaseModel):
    """User health data update request"""

    age: Optional[int] = Field(None, ge=13, le=120, description="Age")
    gender: Optional[str] = Field(
        None, pattern="^(male|female|other)$", description="Gender"
    )
    height: Optional[float] = Field(None, ge=50, le=300, description="Height in cm")
    weight: Optional[float] = Field(None, ge=20, le=500, description="Weight in kg")
    activity_level: Optional[str] = Field(None, description="Activity level")


class UserHealthDataResponse(BaseResponse):
    """User health data response"""

    user_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    activity_level: Optional[str] = None
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    updated_at: datetime


# User Health Goals Models
class UserHealthGoalRequest(BaseModel):
    """User health goal creation/update request"""

    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Goal description"
    )
    type: str = Field(..., description="Goal type")
    target_value: Optional[float] = Field(None, description="Target value")
    current_value: Optional[float] = Field(None, description="Current value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    target_date: Optional[date] = Field(None, description="Target completion date")
    status: str = Field(default="active", description="Goal status")


class UserHealthGoalResponse(BaseModel):
    """User health goal response"""

    id: str
    title: str
    description: Optional[str] = None
    type: str
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    target_date: Optional[date] = None
    status: str
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    created_at: datetime
    updated_at: datetime


class UserHealthGoalsListResponse(BaseResponse):
    """User health goals list response"""

    goals: List[UserHealthGoalResponse]
    total_count: int


# Health Advice Models
class HealthAdviceRequest(BaseModel):
    """健康建议生成请求"""

    goal_type: Optional[str] = Field(
        None, description="健康目标类型 (weight_loss, muscle_gain, general_wellness)"
    )
    duration_weeks: Optional[int] = Field(4, description="计划周期（周）", ge=1, le=52)
    special_requirements: Optional[List[str]] = Field(None, description="特殊要求列表")


class HealthAdviceSection(BaseModel):
    """健康建议单个模块"""

    title: str = Field(..., description="模块标题")
    content: str = Field(..., description="建议内容")
    recommendations: List[str] = Field(default_factory=list, description="核心推荐")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="相关指标")


class HealthAdviceData(BaseModel):
    """健康建议数据"""

    diet: HealthAdviceSection = Field(..., description="饮食建议")
    exercise: HealthAdviceSection = Field(..., description="运动计划")
    weight: HealthAdviceSection = Field(..., description="体重管理")
    sleep: HealthAdviceSection = Field(..., description="睡眠优化")
    mental_health: HealthAdviceSection = Field(..., description="心理健康")


class HealthAdviceResponse(BaseResponse):
    """健康建议响应"""

    data: Optional[Dict[str, Any]] = Field(None, description="健康建议数据")


# ================================
# Family Management Models
# ================================


class FamilyRole(str, Enum):
    """Family member role enumeration"""

    OWNER = "owner"  # Full control, can delete family
    MANAGER = "manager"  # Can invite/remove members, view all data
    VIEWER = "viewer"  # Can only view shared data


class InviteStatus(str, Enum):
    """Invitation status enumeration"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class FamilyCreateRequest(BaseModel):
    """Request to create a new family"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Family name (1-100 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Family description (optional, max 500 characters)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate family name"""
        if not v.strip():
            raise ValueError("Family name cannot be empty or whitespace only")
        return v.strip()


class FamilyMember(BaseModel):
    """Family member information"""

    user_id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    role: FamilyRole
    joined_at: datetime
    last_active: Optional[datetime] = None
    is_active: bool = True


class FamilyInfo(BaseModel):
    """Family information"""

    family_id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    created_at: datetime
    updated_at: datetime
    member_count: int
    is_active: bool = True


class FamilyInfoResponse(SuccessResponse[FamilyInfo]):
    """Family information response"""

    pass


class FamilyListResponse(SuccessResponse[List[FamilyInfo]]):
    """Family list response"""

    pass


class InviteMemberRequest(BaseModel):
    """Request to invite a member to family"""

    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Valid email address of the user to invite",
    )
    role: FamilyRole = Field(
        default=FamilyRole.VIEWER, description="Role to assign to the invited member"
    )
    message: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional invitation message (max 500 characters)",
    )


class InviteInfo(BaseModel):
    """Invitation information"""

    invite_id: str
    family_id: str
    family_name: str
    inviter_id: str
    inviter_name: str
    invitee_email: str
    role: FamilyRole
    status: InviteStatus
    message: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    responded_at: Optional[datetime] = None


class InviteMemberResponse(SuccessResponse[InviteInfo]):
    """Invite member response"""

    pass


class PendingInviteResponse(SuccessResponse[List[InviteInfo]]):
    """Pending invitations response"""

    pass


class AcceptInviteRequest(BaseModel):
    """Request to accept a family invitation"""

    invite_code: str = Field(
        ..., min_length=1, description="Invitation code received via email"
    )


class DeclineInviteRequest(BaseModel):
    """Request to decline a family invitation"""

    invite_code: str = Field(
        ..., min_length=1, description="Invitation code received via email"
    )
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional reason for declining (max 200 characters)",
    )


class FamilyMembersResponse(SuccessResponse[List[FamilyMember]]):
    """Family members list response"""

    pass


class UpdateMemberRoleRequest(BaseModel):
    """Request to update a family member's role"""

    user_id: str = Field(..., description="User ID of the member to update")
    new_role: FamilyRole = Field(..., description="New role to assign")

    @field_validator("new_role")
    @classmethod
    def validate_role_change(cls, v):
        """Validate role change"""
        if v == FamilyRole.OWNER:
            raise ValueError(
                "Cannot assign owner role through role update. Use transfer ownership instead."
            )
        return v


class RemoveMemberRequest(BaseModel):
    """Request to remove a family member"""

    user_id: str = Field(..., description="User ID of the member to remove")
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional reason for removal (max 200 characters)",
    )


class TransferOwnershipRequest(BaseModel):
    """Request to transfer family ownership"""

    new_owner_id: str = Field(..., description="User ID of the new owner")
    confirmation_message: str = Field(
        ...,
        pattern="^I understand that I will lose ownership of this family$",
        description="Confirmation message to prevent accidental transfers",
    )


class LeaveFamilyRequest(BaseModel):
    """Request to leave a family"""

    family_id: str = Field(..., description="Family ID to leave")
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional reason for leaving (max 200 characters)",
    )


class DeleteFamilyRequest(BaseModel):
    """Request to delete a family (owner only)"""

    family_id: str = Field(..., description="Family ID to delete")
    confirmation_message: str = Field(
        ...,
        pattern="^DELETE FAMILY PERMANENTLY$",
        description="Confirmation message to prevent accidental deletion",
    )


class FamilyPermissionInfo(BaseModel):
    """Family permission information for a user"""

    family_id: str
    user_id: str
    role: FamilyRole
    permissions: List[str]  # List of specific permissions
    can_invite_members: bool
    can_remove_members: bool
    can_view_all_data: bool
    can_modify_family_settings: bool
    can_delete_family: bool


class FamilyPermissionResponse(SuccessResponse[FamilyPermissionInfo]):
    """Family permission check response"""

    pass


class FamilyActivityLog(BaseModel):
    """Family activity log entry"""

    log_id: str
    family_id: str
    user_id: str
    username: str
    action: str  # e.g., "member_invited", "member_joined", "role_changed"
    details: Dict[str, Any]
    timestamp: datetime


class FamilyActivityLogResponse(SuccessResponse[List[FamilyActivityLog]]):
    """Family activity log response"""

    pass


class FamilySettingsRequest(BaseModel):
    """Request to update family settings"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Family name"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Family description"
    )
    privacy_settings: Optional[Dict[str, Any]] = Field(
        None, description="Privacy settings for the family"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate family name"""
        if v is not None and not v.strip():
            raise ValueError("Family name cannot be empty or whitespace only")
        return v.strip() if v else v


class FamilySettings(BaseModel):
    """Family settings information"""

    family_id: str
    name: str
    description: Optional[str] = None
    privacy_settings: Dict[str, Any]
    member_permissions: Dict[str, List[str]]
    data_sharing_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class FamilySettingsResponse(SuccessResponse[FamilySettings]):
    """Family settings response"""

    pass


# ============================================================================
# MEMBER SWITCHING & DATA ISOLATION MODELS
# ============================================================================


class SwitchMemberRequest(BaseModel):
    """Request to switch active family member"""

    family_id: str = Field(..., description="Family ID")
    member_id: str = Field(..., description="Member ID to switch to")

    @field_validator("family_id")
    @classmethod
    def validate_family_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Family ID cannot be empty")
        return v.strip()

    @field_validator("member_id")
    @classmethod
    def validate_member_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Member ID cannot be empty")
        return v.strip()


class ActiveMemberInfo(BaseModel):
    """Active member information"""

    member_id: str
    user_id: str
    family_id: str
    username: str
    display_name: Optional[str] = None
    role: FamilyRole
    permissions: List[str]
    data_access_level: str  # 'full', 'limited', 'basic'
    switched_at: datetime


class SwitchMemberResponse(SuccessResponse[ActiveMemberInfo]):
    """Response for member switching"""

    pass


class EnhancedHealthChatRequest(BaseModel):
    """Enhanced health chat request with member context"""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    member_id: Optional[str] = Field(
        None, description="Active family member ID for data isolation"
    )
    context: Optional[Dict[str, Any]] = None

    @field_validator("member_id")
    @classmethod
    def validate_member_id(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Member ID cannot be empty if provided")
        return v.strip() if v else None


class DataAccessLevel(str, Enum):
    """Data access level enumeration"""

    FULL = "full"  # Full access to all data
    LIMITED = "limited"  # Limited access with some restrictions
    BASIC = "basic"  # Basic access with heavy restrictions


class DataSanitizationRule(BaseModel):
    """Data sanitization rule"""

    field_name: str
    access_level: DataAccessLevel
    sanitization_type: str  # 'mask', 'remove', 'aggregate', 'anonymize'
    replacement_value: Optional[str] = None


class MemberDataContext(BaseModel):
    """Member data context for isolation"""

    user_id: str
    member_id: Optional[str] = None
    family_id: Optional[str] = None
    requester_role: Optional[FamilyRole] = None
    data_access_level: DataAccessLevel = DataAccessLevel.BASIC
    allowed_fields: List[str] = Field(default_factory=list)
    sanitization_rules: List[DataSanitizationRule] = Field(default_factory=list)

    @property
    def isolation_key(self) -> str:
        """Generate isolation key for data separation"""
        if self.member_id:
            return f"{self.user_id}:{self.member_id}"
        return self.user_id

    @property
    def is_family_context(self) -> bool:
        """Check if this is a family context"""
        return self.family_id is not None and self.member_id is not None


class ConversationHistoryKey(BaseModel):
    """Conversation history composite key"""

    user_id: str
    member_id: Optional[str] = None
    session_id: Optional[str] = None

    @property
    def composite_key(self) -> str:
        """Generate composite key for conversation isolation"""
        if self.member_id:
            base_key = f"{self.user_id}:{self.member_id}"
        else:
            base_key = self.user_id

        if self.session_id:
            return f"{base_key}:{self.session_id}"
        return base_key


class DataPrivacySettings(BaseModel):
    """Data privacy settings for family members"""

    family_id: str
    member_id: str
    share_health_data: bool = False
    share_activity_data: bool = False
    share_conversation_history: bool = False
    share_goals: bool = False
    share_achievements: bool = False
    data_retention_days: int = Field(default=90, ge=1, le=365)
    anonymize_sensitive_data: bool = True


class FamilyDataAccessRequest(BaseModel):
    """Request for accessing family member data"""

    family_id: str
    target_member_id: str
    requested_data_types: List[str] = Field(..., min_length=1)
    access_reason: Optional[str] = None

    @field_validator("requested_data_types")
    @classmethod
    def validate_data_types(cls, v):
        valid_types = [
            "health_profile",
            "activity_data",
            "conversation_history",
            "goals",
            "achievements",
            "sleep_data",
            "nutrition_data",
        ]
        for data_type in v:
            if data_type not in valid_types:
                raise ValueError(
                    f"Invalid data type: {data_type}. Valid types: {valid_types}"
                )
        return v


class SanitizedUserData(BaseModel):
    """Sanitized user data based on access level"""

    user_id: str
    member_id: Optional[str] = None
    display_name: Optional[str] = None
    basic_health_info: Optional[Dict[str, Any]] = None
    activity_summary: Optional[Dict[str, Any]] = None
    goals_summary: Optional[Dict[str, Any]] = None
    data_access_level: DataAccessLevel
    sanitized_fields: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


class FamilyDataAccessResponse(SuccessResponse[SanitizedUserData]):
    """Response for family data access"""

    pass


# ============================================================================
# PHASE III: FAMILY DASHBOARD & REPORTING MODELS
# ============================================================================


class HealthReportRequest(BaseModel):
    """Request to generate family health report"""

    members: List[str] = Field(
        ..., min_length=1, description="List of family member IDs"
    )
    start_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date in YYYY-MM-DD format",
    )
    end_date: str = Field(
        ..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="End date in YYYY-MM-DD format"
    )

    @field_validator("members")
    @classmethod
    def validate_members(cls, v):
        if len(v) > 10:  # Limit to 10 members for performance
            raise ValueError("Maximum 10 members allowed per report")
        return v


class TrendData(BaseModel):
    """Trend analysis data"""

    trend_direction: str = Field(
        ..., description="Trend direction: increasing, decreasing, stable"
    )
    change_percent: float = Field(..., description="Percentage change")
    trend_description: str = Field(..., description="Human-readable trend description")


class HealthMetricSummary(BaseModel):
    """Health metric summary"""

    current_value: float
    previous_value: Optional[float] = None
    trend: TrendData
    unit: str
    rank_in_family: Optional[int] = None


class MemberHealthData(BaseModel):
    """Individual member health data in report"""

    member_id: str
    activity_metrics: Dict[str, HealthMetricSummary]
    sleep_metrics: Dict[str, HealthMetricSummary]
    weight_metrics: Dict[str, HealthMetricSummary]
    nutrition_metrics: Dict[str, HealthMetricSummary]
    heart_rate_metrics: Dict[str, HealthMetricSummary]


class HealthAlert(BaseModel):
    """Health alert information"""

    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity: low, medium, high")
    member_id: str = Field(..., description="Member ID")
    message: str = Field(..., description="Alert message")
    recommendation: str = Field(..., description="Recommended action")


class HealthReportData(BaseModel):
    """Health report data structure"""

    report_id: str
    generation_time: str
    period: Dict[str, Any]
    members: List[str]
    member_count: int
    summary: Dict[str, Any]
    trends: Dict[str, Any]
    alerts: List[HealthAlert]
    aggregated_data: Dict[str, Any]
    metadata: Dict[str, Any]


class HealthReportResponse(SuccessResponse[HealthReportData]):
    """Health report response"""

    pass


class LeaderboardRequest(BaseModel):
    """Request for family leaderboard"""

    metric: str = Field(
        ...,
        pattern="^(steps|calories|sleep_quality|weight_loss)$",
        description="Leaderboard metric",
    )
    period: str = Field(
        ..., pattern="^(daily|weekly|monthly)$", description="Time period"
    )


class LeaderboardEntry(BaseModel):
    """Leaderboard entry for a family member"""

    rank: int
    user_id: str
    name: str
    avatar: Optional[str] = None
    value: float
    percentage: float
    change_from_last_period: float
    streak_days: int
    badges: List[str] = Field(default_factory=list)


class LeaderboardStats(BaseModel):
    """Leaderboard statistics"""

    average_value: float
    highest_value: float
    lowest_value: float
    total_participants: int
    period_start: str
    period_end: str


class LeaderboardData(BaseModel):
    """Leaderboard data structure"""

    leaderboard_id: str
    metric: str
    period: str
    family_id: Optional[str] = None
    generated_at: str
    rankings: List[LeaderboardEntry]
    statistics: LeaderboardStats
    metadata: Dict[str, Any]


class LeaderboardResponse(SuccessResponse[LeaderboardData]):
    """Leaderboard response"""

    pass


class ChallengeParticipant(BaseModel):
    """Challenge participant information"""

    user_id: str
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    completed: bool = False


class ChallengeProgress(BaseModel):
    """Challenge progress information"""

    completion_percentage: float
    participants_completed: int
    total_participants: int
    current_leader: Optional[str] = None
    days_remaining: Optional[int] = None


class FamilyChallenge(BaseModel):
    """Family challenge information"""

    challenge_id: str
    title: str
    description: str
    challenge_type: str = Field(
        ..., description="Challenge type: activity, nutrition, sleep, etc."
    )
    target_metric: str
    target_value: float
    start_date: str
    end_date: str
    progress: ChallengeProgress
    participants: List[ChallengeParticipant]
    status: str = Field(default="active", description="Challenge status")


class CompletedChallenge(BaseModel):
    """Completed challenge information"""

    challenge_id: str
    title: str
    description: str
    challenge_type: str
    target_metric: str
    target_value: float
    completed_date: str
    results: Dict[str, Any]


class UpcomingChallenge(BaseModel):
    """Upcoming challenge information"""

    challenge_id: str
    title: str
    description: str
    challenge_type: str
    target_metric: str
    target_value: float
    start_date: str
    end_date: str
    participants_registered: int


class ChallengeSummary(BaseModel):
    """Challenge summary statistics"""

    total_active: int
    total_completed: int
    total_upcoming: int
    family_points: int
    family_rank: int


class FamilyChallengesData(BaseModel):
    """Family challenges data structure"""

    family_id: str
    retrieved_at: str
    active_challenges: List[FamilyChallenge]
    completed_challenges: List[CompletedChallenge]
    upcoming_challenges: List[UpcomingChallenge]
    challenge_summary: ChallengeSummary


class FamilyChallengesResponse(SuccessResponse[FamilyChallengesData]):
    """Family challenges response"""

    pass


class CreateChallengeRequest(BaseModel):
    """Request to create a new family challenge"""

    title: str = Field(..., min_length=1, max_length=100, description="Challenge title")
    description: str = Field(
        ..., min_length=1, max_length=500, description="Challenge description"
    )
    challenge_type: str = Field(
        ...,
        pattern="^(activity|nutrition|sleep|weight_management)$",
        description="Challenge type",
    )
    target_metric: str = Field(..., description="Target metric to track")
    target_value: float = Field(..., gt=0, description="Target value to achieve")
    duration_days: int = Field(
        default=7, ge=1, le=90, description="Challenge duration in days"
    )
    start_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date in YYYY-MM-DD format (defaults to today)",
    )
    participants: List[str] = Field(
        default_factory=list, description="Initial participant IDs"
    )
    rewards: List[str] = Field(default_factory=list, description="Challenge rewards")


class CreateChallengeData(BaseModel):
    """Created challenge data"""

    challenge_id: str
    family_id: str
    title: str
    description: str
    challenge_type: str
    target_metric: str
    target_value: float
    duration_days: int
    start_date: str
    end_date: str
    participants: List[str]
    rewards: List[str]
    status: str
    created_at: str
    created_by: str
    progress: Dict[str, Any]


class CreateChallengeResponse(SuccessResponse[CreateChallengeData]):
    """Create challenge response"""

    pass


# ==================== RAG Models (v1.1 特种作战装备) ====================

class RAGQueryRequest(BaseModel):
    """RAG渗透任务请求"""

    user_query: str = Field(..., min_length=1, max_length=1000, description="渗透目标（用户问题）")
    k: int = Field(default=3, ge=1, le=10, description="情报份数（返回文档数）")


class RAGQueryResponse(BaseResponse):
    """渗透任务战果报告"""

    results: List[str] = Field(default_factory=list, description="捕获的核心情报列表")
    query: str = Field(..., description="原始渗透目标")
    total_found: int = Field(default=0, description="发现的情报总数")
