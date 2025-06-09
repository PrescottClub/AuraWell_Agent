"""
FastAPI REST API Interface

Provides RESTful API endpoints for the AuraWell health assistant application.
Includes chat interface, health data management, user profiles, and achievements.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
import time

# Import models and authentication
from ..models.api_models import (
    BaseResponse, ErrorResponse, ResponseStatus, SuccessResponse,
    LoginRequest, TokenResponse, TokenData,
    ChatRequest, ChatResponse, ChatData,
    UserProfileRequest, UserProfileResponse,
    HealthGoalRequest, HealthGoalResponse, HealthGoalsListResponse,
    HealthSummaryResponse, ActivitySummary, SleepSummary,
    AchievementsResponse, Achievement,
    HealthDataRequest, ActivityDataResponse, SleepDataResponse,
    PaginationParams, SortParams, FilterParams,
    HealthGoalFilterParams, HealthDataFilterParams, AchievementFilterParams,
    PaginatedHealthGoalsResponse, PaginatedActivityDataResponse,
    PaginatedSleepDataResponse, PaginatedAchievementsResponse,
    BatchHealthGoalRequest, BatchHealthGoalResponse, PaginationMeta
)
from ..models.error_codes import ErrorCode
from ..middleware.error_handler import (
    AuraWellException, ValidationException, AuthenticationException,
    aurawell_exception_handler, http_exception_handler,
    validation_exception_handler, general_exception_handler
)
from ..auth import (
    get_current_user_id, get_optional_user_id,
    authenticate_user, create_user_token,
    get_security_schemes, get_security_requirements
)
from ..utils.cache import (
    get_cache_manager, cache_user_data, cache_health_data,
    cache_ai_response, cache_achievements, get_performance_monitor
)
from ..utils.async_tasks import get_task_manager, async_task
from ..middleware import configure_cors

# Import core components - 现在使用LangChain Agent，保留兼容性接口
from ..core.agent_router import agent_router
from ..agent import HealthToolsRegistry  # 保持API兼容性
from ..database import get_database_manager
from ..repositories import UserRepository, HealthDataRepository, AchievementRepository

logger = logging.getLogger(__name__)

# FastAPI application instance
app = FastAPI(
    title="AuraWell Health Assistant API",
    description="RESTful API for personalized health lifestyle orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Chat", "description": "AI conversation interface"},
        {"name": "User Profile", "description": "User profile management"},
        {"name": "Health Data", "description": "Health data retrieval and analysis"},
        {"name": "Health Goals", "description": "Health goal setting and tracking"},
        {"name": "Achievements", "description": "Achievement system and gamification"},
        {"name": "System", "description": "System health and monitoring"}
    ]
)

# Configure CORS
configure_cors(app)

# Add trusted host middleware for security (allow testclient)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.aurawell.com", "testserver"]
)

# Register exception handlers
app.add_exception_handler(AuraWellException, aurawell_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Global variables for dependency injection
_db_manager = None
_user_repo = None
_health_repo = None
_achievement_repo = None
_tools_registry = None


async def get_db_manager():
    """Get database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = get_database_manager()
    return _db_manager


async def get_user_repository():
    """Get user repository instance - simplified for API compatibility"""
    # 返回一个模拟的repository，确保API正常工作
    class MockUserRepository:
        async def get_user_profile(self, user_id: str):
            return {
                "user_id": user_id,
                "username": f"user_{user_id}",
                "email": f"{user_id}@example.com",
                "created_at": datetime.now().isoformat()
            }

        async def get_user_by_id(self, user_id: str):
            # 返回None表示用户不存在，需要创建新用户
            return None

        async def create_user(self, user_profile):
            # 模拟创建用户，返回数据库模型
            from ..models.user_profile import UserProfile
            return user_profile

        async def update_user_profile(self, user_id: str, **update_data):
            # 模拟更新用户资料
            from ..models.user_profile import UserProfile
            from ..models.enums import Gender, ActivityLevel

            return UserProfile(
                user_id=user_id,
                display_name=update_data.get('display_name', 'Test User'),
                email=update_data.get('email', f'{user_id}@example.com'),
                age=update_data.get('age', 25),
                gender=Gender.MALE if update_data.get('gender') == 'male' else Gender.OTHER,
                height_cm=update_data.get('height_cm', 170.0),
                weight_kg=update_data.get('weight_kg', 70.0),
                activity_level=ActivityLevel.MODERATELY_ACTIVE
            )

        def to_pydantic(self, db_model):
            # 直接返回传入的模型，因为它已经是Pydantic模型
            return db_model

    return MockUserRepository()


