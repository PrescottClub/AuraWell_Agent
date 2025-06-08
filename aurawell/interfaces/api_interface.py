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
import time

# Import models and authentication
from ..models.api_models import (
    BaseResponse, ErrorResponse, ResponseStatus,
    LoginRequest, TokenResponse,
    ChatRequest, ChatResponse,
    UserProfileRequest, UserProfileResponse,
    HealthGoalRequest, HealthGoalResponse, HealthGoalsListResponse,
    HealthSummaryResponse, ActivitySummary, SleepSummary,
    AchievementsResponse, Achievement,
    HealthDataRequest, ActivityDataResponse, SleepDataResponse,
    PaginationParams
)
from ..auth import (
    get_current_user_id, get_optional_user_id,
    authenticate_user, create_user_token,
    get_security_schemes, get_security_requirements
)
from ..middleware import configure_cors

# Import core components
from ..agent import ConversationAgent, HealthToolsRegistry
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
    """Get user repository instance"""
    global _user_repo
    if _user_repo is None:
        db_manager = await get_db_manager()
        _user_repo = UserRepository(db_manager)
    return _user_repo


async def get_health_repository():
    """Get health data repository instance"""
    global _health_repo
    if _health_repo is None:
        db_manager = await get_db_manager()
        _health_repo = HealthDataRepository(db_manager)
    return _health_repo


async def get_achievement_repository():
    """Get achievement repository instance"""
    global _achievement_repo
    if _achievement_repo is None:
        db_manager = await get_db_manager()
        _achievement_repo = AchievementRepository(db_manager)
    return _achievement_repo


async def get_tools_registry():
    """Get health tools registry instance"""
    global _tools_registry
    if _tools_registry is None:
        _tools_registry = HealthToolsRegistry()
    return _tools_registry


# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header to all requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log slow requests (> 500ms as per requirement)
    if process_time > 0.5:
        logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.3f}s")

    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    error_response = ErrorResponse(
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}",
        details={"path": str(request.url.path)}
    )
    # Convert to dict and handle datetime serialization
    content = error_response.model_dump()
    content["timestamp"] = content["timestamp"].isoformat()

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    error_response = ErrorResponse(
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        details={"path": str(request.url.path)}
    )
    # Convert to dict and handle datetime serialization
    content = error_response.model_dump()
    content["timestamp"] = content["timestamp"].isoformat()

    return JSONResponse(
        status_code=500,
        content=content
    )


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
        HTTPException: If authentication fails
    """
    user_id = authenticate_user(login_request.username, login_request.password)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = create_user_token(user_id)

    return TokenResponse(
        message="Login successful",
        **token_data
    )


# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    chat_request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    tools_registry: HealthToolsRegistry = Depends(get_tools_registry)
):
    """
    Process chat message and return AI response

    Args:
        chat_request: Chat message and context
        current_user_id: Authenticated user ID
        tools_registry: Health tools registry

    Returns:
        AI response with conversation metadata

    Raises:
        HTTPException: If chat processing fails
    """
    try:
        # Validate user access
        if chat_request.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot chat for another user"
            )

        # Create conversation agent
        agent = ConversationAgent(
            user_id=current_user_id,
            demo_mode=False  # Use real AI in production
        )

        # Process message
        ai_response = await agent.a_run(chat_request.message)

        return ChatResponse(
            message="Chat processed successfully",
            reply=ai_response,
            user_id=current_user_id,
            conversation_id=f"conv_{current_user_id}_{int(datetime.now().timestamp())}",
            tools_used=[]  # TODO: Extract from agent
        )

    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed"
        )


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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        return UserProfileResponse(
            message="User profile retrieved successfully",
            user_id=user_profile.user_id,
            display_name=user_profile.display_name,
            email=user_profile.email,
            age=user_profile.age,
            gender=user_profile.gender,
            height_cm=user_profile.height_cm,
            weight_kg=user_profile.weight_kg,
            activity_level=user_profile.activity_level,
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
        existing_profile = await user_repo.get_user_profile(current_user_id)

        if not existing_profile:
            # Create new profile if doesn't exist
            from ..models.user_profile import UserProfile

            new_profile = UserProfile(
                user_id=current_user_id,
                display_name=profile_update.display_name,
                email=profile_update.email,
                age=profile_update.age,
                gender=profile_update.gender,
                height_cm=profile_update.height_cm,
                weight_kg=profile_update.weight_kg,
                activity_level=profile_update.activity_level
            )

            updated_profile = await user_repo.create_user_profile(new_profile)
        else:
            # Update existing profile
            update_data = profile_update.model_dump(exclude_unset=True)
            updated_profile = await user_repo.update_user_profile(current_user_id, update_data)

        return UserProfileResponse(
            message="User profile updated successfully",
            user_id=updated_profile.user_id,
            display_name=updated_profile.display_name,
            email=updated_profile.email,
            age=updated_profile.age,
            gender=updated_profile.gender,
            height_cm=updated_profile.height_cm,
            weight_kg=updated_profile.weight_kg,
            activity_level=updated_profile.activity_level,
            created_at=updated_profile.created_at,
            updated_at=updated_profile.updated_at
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
        # Use achievement tool to get data
        achievement_tool = tools_registry.get_tool("check_achievements")
        achievement_data = await achievement_tool(current_user_id)

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