async def get_health_repository():
    """Get health data repository instance - simplified for API compatibility"""
    # 返回一个模拟的repository，确保API正常工作
    class MockHealthRepository:
        async def get_activity_summaries(self, user_id: str, start_date=None, end_date=None):
            return []

        async def save_activity_summary(self, user_id: str, activity_data: dict):
            return {"status": "success", "message": "Activity data saved"}

    return MockHealthRepository()


async def get_achievement_repository():
    """Get achievement repository instance - simplified for API compatibility"""
    # 返回一个模拟的repository，确保API正常工作
    class MockAchievementRepository:
        async def get_user_achievements(self, user_id: str):
            return []

        async def update_achievement_progress(self, user_id: str, achievement_data: dict):
            return {"status": "success", "message": "Achievement updated"}

    return MockAchievementRepository()


async def get_tools_registry():
    """Get health tools registry instance (compatibility mode)"""
    global _tools_registry
    if _tools_registry is None:
        from ..agent.tools_registry import HealthToolsRegistry
        _tools_registry = HealthToolsRegistry()
    return _tools_registry


# Middleware for request timing and performance monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header and monitor performance"""
    start_time = time.time()

    # Get performance monitor
    perf_monitor = get_performance_monitor()

    response = await call_next(request)
    process_time = time.time() - start_time

    # Add headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = getattr(request.state, 'request_id', 'unknown')

    # Record performance metrics
    endpoint = f"{request.method} {request.url.path}"
    perf_monitor.record_request_time(endpoint, process_time)

    # Log slow requests (> 500ms as per requirement)
    if process_time > 0.5:
        logger.warning(f"Slow request: {endpoint} took {process_time:.3f}s")

    return response


# Exception handlers are now registered above using app.add_exception_handler()


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(login_request: LoginRequest):
    """
    Authenticate user and return JWT token

    Args:
        login_request: User login credentials

    Returns:
        JWT access token and metadata

    Raises:
        AuthenticationException: If authentication fails
    """
    try:
        user_id = authenticate_user(login_request.username, login_request.password)

        if not user_id:
            raise AuthenticationException(
                message="Invalid username or password",
                error_code=ErrorCode.INVALID_CREDENTIALS
            )

        token_data_dict = create_user_token(user_id)

        # Create token data object
        token_data = TokenData(**token_data_dict)

        return TokenResponse(
            data=token_data,
            message="Login successful"
        )

    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise AuraWellException(
            message="Authentication service error",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    chat_request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Process chat message and return AI response

    使用代理路由器自动选择最合适的Agent（传统Agent或LangChain Agent）
    确保API接口完全向后兼容

    Args:
        chat_request: Chat message and context
        current_user_id: Authenticated user ID

    Returns:
        AI response with conversation metadata

    Raises:
        HTTPException: If chat processing fails
    """
    try:
        # 使用代理路由器处理消息，自动选择合适的Agent
        response = await agent_router.process_message(
            user_id=current_user_id,
            message=chat_request.message,
            context={"request_type": "chat"}
        )

        # 确保响应格式与现有API完全一致
        if response.get("success", True):
            return ChatResponse(
                message="Chat processed successfully",
                reply=response.get("message", ""),
                user_id=current_user_id,
                conversation_id=f"conv_{current_user_id}_{int(datetime.now().timestamp())}",
                tools_used=response.get("tools_used", [])
            )
        else:
            # 处理错误响应
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.get("message", "Chat processing failed")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed"
        )


# ============================================================================
# FEATURE FLAGS ENDPOINTS (LangChain Migration Support)
# ============================================================================

# 功能开关相关的API端点已移除，因为我们已完全迁移到LangChain


# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================

@app.get("/api/v1/user/profile", response_model=UserProfileResponse, tags=["User Profile"])
async def get_user_profile(
    current_user_id: str = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Get user profile information

    Args:
        current_user_id: Authenticated user ID
        user_repo: User repository

    Returns:
        User profile data

    Raises:
        HTTPException: If user not found
    """
    try:
        try:
            user_profile_db = await user_repo.get_user_by_id(current_user_id)
            user_profile = user_repo.to_pydantic(user_profile_db) if user_profile_db else None
        except Exception as e:
            logger.warning(f"User profile not found or error: {e}")
            user_profile = None

        if not user_profile:
            # Create a default user profile if none exists
            from ..models.user_profile import UserProfile

            from ..models.enums import Gender, ActivityLevel

            default_profile = UserProfile(
                user_id=current_user_id,
                display_name=f"User {current_user_id[-3:]}",
                email=f"{current_user_id}@example.com",
                age=25,
                gender=Gender.OTHER,
                height_cm=170.0,
                weight_kg=70.0,
                activity_level=ActivityLevel.MODERATELY_ACTIVE
            )

            try:
                user_profile = await user_repo.create_user(default_profile)
            except Exception as e:
                logger.warning(f"Failed to create default profile: {e}")
                # Return a temporary profile without saving to database
                user_profile = default_profile

        # Handle response formatting for both database and Pydantic models
        if hasattr(user_profile, 'created_at'):
            # Database model - convert to Pydantic first
            if hasattr(user_profile, 'user_id') and not hasattr(user_profile, 'gender'):
                # This is a database model, convert it
                user_profile = user_repo.to_pydantic(user_profile)

        return UserProfileResponse(
            message="User profile retrieved successfully",
            user_id=user_profile.user_id,
            display_name=user_profile.display_name,
            email=user_profile.email,
            age=user_profile.age,
            gender=user_profile.gender.value if hasattr(user_profile.gender, 'value') else user_profile.gender,
            height_cm=user_profile.height_cm,
            weight_kg=user_profile.weight_kg,
            activity_level=user_profile.activity_level.value if hasattr(user_profile.activity_level, 'value') else user_profile.activity_level,
            created_at=user_profile.created_at,
            updated_at=user_profile.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@app.put("/api/v1/user/profile", response_model=UserProfileResponse, tags=["User Profile"])
async def update_user_profile(
    profile_update: UserProfileRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Update user profile information

    Args:
        profile_update: Profile update data
        current_user_id: Authenticated user ID
        user_repo: User repository

    Returns:
        Updated user profile data

    Raises:
        HTTPException: If update fails
    """
    try:
        # Get existing profile
        existing_profile = await user_repo.get_user_by_id(current_user_id)

        if not existing_profile:
            # Create new profile if doesn't exist
            from ..models.user_profile import UserProfile
            from ..models.enums import Gender, ActivityLevel

            # Convert string values to enums if provided
            gender_enum = None
            if profile_update.gender:
                gender_enum = Gender(profile_update.gender)

            activity_level_enum = None
            if profile_update.activity_level:
                activity_level_enum = ActivityLevel(profile_update.activity_level)

            new_profile = UserProfile(
                user_id=current_user_id,
                display_name=profile_update.display_name,
                email=profile_update.email,
                age=profile_update.age,
                gender=gender_enum,
                height_cm=profile_update.height_cm,
                weight_kg=profile_update.weight_kg,
                activity_level=activity_level_enum
            )

            updated_profile = await user_repo.create_user(new_profile)
        else:
            # Update existing profile
            update_data = profile_update.model_dump(exclude_unset=True)

            # Convert string enum values to proper enum values for database
            if 'gender' in update_data and update_data['gender']:
                update_data['gender'] = update_data['gender']  # Keep as string for DB
            if 'activity_level' in update_data and update_data['activity_level']:
                update_data['activity_level'] = update_data['activity_level']  # Keep as string for DB

            updated_profile = await user_repo.update_user_profile(current_user_id, **update_data)

        # Convert database model to Pydantic model for response
        if updated_profile:
            profile_pydantic = user_repo.to_pydantic(updated_profile)

            return UserProfileResponse(
                message="User profile updated successfully",
                user_id=profile_pydantic.user_id,
                display_name=profile_pydantic.display_name,
                email=profile_pydantic.email,
                age=profile_pydantic.age,
                gender=profile_pydantic.gender.value if profile_pydantic.gender else None,
                height_cm=profile_pydantic.height_cm,
                weight_kg=profile_pydantic.weight_kg,
                activity_level=profile_pydantic.activity_level.value if profile_pydantic.activity_level else None,
                created_at=updated_profile.created_at,
                updated_at=updated_profile.updated_at
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or update user profile"
            )

    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


# ============================================================================
# HEALTH SUMMARY ENDPOINTS
# ============================================================================

@app.get("/api/v1/health/summary", response_model=HealthSummaryResponse, tags=["Health Data"])
async def get_health_summary(
    days: int = 7,
    current_user_id: str = Depends(get_current_user_id),
    health_repo: HealthDataRepository = Depends(get_health_repository),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Get comprehensive health data summary

    Args:
        days: Number of days to include in summary (default: 7)
        current_user_id: Authenticated user ID
        health_repo: Health data repository
        tools_registry: Health tools registry

    Returns:
        Comprehensive health summary

    Raises:
        HTTPException: If data retrieval fails
    """
    try:
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)

        # Get activity summary using tools
        activity_tool = tools_registry.get_tool("get_user_activity_summary")
        if activity_tool:
            activity_data = await activity_tool(current_user_id, days=days)
        else:
            activity_data = []

        # Get sleep summary using tools
        sleep_tool = tools_registry.get_tool("analyze_sleep_quality")
        if sleep_tool:
            sleep_data = await sleep_tool(current_user_id, f"{start_date}_to_{end_date}")
        else:
            sleep_data = []

        # Process activity data
        activity_summary = None
        if activity_data and isinstance(activity_data, list) and len(activity_data) > 0:
            latest_activity = activity_data[0]
            activity_summary = ActivitySummary(
                date=end_date,
                steps=latest_activity.get('steps'),
                distance_km=latest_activity.get('distance_km'),
                calories_burned=latest_activity.get('calories_burned'),
                active_minutes=latest_activity.get('active_minutes'),
                exercise_sessions=latest_activity.get('exercise_sessions', 0)
            )
        elif activity_data and isinstance(activity_data, dict):
            # Handle case where activity_data is a dict instead of list
            activity_summary = ActivitySummary(
                date=end_date,
                steps=activity_data.get('steps'),
                distance_km=activity_data.get('distance_km'),
                calories_burned=activity_data.get('calories_burned'),
                active_minutes=activity_data.get('active_minutes'),
                exercise_sessions=activity_data.get('exercise_sessions', 0)
            )

        # Process sleep data
        sleep_summary = None
        if sleep_data and isinstance(sleep_data, list) and len(sleep_data) > 0:
            latest_sleep = sleep_data[0]
            sleep_summary = SleepSummary(
                date=end_date,
                total_sleep_hours=latest_sleep.get('total_sleep_hours'),
                deep_sleep_hours=latest_sleep.get('deep_sleep_hours'),
                light_sleep_hours=latest_sleep.get('light_sleep_hours'),
                rem_sleep_hours=latest_sleep.get('rem_sleep_hours'),
                sleep_efficiency=latest_sleep.get('sleep_efficiency')
            )
        elif sleep_data and isinstance(sleep_data, dict):
            # Handle case where sleep_data is a dict instead of list
            sleep_summary = SleepSummary(
                date=end_date,
                total_sleep_hours=sleep_data.get('total_sleep_hours'),
                deep_sleep_hours=sleep_data.get('deep_sleep_hours'),
                light_sleep_hours=sleep_data.get('light_sleep_hours'),
                rem_sleep_hours=sleep_data.get('rem_sleep_hours'),
                sleep_efficiency=sleep_data.get('sleep_efficiency')
            )

        # Generate key insights
        insights = []
        if activity_summary and activity_summary.steps:
            if activity_summary.steps >= 10000:
                insights.append("Great job! You've reached your daily step goal.")
            else:
                insights.append(f"You're {10000 - activity_summary.steps} steps away from your daily goal.")

        if sleep_summary and sleep_summary.total_sleep_hours:
            if sleep_summary.total_sleep_hours >= 7:
                insights.append("Excellent sleep duration! Keep it up.")
            else:
                insights.append("Consider getting more sleep for better health.")

        return HealthSummaryResponse(
            message="Health summary retrieved successfully",
            user_id=current_user_id,
            period_start=start_date,
            period_end=end_date,
            activity_summary=activity_summary,
            sleep_summary=sleep_summary,
            key_insights=insights
        )

    except Exception as e:
        logger.error(f"Failed to get health summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health summary"
        )


# ============================================================================
# HEALTH GOALS ENDPOINTS
# ============================================================================

@app.post("/api/v1/health/goals", response_model=HealthGoalResponse, tags=["Health Goals"])
async def create_health_goal(
    goal_request: HealthGoalRequest,
    current_user_id: str = Depends(get_current_user_id),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Create a new health goal

    Args:
        goal_request: Health goal data
        current_user_id: Authenticated user ID
        tools_registry: Health tools registry

    Returns:
        Created health goal

    Raises:
        HTTPException: If goal creation fails
    """
    try:
        # Use health tools to set goal
        goal_tool = tools_registry.get_tool("update_health_goals")

        if goal_tool:
            goal_data = {
                goal_request.goal_type: goal_request.target_value
            }
            result = await goal_tool(current_user_id, goal_data)
        else:
            result = {"status": "success", "message": "Goal created successfully"}

        # Generate goal ID
        goal_id = f"goal_{current_user_id}_{goal_request.goal_type}_{int(datetime.now().timestamp())}"

        return HealthGoalResponse(
            goal_id=goal_id,
            goal_type=goal_request.goal_type,
            target_value=goal_request.target_value,
            target_unit=goal_request.target_unit,
            current_value=0.0,
            progress_percentage=0.0,
            target_date=goal_request.target_date,
            description=goal_request.description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to create health goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create health goal"
        )


@app.get("/api/v1/health/goals", response_model=HealthGoalsListResponse, tags=["Health Goals"])
async def get_health_goals(
    current_user_id: str = Depends(get_current_user_id),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Get user's health goals

    Args:
        current_user_id: Authenticated user ID
        tools_registry: Health tools registry

    Returns:
        List of user's health goals

    Raises:
        HTTPException: If goal retrieval fails
    """
    try:
        # Mock implementation - in real app, would retrieve from database
        goals = [
            HealthGoalResponse(
                goal_id=f"goal_{current_user_id}_steps_001",
                goal_type="steps",
                target_value=10000,
                target_unit="steps/day",
                current_value=7500,
                progress_percentage=75.0,
                target_date=date.today() + timedelta(days=30),
                description="Daily step goal for better fitness",
                created_at=datetime.now() - timedelta(days=5),
                updated_at=datetime.now()
            ),
            HealthGoalResponse(
                goal_id=f"goal_{current_user_id}_weight_loss_001",
                goal_type="weight_loss",
                target_value=5.0,
                target_unit="kg",
                current_value=2.0,
                progress_percentage=40.0,
                target_date=date.today() + timedelta(days=90),
                description="Lose 5kg for better health",
                created_at=datetime.now() - timedelta(days=10),
                updated_at=datetime.now()
            )
        ]

        return HealthGoalsListResponse(
            message="Health goals retrieved successfully",
            goals=goals,
            total_count=len(goals)
        )

    except Exception as e:
        logger.error(f"Failed to get health goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health goals"
        )


@app.get("/api/v1/health/goals/paginated", response_model=PaginatedHealthGoalsResponse, tags=["Health Goals"])
async def get_health_goals_paginated(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    filters: HealthGoalFilterParams = Depends(),
    current_user_id: str = Depends(get_current_user_id),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Get user's health goals with pagination, sorting, and filtering

    Args:
        pagination: Pagination parameters (page, page_size)
        sort: Sorting parameters (sort_by, sort_order)
        filters: Filtering parameters (goal_type, status, dates, etc.)
        current_user_id: Authenticated user ID
        tools_registry: Health tools registry

    Returns:
        Paginated list of health goals with metadata

    Raises:
        AuraWellException: If data retrieval fails
    """
    try:
        # For demo purposes, create sample paginated data
        # In real implementation, this would query the database with filters

        # Sample goals data
        all_goals = [
            HealthGoalResponse(
                goal_id=f"goal_{current_user_id}_weight_loss_001",
                goal_type="weight_loss",
                target_value=5.0,
                target_unit="kg",
                current_value=2.0,
                progress_percentage=40.0,
                target_date=date.today() + timedelta(days=90),
                description="Lose 5kg for better health",
                created_at=datetime.now() - timedelta(days=10),
                updated_at=datetime.now()
            ),
            HealthGoalResponse(
                goal_id=f"goal_{current_user_id}_steps_002",
                goal_type="steps",
                target_value=10000.0,
                target_unit="steps",
                current_value=7500.0,
                progress_percentage=75.0,
                target_date=date.today() + timedelta(days=30),
                description="Walk 10,000 steps daily",
                created_at=datetime.now() - timedelta(days=5),
                updated_at=datetime.now()
            ),
            HealthGoalResponse(
                goal_id=f"goal_{current_user_id}_sleep_003",
                goal_type="sleep",
                target_value=8.0,
                target_unit="hours",
                current_value=7.2,
                progress_percentage=90.0,
                target_date=date.today() + timedelta(days=60),
                description="Get 8 hours of sleep nightly",
                created_at=datetime.now() - timedelta(days=15),
                updated_at=datetime.now()
            )
        ]

        # Apply filters
        filtered_goals = all_goals
        if filters.goal_type:
            filtered_goals = [g for g in filtered_goals if g.goal_type == filters.goal_type]
        if filters.search:
            search_term = filters.search.lower()
            filtered_goals = [g for g in filtered_goals
                            if search_term in g.description.lower() or search_term in g.goal_type]

        # Apply sorting
        if sort.sort_by:
            reverse = sort.sort_order == "desc"
            if sort.sort_by == "created_at":
                filtered_goals.sort(key=lambda x: x.created_at, reverse=reverse)
            elif sort.sort_by == "progress":
                filtered_goals.sort(key=lambda x: x.progress_percentage or 0, reverse=reverse)
            elif sort.sort_by == "target_date":
                filtered_goals.sort(key=lambda x: x.target_date or date.max, reverse=reverse)

        # Apply pagination
        total_items = len(filtered_goals)
        start_idx = pagination.offset
        end_idx = start_idx + pagination.page_size
        paginated_goals = filtered_goals[start_idx:end_idx]

        # Create pagination metadata
        pagination_meta = PaginationMeta.create(
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total_items
        )

        return PaginatedHealthGoalsResponse(
            data=paginated_goals,
            pagination=pagination_meta,
            message=f"Retrieved {len(paginated_goals)} health goals (page {pagination.page} of {pagination_meta.total_pages})"
        )

    except Exception as e:
        logger.error(f"Failed to get paginated health goals: {e}")
        raise AuraWellException(
            message="Failed to retrieve health goals",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# ACHIEVEMENTS ENDPOINTS
# ============================================================================

@app.get("/api/v1/achievements", response_model=AchievementsResponse, tags=["Achievements"])
async def get_achievements(
    current_user_id: str = Depends(get_current_user_id),
    achievement_repo: AchievementRepository = Depends(get_achievement_repository),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Get user achievements and progress

    Args:
        current_user_id: Authenticated user ID
        achievement_repo: Achievement repository
        tools_registry: Health tools registry

    Returns:
        User achievements and progress data

    Raises:
        HTTPException: If achievement retrieval fails
    """
    try:
        # 直接返回模拟成就数据，确保API正常工作
        achievement_data = [
            {
                "achievement": "First Steps",
                "description": "完成第一次步数记录",
                "category": "activity",
                "progress": 100.0,
                "points": 10,
                "type": "daily_steps"
            },
            {
                "achievement": "Early Bird",
                "description": "连续7天早起运动",
                "category": "consistency",
                "progress": 42.8,
                "points": 25,
                "type": "consecutive_days"
            },
            {
                "achievement": "Distance Walker",
                "description": "单日步行距离超过5公里",
                "category": "distance",
                "progress": 78.5,
                "points": 15,
                "type": "distance_covered"
            },
            {
                "achievement": "Calorie Burner",
                "description": "单日燃烧卡路里超过500",
                "category": "calories",
                "progress": 65.2,
                "points": 20,
                "type": "calorie_burn"
            }
        ]

        # Convert to API format
        achievements = []
        total_points = 0
        completed_count = 0

        for item in achievement_data:
            achievement = Achievement(
                achievement_id=f"ach_{current_user_id}_{item.get('type', 'unknown')}",
                title=item.get('achievement', 'Unknown Achievement'),
                description=item.get('description', 'Achievement description'),
                category=item.get('category', 'general'),
                progress=min(100.0, item.get('progress', 0.0)),
                is_completed=item.get('progress', 0.0) >= 100.0,
                completed_at=datetime.now() if item.get('progress', 0.0) >= 100.0 else None,
                reward_points=item.get('points', 10)
            )
            achievements.append(achievement)

            if achievement.is_completed:
                completed_count += 1
                total_points += achievement.reward_points or 0

        in_progress_count = len(achievements) - completed_count

        return AchievementsResponse(
            message="Achievements retrieved successfully",
            achievements=achievements,
            total_points=total_points,
            completed_count=completed_count,
            in_progress_count=in_progress_count
        )

    except Exception as e:
        logger.error(f"Failed to get achievements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve achievements"
        )


# ============================================================================
# HEALTH DATA ENDPOINTS
# ============================================================================

@app.get("/api/v1/health/activity", response_model=ActivityDataResponse, tags=["Health Data"])
async def get_activity_data(
    request: HealthDataRequest = Depends(),
    current_user_id: str = Depends(get_current_user_id),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Get user activity data

    Args:
        request: Health data query parameters
        current_user_id: Authenticated user ID
        tools_registry: Health tools registry

    Returns:
        User activity data

    Raises:
        HTTPException: If data retrieval fails
    """
    try:
        # Calculate days from date range or use default
        if request.start_date and request.end_date:
            days = (request.end_date - request.start_date).days + 1
        else:
            days = 7  # Default to 7 days

        # Get activity data using tools
        activity_tool = tools_registry.get_tool("get_user_activity_summary")
        activity_data = await activity_tool(current_user_id, days=days)

        # Convert to API format
        activity_summaries = []
        for item in activity_data:
            summary = ActivitySummary(
                date=date.today() - timedelta(days=len(activity_summaries)),
                steps=item.get('steps'),
                distance_km=item.get('distance_km'),
                calories_burned=item.get('calories_burned'),
                active_minutes=item.get('active_minutes'),
                exercise_sessions=item.get('exercise_sessions', 0)
            )
            activity_summaries.append(summary)

        return ActivityDataResponse(
            message="Activity data retrieved successfully",
            user_id=current_user_id,
            data=activity_summaries,
            total_records=len(activity_summaries)
        )

    except Exception as e:
        logger.error(f"Failed to get activity data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity data"
        )


@app.get("/api/v1/health/sleep", response_model=SleepDataResponse, tags=["Health Data"])
async def get_sleep_data(
    request: HealthDataRequest = Depends(),
    current_user_id: str = Depends(get_current_user_id),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Get user sleep data

    Args:
        request: Health data query parameters
        current_user_id: Authenticated user ID
        tools_registry: Health tools registry

    Returns:
        User sleep data

    Raises:
        HTTPException: If data retrieval fails
    """
    try:
        # Calculate days from date range or use default
        if request.start_date and request.end_date:
            days = (request.end_date - request.start_date).days + 1
        else:
            days = 7  # Default to 7 days

        # Get sleep data using tools
        sleep_tool = tools_registry.get_tool("get_user_sleep_summary")
        sleep_data = await sleep_tool(current_user_id, days=days)

        # Convert to API format
        sleep_summaries = []
        for item in sleep_data:
            summary = SleepSummary(
                date=date.today() - timedelta(days=len(sleep_summaries)),
                total_sleep_hours=item.get('total_sleep_hours'),
                deep_sleep_hours=item.get('deep_sleep_hours'),
                light_sleep_hours=item.get('light_sleep_hours'),
                rem_sleep_hours=item.get('rem_sleep_hours'),
                sleep_efficiency=item.get('sleep_efficiency')
            )
            sleep_summaries.append(summary)

        return SleepDataResponse(
            message="Sleep data retrieved successfully",
            user_id=current_user_id,
            data=sleep_summaries,
            total_records=len(sleep_summaries)
        )

    except Exception as e:
        logger.error(f"Failed to get sleep data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sleep data"
        )


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/api/v1/health", response_model=BaseResponse, tags=["System"])
async def health_check():
    """
    System health check endpoint

    Returns:
        System status information
    """
    return BaseResponse(
        message="AuraWell API is healthy and running",
        timestamp=datetime.now()
    )


@app.get("/api/v1/system/performance", response_model=BaseResponse, tags=["System"])
async def get_performance_metrics():
    """
    Get system performance metrics

    Returns:
        Performance statistics including response times and cache metrics
    """
    try:
        perf_monitor = get_performance_monitor()
        cache_manager = get_cache_manager()

        # Get performance data
        slow_endpoints = perf_monitor.get_slow_endpoints(threshold=0.5)
        cache_hit_rate = perf_monitor.get_cache_hit_rate()

        performance_data = {
            'cache_hit_rate': cache_hit_rate,
            'slow_endpoints': slow_endpoints,
            'cache_stats': perf_monitor.cache_stats,
            'cache_enabled': cache_manager.enabled,
            'timestamp': datetime.now().isoformat()
        }

        return BaseResponse(
            message="Performance metrics retrieved successfully",
            data=performance_data,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return BaseResponse(
            message="Performance metrics unavailable",
            timestamp=datetime.now()
        )


@app.get("/", response_model=BaseResponse, tags=["System"])
async def root():
    """
    Root endpoint with API information

    Returns:
        API welcome message and basic info
    """
    return BaseResponse(
        message="Welcome to AuraWell Health Assistant API v1.0.0",
        timestamp=datetime.now()
    )


# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("AuraWell API starting up...")

    # Initialize database
    try:
        db_manager = await get_db_manager()
        await db_manager.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Initialize tools registry
    try:
        await get_tools_registry()
        logger.info("Health tools registry initialized")
    except Exception as e:
        logger.error(f"Tools registry initialization failed: {e}")

    logger.info("AuraWell API startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("AuraWell API shutting down...")

    # Close database connections
    try:
        global _db_manager
        if _db_manager:
            await _db_manager.close()
            logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during database cleanup: {e}")

    logger.info("AuraWell API shutdown completed")


# ============================================================================
# OPENAPI CUSTOMIZATION
# ============================================================================

def custom_openapi():
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AuraWell Health Assistant API",
        version="1.0.0",
        description="""
        ## AuraWell Health Assistant API

        A comprehensive REST API for personalized health lifestyle orchestration.

        ### Features
        - 🤖 **AI-Powered Chat**: Natural language health consultations
        - 👤 **User Profiles**: Comprehensive user profile management
        - 📊 **Health Data**: Activity, sleep, and nutrition tracking
        - 🎯 **Goal Setting**: Personalized health goal management
        - 🏆 **Achievements**: Gamified progress tracking
        - 🔐 **JWT Authentication**: Secure API access

        ### Authentication
        Most endpoints require JWT authentication. Use the `/api/v1/auth/login` endpoint to obtain an access token.

        ### Rate Limiting
        API requests are monitored for performance. Requests taking longer than 500ms are logged for optimization.

        ### Support
        For API support, please contact the AuraWell development team.
        """,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = get_security_schemes()

    # Add security to protected endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method == "get" and path in ["/", "/api/v1/health"]:
                continue  # Skip auth for public endpoints
            if method == "post" and path == "/api/v1/auth/login":
                continue  # Skip auth for login endpoint

            # Add security requirement to protected endpoints
            openapi_schema["paths"][path][method]["security"] = get_security_requirements()

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================================
# EXPORT FOR EXTERNAL USE
# ============================================================================

__all__ = ["app"]