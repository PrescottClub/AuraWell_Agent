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
    LoginRequest, RegisterRequest, TokenResponse, TokenData,
    ChatRequest, ChatResponse, ChatData,
    HealthChatRequest, HealthChatResponse, ConversationCreateRequest, ConversationResponse,
    ConversationListResponse, ChatHistoryRequest, ChatHistoryResponse, HealthSuggestionsResponse,
    UserProfileRequest, UserProfileResponse,
    HealthGoalRequest, HealthGoalResponse, HealthGoalsListResponse,
    HealthSummaryResponse, ActivitySummary, SleepSummary,
    AchievementsResponse, Achievement,
    HealthDataRequest, ActivityDataResponse, SleepDataResponse,
    PaginationParams, SortParams, FilterParams,
    HealthGoalFilterParams, HealthDataFilterParams, AchievementFilterParams,
    PaginatedHealthGoalsResponse, PaginatedActivityDataResponse,
    PaginatedSleepDataResponse, PaginatedAchievementsResponse,
    BatchHealthGoalRequest, BatchHealthGoalResponse, PaginationMeta,
    HealthPlanRequest, HealthPlanResponse, HealthPlansListResponse,
    HealthPlanGenerateRequest, HealthPlanGenerateResponse, HealthPlan, HealthPlanModule,
    UserHealthDataRequest, UserHealthDataResponse,
    UserHealthGoalRequest, UserHealthGoalResponse, UserHealthGoalsListResponse,
    HealthAdviceRequest, HealthAdviceResponse as APIHealthAdviceResponse,
    # Family Management Models
    FamilyCreateRequest, FamilyInfoResponse, FamilyListResponse,
    InviteMemberRequest, InviteMemberResponse, AcceptInviteRequest, DeclineInviteRequest,
    FamilyMembersResponse, UpdateMemberRoleRequest, RemoveMemberRequest,
    TransferOwnershipRequest, LeaveFamilyRequest, DeleteFamilyRequest,
    FamilyPermissionResponse, FamilyActivityLogResponse, FamilySettingsRequest,
    FamilySettingsResponse, PendingInviteResponse
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
from ..services.chat_service import ChatService
from ..services.family_service import FamilyService

# Import LangChain Agent components
from ..langchain_agent.services.health_advice_service import HealthAdviceService
from ..langchain_agent.tools.health_advice_tool import HealthAdviceTool

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
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

    yield

    # Shutdown
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


# FastAPI application instance
app = FastAPI(
    title="AuraWell Health Assistant API",
    description="RESTful API for personalized health lifestyle orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Authentication", "description": "User authentication and authorization"},
        {"name": "Chat", "description": "AI conversation interface"},
        {"name": "User Profile", "description": "User profile management"},
        {"name": "Health Data", "description": "Health data retrieval and analysis"},
        {"name": "Health Goals", "description": "Health goal setting and tracking"},
        {"name": "Achievements", "description": "Achievement system and gamification"},
        {"name": "Family Management", "description": "Family creation and member management"},
        {"name": "System", "description": "System health and monitoring"},
        {"name": "Health Advice", "description": "Health advice generation"}
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
_health_plan_repo = None
_tools_registry = None
_chat_service = None
_health_advice_service = None
_family_service = None


async def get_db_manager():
    """Get database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = get_database_manager()
    return _db_manager


async def get_user_repository():
    """Get user repository instance - with fallback to mock if database unavailable"""
    global _user_repo
    if _user_repo is None:
        try:
            # 尝试使用真实的数据库Repository
            db_manager = await get_db_manager()
            from ..repositories.user_repository import UserRepository

            # 创建一个包装器来管理session
            class UserRepositoryWrapper:
                def __init__(self, db_manager):
                    self.db_manager = db_manager

                async def get_user_profile(self, user_id: str):
                    async with self.db_manager.get_session() as session:
                        repo = UserRepository(session)
                        user = await repo.get_user_by_id(user_id)
                        return repo.to_pydantic(user) if user else None

                async def get_user_by_id(self, user_id: str):
                    async with self.db_manager.get_session() as session:
                        repo = UserRepository(session)
                        return await repo.get_user_by_id(user_id)

                async def get_user_by_username(self, username: str):
                    async with self.db_manager.get_session() as session:
                        repo = UserRepository(session)
                        return await repo.get_user_by_username(username)

                async def get_user_by_email(self, email: str):
                    async with self.db_manager.get_session() as session:
                        repo = UserRepository(session)
                        return await repo.get_user_by_email(email)

                async def create_user(self, user_profile):
                    async with self.db_manager.get_session() as session:
                        repo = UserRepository(session)
                        result = await repo.create_user(user_profile)
                        await session.commit()
                        return result

                async def update_user_profile(self, user_id: str, **update_data):
                    async with self.db_manager.get_session() as session:
                        repo = UserRepository(session)
                        result = await repo.update_user_profile(user_id, **update_data)
                        await session.commit()
                        return result

                def to_pydantic(self, db_model):
                    if db_model is None:
                        return None
                    # 如果已经是Pydantic模型，直接返回
                    if hasattr(db_model, 'model_dump'):
                        return db_model
                    # 否则转换为Pydantic模型
                    from ..repositories.user_repository import UserRepository
                    return UserRepository.to_pydantic(db_model)

            _user_repo = UserRepositoryWrapper(db_manager)
            logger.info("Successfully created real user repository")

        except Exception as e:
            logger.warning(f"Failed to create real user repository: {e}, using mock")
            # 如果数据库不可用，使用模拟Repository
            _user_repo = MockUserRepository()

    return _user_repo


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

        async def get_user_by_username(self, username: str):
            # 检查用户名是否存在
            return None

        async def get_user_by_email(self, email: str):
            # 检查邮箱是否存在
            return None

        async def create_user(self, user_profile):
            # 模拟创建用户，返回数据库模型
            from ..models.user_profile import UserProfile
            return user_profile

        async def update_user_profile(self, user_id: str, **update_data):
            # 模拟更新用户资料
            from ..models.user_profile import UserProfile
            from ..models.enums import Gender, ActivityLevel

            # 处理gender枚举
            gender_enum = Gender.OTHER  # 默认值
            if update_data.get('gender'):
                gender_str = update_data.get('gender')
                if gender_str == 'male':
                    gender_enum = Gender.MALE
                elif gender_str == 'female':
                    gender_enum = Gender.FEMALE
                else:
                    gender_enum = Gender.OTHER

            # 处理activity_level枚举
            activity_level_enum = ActivityLevel.MODERATELY_ACTIVE  # 默认值
            if update_data.get('activity_level'):
                activity_str = update_data.get('activity_level')
                try:
                    activity_level_enum = ActivityLevel(activity_str)
                except ValueError:
                    activity_level_enum = ActivityLevel.MODERATELY_ACTIVE
            elif 'activity_level' in update_data and update_data['activity_level'] is None:
                # 如果明确传入了None，使用默认值
                activity_level_enum = ActivityLevel.MODERATELY_ACTIVE

            return UserProfile(
                user_id=user_id,
                display_name=update_data.get('display_name', 'Test User'),
                email=update_data.get('email', f'{user_id}@example.com'),
                age=update_data.get('age', 25),
                gender=gender_enum,
                height_cm=update_data.get('height_cm', 170.0),
                weight_kg=update_data.get('weight_kg', 70.0),
                activity_level=activity_level_enum
            )

        def to_pydantic(self, db_model):
            # 直接返回传入的模型，因为它已经是Pydantic模型
            return db_model


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


async def get_health_plan_repository():
    """Get health plan repository instance"""
    global _health_plan_repo
    if _health_plan_repo is None:
        try:
            # 尝试使用真实的数据库Repository
            db_manager = await get_db_manager()
            from ..repositories.health_plan_repository import HealthPlanRepository

            # 创建一个包装器来管理session
            class HealthPlanRepositoryWrapper:
                def __init__(self, db_manager):
                    self.db_manager = db_manager

                async def get_user_health_plans(self, user_id: str, status=None, limit=None, offset=None):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        return await repo.get_user_health_plans(user_id, status, limit, offset)

                async def get_health_plan_by_id(self, plan_id: str, user_id: str):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        return await repo.get_health_plan_by_id(plan_id, user_id)

                async def create_health_plan(self, user_id: str, plan_data: dict):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        result = await repo.create_health_plan(user_id, plan_data)
                        await session.commit()  # 确保提交事务
                        return result

                async def create_plan_module(self, plan_id: str, module_data: dict):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        result = await repo.create_plan_module(plan_id, module_data)
                        await session.commit()  # 确保提交事务
                        return result

                async def get_plan_modules(self, plan_id: str):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        return await repo.get_plan_modules(plan_id)

                async def update_health_plan(self, plan_id: str, user_id: str, update_data: dict):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        result = await repo.update_health_plan(plan_id, update_data)
                        await session.commit()
                        return result

                async def delete_health_plan(self, plan_id: str, user_id: str):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        result = await repo.delete_health_plan(plan_id)
                        await session.commit()
                        return result

                async def get_plan_progress(self, plan_id: str, start_date=None, end_date=None, module_type=None):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        return await repo.get_plan_progress(plan_id, start_date, end_date, module_type)

                async def create_progress_record(self, plan_id: str, progress_data: dict):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        result = await repo.create_progress_record(plan_id, progress_data)
                        await session.commit()
                        return result

                async def create_feedback(self, plan_id: str, feedback_data: dict):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        result = await repo.create_feedback(plan_id, feedback_data)
                        await session.commit()
                        return result

                async def get_plan_templates(self, category=None, difficulty_level=None, is_active=True):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        return await repo.get_plan_templates(category, difficulty_level, is_active)

                async def get_template_by_id(self, template_id: str):
                    async with self.db_manager.get_session() as session:
                        repo = HealthPlanRepository(session)
                        return await repo.get_template_by_id(template_id)

            _health_plan_repo = HealthPlanRepositoryWrapper(db_manager)
            logger.info("Successfully created real health plan repository")

        except Exception as e:
            logger.warning(f"Failed to create real health plan repository: {e}, using mock")
            # 如果数据库不可用，使用模拟Repository
            _health_plan_repo = MockHealthPlanRepository()

    return _health_plan_repo


class MockHealthPlanRepository:
    async def get_user_health_plans(self, user_id: str, status=None, limit=None, offset=None):
        return []

    async def get_health_plan_by_id(self, plan_id: str, user_id: str):
        return None

    async def create_health_plan(self, user_id: str, plan_data: dict):
        # 模拟数据库对象
        class MockPlan:
            def __init__(self, data):
                self.id = f"plan_{user_id}_{int(datetime.now().timestamp())}"
                self.title = data.get('title', '')
                self.description = data.get('description', '')
                self.duration_days = data.get('duration_days', 30)
                self.status = data.get('status', 'active')
                self.progress = data.get('progress', 0.0)
                self.created_at = datetime.now()
                self.updated_at = datetime.now()
                self.user_id = user_id

        return MockPlan(plan_data)

    async def update_health_plan(self, plan_id: str, user_id: str, update_data: dict):
        return {"id": plan_id, **update_data}

    async def delete_health_plan(self, plan_id: str, user_id: str):
        return True

    async def get_plan_modules(self, plan_id: str):
        return []

    async def create_plan_module(self, plan_id: str, module_data: dict):
        # 模拟数据库对象
        class MockModule:
            def __init__(self, data):
                self.id = f"module_{plan_id}_{int(datetime.now().timestamp())}"
                self.module_type = data.get('module_type', 'general')
                self.title = data.get('title', '')
                self.description = data.get('description', '')
                self.content = data.get('content', {})
                self.duration_days = data.get('duration_days', 30)
                self.created_at = datetime.now()
                self.updated_at = datetime.now()
                self.plan_id = plan_id

        return MockModule(module_data)

    async def get_plan_progress(self, plan_id: str, start_date=None, end_date=None, module_type=None):
        return []

    async def create_progress_record(self, plan_id: str, progress_data: dict):
        return {"id": f"progress_{plan_id}_{int(datetime.now().timestamp())}", **progress_data}

    async def create_feedback(self, plan_id: str, feedback_data: dict):
        return {"id": f"feedback_{plan_id}_{int(datetime.now().timestamp())}", **feedback_data}

    async def get_plan_templates(self, category=None, difficulty_level=None, is_active=True):
        return []

    async def get_template_by_id(self, template_id: str):
        return None


async def get_tools_registry():
    """Get health tools registry instance (compatibility mode)"""
    global _tools_registry
    if _tools_registry is None:
        from ..agent.tools_registry import HealthToolsRegistry
        _tools_registry = HealthToolsRegistry()
    return _tools_registry


async def get_chat_service():
    """Get chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


async def get_health_advice_service():
    """Get health advice service instance"""
    global _health_advice_service
    if '_health_advice_service' not in globals():
        _health_advice_service = HealthAdviceService()
    return _health_advice_service


async def get_family_service() -> FamilyService:
    """Get family service instance"""
    global _family_service
    if _family_service is None:
        # Create family service with mock session
        # In production, this should use proper database session
        _family_service = FamilyService(db_session=None)
    return _family_service


@app.post("/api/v1/health/advice/comprehensive", response_model=APIHealthAdviceResponse, tags=["Health Advice"])
async def generate_comprehensive_health_advice(
    advice_request: HealthAdviceRequest,
    current_user_id: str = Depends(get_current_user_id),
    health_advice_service: HealthAdviceService = Depends(get_health_advice_service)
):
    """
    生成包含五个模块的综合健康建议
    
    生成个性化的健康建议，包括：
    - 饮食建议 (Diet)
    - 运动计划 (Exercise) 
    - 体重管理 (Weight)
    - 睡眠优化 (Sleep)
    - 心理健康 (Mental Health)
    
    基于用户画像、健康指标计算和AI知识检索生成。
    """
    try:
        logger.info(f"Generating comprehensive health advice for user: {current_user_id}")
        
        # 生成综合健康建议
        advice_response = await health_advice_service.generate_comprehensive_advice(
            user_id=current_user_id,
            goal_type=advice_request.goal_type,
            duration_weeks=advice_request.duration_weeks or 4,
            special_requirements=advice_request.special_requirements
        )
        
        # 转换为API响应格式
        api_response = APIHealthAdviceResponse(
            status=ResponseStatus.SUCCESS,
            message="健康建议生成成功",
            data={
                "advice": {
                    "diet": {
                        "title": advice_response.diet.title,
                        "content": advice_response.diet.content,
                        "recommendations": advice_response.diet.recommendations,
                        "metrics": advice_response.diet.metrics
                    },
                    "exercise": {
                        "title": advice_response.exercise.title,
                        "content": advice_response.exercise.content,
                        "recommendations": advice_response.exercise.recommendations,
                        "metrics": advice_response.exercise.metrics
                    },
                    "weight": {
                        "title": advice_response.weight.title,
                        "content": advice_response.weight.content,
                        "recommendations": advice_response.weight.recommendations,
                        "metrics": advice_response.weight.metrics
                    },
                    "sleep": {
                        "title": advice_response.sleep.title,
                        "content": advice_response.sleep.content,
                        "recommendations": advice_response.sleep.recommendations,
                        "metrics": advice_response.sleep.metrics
                    },
                    "mental_health": {
                        "title": advice_response.mental_health.title,
                        "content": advice_response.mental_health.content,
                        "recommendations": advice_response.mental_health.recommendations,
                        "metrics": advice_response.mental_health.metrics
                    }
                },
                "summary": advice_response.summary,
                "generated_at": advice_response.generated_at,
                "user_id": advice_response.user_id
            }
        )
        
        logger.info(f"Successfully generated comprehensive health advice for user: {current_user_id}")
        return api_response
        
    except Exception as e:
        logger.error(f"Error generating comprehensive health advice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成健康建议时发生错误: {str(e)}"
        )


@app.post("/api/v1/health/advice/quick", response_model=BaseResponse, tags=["Health Advice"])
async def generate_quick_health_advice(
    topic: str,
    current_user_id: str = Depends(get_current_user_id),
    health_advice_service: HealthAdviceService = Depends(get_health_advice_service)
):
    """
    生成特定主题的快速健康建议
    
    支持的主题：
    - diet: 饮食建议
    - exercise: 运动建议
    - weight: 体重管理
    - sleep: 睡眠优化
    - mental: 心理健康
    """
    try:
        logger.info(f"Generating quick health advice for topic: {topic}, user: {current_user_id}")
        
        # 验证主题
        valid_topics = ["diet", "exercise", "weight", "sleep", "mental"]
        if topic not in valid_topics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的主题。支持的主题: {', '.join(valid_topics)}"
            )
        
        # 生成快速建议
        advice_text = await health_advice_service.generate_quick_advice(
            user_id=current_user_id,
            topic=topic
        )
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"成功生成{topic}建议",
            data={
                "topic": topic,
                "advice": advice_text,
                "generated_at": datetime.now().isoformat(),
                "user_id": current_user_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quick health advice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成快速建议时发生错误: {str(e)}"
        )


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
# FAMILY MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/v1/family", response_model=FamilyInfoResponse, tags=["Family Management"])
async def create_family(
    family_request: FamilyCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Create a new family with the current user as owner
    
    Args:
        family_request: Family creation request with name and description
        current_user_id: ID of the authenticated user
        
    Returns:
        FamilyInfoResponse: Created family information
        
    Raises:
        ConflictError: If user already owns maximum families (3)
        ValidationError: If input validation fails
    """
    try:
        logger.info(f"User {current_user_id} creating family: {family_request.name}")
        
        family_info = await family_service.create_family(family_request, current_user_id)
        
        return FamilyInfoResponse(
            data=family_info,
            message="Family created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating family: {e}")
        if hasattr(e, 'error_code'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST if e.error_code == "VALIDATION_ERROR" 
                           else status.HTTP_409_CONFLICT if e.error_code == "CONFLICT" 
                           else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create family"
        )


@app.get("/api/v1/family/{family_id}", response_model=FamilyInfoResponse, tags=["Family Management"])
async def get_family_info(
    family_id: str,
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Get information about a specific family
    
    Args:
        family_id: ID of the family to retrieve
        current_user_id: ID of the authenticated user
        
    Returns:
        FamilyInfoResponse: Family information
        
    Raises:
        NotFoundError: If family not found
        AuthorizationError: If user is not a member
    """
    try:
        family_info = await family_service.get_family_info(family_id, current_user_id)
        
        return FamilyInfoResponse(
            data=family_info,
            message="Family information retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting family info: {e}")
        if hasattr(e, 'error_code'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if e.error_code == "NOT_FOUND"
                           else status.HTTP_403_FORBIDDEN if e.error_code == "AUTHORIZATION_ERROR"
                           else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get family information"
        )


@app.get("/api/v1/family", response_model=FamilyListResponse, tags=["Family Management"])
async def get_user_families(
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Get all families that the current user is a member of
    
    Args:
        current_user_id: ID of the authenticated user
        
    Returns:
        FamilyListResponse: List of families
    """
    try:
        families = await family_service.get_user_families(current_user_id)
        
        return FamilyListResponse(
            data=families,
            message=f"Retrieved {len(families)} families"
        )
        
    except Exception as e:
        logger.error(f"Error getting user families: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user families"
        )


@app.post("/api/v1/family/{family_id}/invite", response_model=InviteMemberResponse, tags=["Family Management"])
async def invite_family_member(
    family_id: str,
    invite_request: InviteMemberRequest,
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Invite a new member to the family
    
    Args:
        family_id: ID of the family
        invite_request: Invitation request with email and role
        current_user_id: ID of the authenticated user
        
    Returns:
        InviteMemberResponse: Invitation information
        
    Raises:
        AuthorizationError: If user doesn't have permission to invite
        ConflictError: If user is already a member or has pending invite
        ValidationError: If email is invalid or user not found
    """
    try:
        logger.info(f"User {current_user_id} inviting {invite_request.email} to family {family_id}")
        
        invite_info = await family_service.invite_member(family_id, invite_request, current_user_id)
        
        return InviteMemberResponse(
            data=invite_info,
            message="Invitation sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Error inviting family member: {e}")
        if hasattr(e, 'error_code'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN if e.error_code == "AUTHORIZATION_ERROR"
                           else status.HTTP_409_CONFLICT if e.error_code == "CONFLICT"
                           else status.HTTP_400_BAD_REQUEST if e.error_code == "VALIDATION_ERROR"
                           else status.HTTP_404_NOT_FOUND if e.error_code == "NOT_FOUND"
                           else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite family member"
        )


@app.post("/api/v1/family/invitation/accept", response_model=FamilyInfoResponse, tags=["Family Management"])
async def accept_family_invitation(
    accept_request: AcceptInviteRequest,
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Accept a family invitation
    
    Args:
        accept_request: Accept invitation request with invite code
        current_user_id: ID of the authenticated user
        
    Returns:
        FamilyInfoResponse: Family information after joining
        
    Raises:
        NotFoundError: If invitation not found
        ValidationError: If invitation is invalid or expired
        AuthorizationError: If user is not the intended recipient
    """
    try:
        logger.info(f"User {current_user_id} accepting family invitation")
        
        family_info = await family_service.accept_invitation(accept_request, current_user_id)
        
        return FamilyInfoResponse(
            data=family_info,
            message="Successfully joined family"
        )
        
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        if hasattr(e, 'error_code'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if e.error_code == "NOT_FOUND"
                           else status.HTTP_400_BAD_REQUEST if e.error_code == "VALIDATION_ERROR"
                           else status.HTTP_403_FORBIDDEN if e.error_code == "AUTHORIZATION_ERROR"
                           else status.HTTP_409_CONFLICT if e.error_code == "CONFLICT"
                           else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept invitation"
        )


@app.post("/api/v1/family/invitation/decline", response_model=BaseResponse, tags=["Family Management"])
async def decline_family_invitation(
    decline_request: DeclineInviteRequest,
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Decline a family invitation
    
    Args:
        decline_request: Decline invitation request with invite code and reason
        current_user_id: ID of the authenticated user
        
    Returns:
        BaseResponse: Success confirmation
        
    Raises:
        NotFoundError: If invitation not found
        ValidationError: If invitation is invalid
        AuthorizationError: If user is not the intended recipient
    """
    try:
        logger.info(f"User {current_user_id} declining family invitation")
        
        success = await family_service.decline_invitation(decline_request, current_user_id)
        
        return BaseResponse(
            success=True,
            message="Invitation declined successfully"
        )
        
    except Exception as e:
        logger.error(f"Error declining invitation: {e}")
        if hasattr(e, 'error_code'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if e.error_code == "NOT_FOUND"
                           else status.HTTP_400_BAD_REQUEST if e.error_code == "VALIDATION_ERROR"
                           else status.HTTP_403_FORBIDDEN if e.error_code == "AUTHORIZATION_ERROR"
                           else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decline invitation"
        )


@app.get("/api/v1/family/{family_id}/members", response_model=FamilyMembersResponse, tags=["Family Management"])
async def get_family_members(
    family_id: str,
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Get all members of a family
    
    Args:
        family_id: ID of the family
        current_user_id: ID of the authenticated user
        
    Returns:
        FamilyMembersResponse: List of family members
        
    Raises:
        AuthorizationError: If user is not a member of the family
    """
    try:
        members = await family_service.get_family_members(family_id, current_user_id)
        
        return FamilyMembersResponse(
            data=members,
            message=f"Retrieved {len(members)} family members"
        )
        
    except Exception as e:
        logger.error(f"Error getting family members: {e}")
        if hasattr(e, 'error_code'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN if e.error_code == "AUTHORIZATION_ERROR"
                           else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get family members"
        )


@app.get("/api/v1/family/{family_id}/permissions", response_model=FamilyPermissionResponse, tags=["Family Management"])
async def get_family_permissions(
    family_id: str,
    current_user_id: str = Depends(get_current_user_id),
    family_service: FamilyService = Depends(get_family_service)
):
    """
    Get the current user's permissions within a family
    
    Args:
        family_id: ID of the family
        current_user_id: ID of the authenticated user
        
    Returns:
        FamilyPermissionResponse: User's permissions
        
    Raises:
        NotFoundError: If user is not a member of the family
    """
    try:
        permissions = await family_service.get_user_family_permissions(family_id, current_user_id)
        
        return FamilyPermissionResponse(
            data=permissions,
            message="Permissions retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting family permissions: {e}")
        if hasattr(e, 'error_code'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if e.error_code == "NOT_FOUND"
                           else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get family permissions"
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


@app.post("/api/v1/auth/register", response_model=SuccessResponse, tags=["Authentication"])
async def register(
    register_request: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Register a new user account

    Args:
        register_request: User registration data
        user_repo: User repository instance

    Returns:
        Success response with registration confirmation

    Raises:
        ValidationException: If registration data is invalid
        AuraWellException: If registration fails
    """
    try:
        # Check if user already exists
        existing_user = await user_repo.get_user_by_username(register_request.username)
        if existing_user:
            raise ValidationException(
                message="Username already exists",
                error_code=ErrorCode.DUPLICATE_RESOURCE
            )

        # Check if email already exists
        existing_email = await user_repo.get_user_by_email(register_request.email)
        if existing_email:
            raise ValidationException(
                message="Email already registered",
                error_code=ErrorCode.DUPLICATE_RESOURCE
            )

        # Create user profile
        from ..models.user_profile import UserProfile
        from ..models.enums import Gender, ActivityLevel
        import hashlib
        import uuid

        # Hash password
        password_hash = hashlib.sha256(register_request.password.encode()).hexdigest()

        # Process health data
        health_data = register_request.health_data or {}

        # Handle gender enum
        gender_enum = Gender.OTHER
        if health_data.get('gender') == 'male':
            gender_enum = Gender.MALE
        elif health_data.get('gender') == 'female':
            gender_enum = Gender.FEMALE

        # Handle activity level enum
        activity_level_enum = ActivityLevel.MODERATELY_ACTIVE
        if health_data.get('activity_level'):
            try:
                activity_level_enum = ActivityLevel(health_data.get('activity_level'))
            except ValueError:
                activity_level_enum = ActivityLevel.MODERATELY_ACTIVE

        # Create user profile
        user_profile = UserProfile(
            user_id=str(uuid.uuid4()),
            display_name=register_request.username,
            email=register_request.email,
            password_hash=password_hash,
            age=health_data.get('age'),
            gender=gender_enum,
            height_cm=health_data.get('height'),
            weight_kg=health_data.get('weight'),
            activity_level=activity_level_enum
        )

        # Save user to repository
        created_user = await user_repo.create_user(user_profile)

        return SuccessResponse(
            message="User registered successfully",
            data={"user_id": created_user.user_id}
        )

    except (ValidationException, AuraWellException):
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise AuraWellException(
            message="Registration service error",
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
# ENHANCED HEALTH CHAT ENDPOINTS
# ============================================================================

@app.post("/api/v1/chat/conversation", response_model=ConversationResponse, tags=["Chat"])
async def create_conversation(
    conversation_request: ConversationCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Create a new health consultation conversation

    Args:
        conversation_request: Conversation creation parameters
        current_user_id: Authenticated user ID
        chat_service: Chat service instance

    Returns:
        New conversation metadata

    Raises:
        HTTPException: If conversation creation fails
    """
    try:
        return await chat_service.create_conversation(
            user_id=current_user_id,
            conversation_type=conversation_request.type,
            metadata=conversation_request.metadata
        )
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@app.get("/api/v1/chat/conversations", response_model=ConversationListResponse, tags=["Chat"])
async def get_conversations(
    current_user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get user's conversation list

    Args:
        current_user_id: Authenticated user ID
        chat_service: Chat service instance

    Returns:
        List of user conversations

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return await chat_service.get_user_conversations(current_user_id)
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@app.post("/api/v1/chat/message", response_model=HealthChatResponse, tags=["Chat"])
async def send_health_chat_message(
    chat_request: HealthChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Send a health chat message and get AI response with suggestions

    Args:
        chat_request: Health chat message and context
        current_user_id: Authenticated user ID
        chat_service: Chat service instance

    Returns:
        AI response with health suggestions and quick replies

    Raises:
        HTTPException: If message processing fails
    """
    try:
        return await chat_service.process_chat_message(
            user_id=current_user_id,
            message=chat_request.message,
            conversation_id=chat_request.conversation_id,
            context=chat_request.context
        )
    except Exception as e:
        logger.error(f"Failed to process health chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@app.get("/api/v1/chat/history", response_model=ChatHistoryResponse, tags=["Chat"])
async def get_chat_history(
    chat_history_request: ChatHistoryRequest = Depends(),
    current_user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get chat history for a conversation

    Args:
        chat_history_request: History request parameters
        current_user_id: Authenticated user ID
        chat_service: Chat service instance

    Returns:
        Chat message history with pagination

    Raises:
        HTTPException: If history retrieval fails
    """
    try:
        return await chat_service.get_chat_history(
            conversation_id=chat_history_request.conversation_id,
            user_id=current_user_id,
            limit=chat_history_request.limit,
            offset=chat_history_request.offset
        )
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@app.delete("/api/v1/chat/conversation/{conversation_id}", tags=["Chat"])
async def delete_conversation(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Delete a conversation and all its messages

    Args:
        conversation_id: ID of conversation to delete
        current_user_id: Authenticated user ID
        chat_service: Chat service instance

    Returns:
        Success confirmation

    Raises:
        HTTPException: If deletion fails
    """
    try:
        success = await chat_service.delete_conversation(conversation_id, current_user_id)
        if success:
            return {"success": True, "message": "Conversation deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@app.get("/api/v1/chat/suggestions", response_model=HealthSuggestionsResponse, tags=["Chat"])
async def get_health_suggestions(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get health suggestion templates for quick access

    Args:
        chat_service: Chat service instance

    Returns:
        List of health suggestion templates

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return await chat_service.get_health_suggestions()
    except Exception as e:
        logger.error(f"Failed to get health suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health suggestions"
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
                display_name=profile_update.display_name or f"User {current_user_id[-3:]}",
                email=profile_update.email or f"{current_user_id}@example.com",
                age=profile_update.age or 25,
                gender=gender_enum or Gender.OTHER,
                height_cm=profile_update.height_cm or 170.0,
                weight_kg=profile_update.weight_kg or 70.0,
                activity_level=activity_level_enum or ActivityLevel.MODERATELY_ACTIVE
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
# USER HEALTH DATA ENDPOINTS
# ============================================================================

@app.get("/api/v1/user/health-data", response_model=UserHealthDataResponse, tags=["User Profile"])
async def get_user_health_data(
    current_user_id: str = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Get user's health data

    Args:
        current_user_id: Authenticated user ID
        user_repo: User repository instance

    Returns:
        User health data with BMI calculations

    Raises:
        HTTPException: If data retrieval fails
    """
    try:
        # Get user profile
        user_profile = await user_repo.get_user_by_id(current_user_id)

        if not user_profile:
            # Return default health data
            return UserHealthDataResponse(
                message="Health data retrieved successfully",
                user_id=current_user_id,
                updated_at=datetime.now()
            )

        # Calculate BMI if height and weight are available
        bmi = None
        bmi_category = None
        if user_profile.height_cm and user_profile.weight_kg:
            height_m = user_profile.height_cm / 100
            bmi = user_profile.weight_kg / (height_m ** 2)

            # Determine BMI category
            if bmi < 18.5:
                bmi_category = "偏瘦"
            elif bmi < 24:
                bmi_category = "正常"
            elif bmi < 28:
                bmi_category = "偏胖"
            else:
                bmi_category = "肥胖"

        return UserHealthDataResponse(
            message="Health data retrieved successfully",
            user_id=current_user_id,
            age=user_profile.age,
            gender=user_profile.gender.value if hasattr(user_profile.gender, 'value') else user_profile.gender,
            height=user_profile.height_cm,
            weight=user_profile.weight_kg,
            activity_level=user_profile.activity_level.value if hasattr(user_profile.activity_level, 'value') else user_profile.activity_level,
            bmi=round(bmi, 1) if bmi else None,
            bmi_category=bmi_category,
            updated_at=user_profile.updated_at or datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to get user health data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health data"
        )


@app.put("/api/v1/user/health-data", response_model=UserHealthDataResponse, tags=["User Profile"])
async def update_user_health_data(
    health_data: UserHealthDataRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Update user's health data

    Args:
        health_data: Health data update request
        current_user_id: Authenticated user ID
        user_repo: User repository instance

    Returns:
        Updated health data with BMI calculations

    Raises:
        HTTPException: If update fails
    """
    try:
        # Update user profile with health data
        update_data = health_data.model_dump(exclude_unset=True)

        # Map field names
        if 'height' in update_data:
            update_data['height_cm'] = update_data.pop('height')
        if 'weight' in update_data:
            update_data['weight_kg'] = update_data.pop('weight')

        updated_profile = await user_repo.update_user_profile(current_user_id, **update_data)

        # Calculate BMI
        bmi = None
        bmi_category = None
        if updated_profile.height_cm and updated_profile.weight_kg:
            height_m = updated_profile.height_cm / 100
            bmi = updated_profile.weight_kg / (height_m ** 2)

            if bmi < 18.5:
                bmi_category = "偏瘦"
            elif bmi < 24:
                bmi_category = "正常"
            elif bmi < 28:
                bmi_category = "偏胖"
            else:
                bmi_category = "肥胖"

        return UserHealthDataResponse(
            message="Health data updated successfully",
            user_id=current_user_id,
            age=updated_profile.age,
            gender=updated_profile.gender.value if hasattr(updated_profile.gender, 'value') else updated_profile.gender,
            height=updated_profile.height_cm,
            weight=updated_profile.weight_kg,
            activity_level=updated_profile.activity_level.value if hasattr(updated_profile.activity_level, 'value') else updated_profile.activity_level,
            bmi=round(bmi, 1) if bmi else None,
            bmi_category=bmi_category,
            updated_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to update user health data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update health data"
        )


# ============================================================================
# USER HEALTH GOALS ENDPOINTS
# ============================================================================

@app.get("/api/v1/user/health-goals", response_model=UserHealthGoalsListResponse, tags=["User Profile"])
async def get_user_health_goals(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get user's health goals

    Args:
        current_user_id: Authenticated user ID

    Returns:
        List of user's health goals

    Raises:
        HTTPException: If goal retrieval fails
    """
    try:
        # Mock implementation - return sample goals
        goals = [
            UserHealthGoalResponse(
                id=f"goal_{current_user_id}_weight_001",
                title="减重目标",
                description="在3个月内减重5公斤",
                type="weight_loss",
                target_value=5.0,
                current_value=2.0,
                unit="kg",
                target_date=date.today() + timedelta(days=90),
                status="active",
                progress=40.0,
                created_at=datetime.now() - timedelta(days=10),
                updated_at=datetime.now()
            ),
            UserHealthGoalResponse(
                id=f"goal_{current_user_id}_steps_001",
                title="每日步数目标",
                description="每天走10000步",
                type="steps",
                target_value=10000.0,
                current_value=7500.0,
                unit="步",
                target_date=date.today() + timedelta(days=30),
                status="active",
                progress=75.0,
                created_at=datetime.now() - timedelta(days=5),
                updated_at=datetime.now()
            )
        ]

        return UserHealthGoalsListResponse(
            message="Health goals retrieved successfully",
            goals=goals,
            total_count=len(goals)
        )

    except Exception as e:
        logger.error(f"Failed to get user health goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health goals"
        )


@app.post("/api/v1/user/health-goals", response_model=UserHealthGoalResponse, tags=["User Profile"])
async def create_user_health_goal(
    goal_request: UserHealthGoalRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new user health goal

    Args:
        goal_request: Health goal creation request
        current_user_id: Authenticated user ID

    Returns:
        Created health goal

    Raises:
        HTTPException: If goal creation fails
    """
    try:
        # Generate goal ID
        goal_id = f"goal_{current_user_id}_{goal_request.type}_{int(datetime.now().timestamp())}"

        # Calculate initial progress
        progress = 0.0
        if goal_request.target_value and goal_request.current_value:
            progress = min((goal_request.current_value / goal_request.target_value) * 100, 100.0)

        return UserHealthGoalResponse(
            id=goal_id,
            title=goal_request.title,
            description=goal_request.description,
            type=goal_request.type,
            target_value=goal_request.target_value,
            current_value=goal_request.current_value,
            unit=goal_request.unit,
            target_date=goal_request.target_date,
            status=goal_request.status,
            progress=progress,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to create user health goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create health goal"
        )


# ============================================================================
# HEALTH PLAN ENDPOINTS
# ============================================================================

@app.get("/api/v1/health-plan/plans", response_model=HealthPlansListResponse, tags=["Health Plans"])
async def get_health_plans(
    current_user_id: str = Depends(get_current_user_id),
    health_plan_repo = Depends(get_health_plan_repository)
):
    """
    Get user's health plans

    Args:
        current_user_id: Authenticated user ID
        health_plan_repo: Health plan repository

    Returns:
        List of user's health plans

    Raises:
        HTTPException: If plan retrieval fails
    """
    try:
        # Get plans from repository
        plans_db = await health_plan_repo.get_user_health_plans(current_user_id)

        # Convert to API models
        plans = []
        for plan_db in plans_db:
            # Convert database model to API model
            from ..models.api_models import HealthPlan, HealthPlanModule

            # Get modules for this plan
            modules_db = await health_plan_repo.get_plan_modules(plan_db.id)
            modules = []
            for module_db in modules_db:
                module = HealthPlanModule(
                    module_type=module_db.module_type,
                    title=module_db.title,
                    description=module_db.description,
                    content=module_db.content,
                    duration_days=module_db.duration_days
                )
                modules.append(module)

            plan = HealthPlan(
                plan_id=plan_db.id,
                title=plan_db.title,
                description=plan_db.description,
                modules=modules,
                duration_days=plan_db.duration_days,
                status=plan_db.status,
                progress=plan_db.progress,
                created_at=plan_db.created_at,
                updated_at=plan_db.updated_at
            )
            plans.append(plan)

        return HealthPlansListResponse(
            message="Health plans retrieved successfully",
            plans=plans,
            total_count=len(plans)
        )

    except Exception as e:
        logger.error(f"Failed to get health plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health plans"
        )


@app.post("/api/v1/health-plan/generate", response_model=HealthPlanGenerateResponse, tags=["Health Plans"])
async def generate_health_plan(
    plan_request: HealthPlanGenerateRequest,
    current_user_id: str = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
    health_plan_repo = Depends(get_health_plan_repository)
):
    """
    Generate a new personalized health plan

    Args:
        plan_request: Health plan generation request
        current_user_id: Authenticated user ID
        user_repo: User repository instance

    Returns:
        Generated health plan with recommendations

    Raises:
        HTTPException: If plan generation fails
    """
    try:
        # Generate plan ID
        plan_id = f"plan_{current_user_id}_{int(datetime.now().timestamp())}"

        # Create plan data
        plan_data = {
            "id": plan_id,
            "title": f"{plan_request.duration_days}天个性化健康计划",
            "description": f"基于您的目标：{', '.join(plan_request.goals)}",
            "duration_days": plan_request.duration_days,
            "status": "active",
            "progress": 0.0,
            "goals": plan_request.goals,
            "preferences": plan_request.user_preferences or {}
        }

        # Create plan in database
        try:
            created_plan_db = await health_plan_repo.create_health_plan(current_user_id, plan_data)
            plan_id = created_plan_db.id  # Use database-generated ID
            logger.info(f"Successfully created health plan {plan_id} in database")
        except Exception as db_error:
            logger.warning(f"Failed to save plan to database: {db_error}, continuing with in-memory plan")
            created_plan_db = None

        # Create modules for the plan
        modules = []
        for module_type in plan_request.modules:
            module_data = {
                "id": f"module_{plan_id}_{module_type}_{int(datetime.now().timestamp())}",
                "module_type": module_type,
                "title": f"{module_type.title()}计划",
                "description": f"个性化的{module_type}方案",
                "duration_days": plan_request.duration_days,
                "content": {},
                "status": "active",
                "progress": 0.0
            }

            if module_type == "diet":
                module_data.update({
                    "title": "个性化饮食计划",
                    "description": "根据您的目标和偏好定制的营养计划",
                    "content": {
                        "daily_calories": 2000,
                        "goals": plan_request.goals,
                        "preferences": plan_request.user_preferences or {},
                        "recommendations": [
                            "多吃蔬菜水果",
                            "控制碳水化合物摄入",
                            "增加蛋白质比例"
                        ]
                    }
                })
            elif module_type == "exercise":
                module_data.update({
                    "title": "运动健身计划",
                    "description": "适合您体能水平的运动方案",
                    "content": {
                        "weekly_frequency": 4,
                        "session_duration": 45,
                        "intensity": "moderate",
                        "exercises": [
                            "有氧运动",
                            "力量训练",
                            "柔韧性训练"
                        ]
                    }
                })
            elif module_type == "weight":
                module_data.update({
                    "title": "体重管理计划",
                    "description": "科学的体重管理策略",
                    "content": {
                        "target_weight_change": -5.0,
                        "weekly_goal": -0.5,
                        "strategies": [
                            "控制热量摄入",
                            "增加运动量",
                            "规律作息"
                        ]
                    }
                })
            elif module_type == "sleep":
                module_data.update({
                    "title": "睡眠优化计划",
                    "description": "改善睡眠质量的方案",
                    "content": {
                        "target_sleep_hours": 8,
                        "bedtime": "22:30",
                        "wake_time": "06:30",
                        "tips": [
                            "睡前1小时避免电子设备",
                            "保持卧室温度适宜",
                            "建立固定的睡前仪式"
                        ]
                    }
                })
            elif module_type == "mental":
                module_data.update({
                    "title": "心理健康计划",
                    "description": "心理健康和压力管理方案",
                    "content": {
                        "daily_meditation": 10,
                        "stress_management": [
                            "深呼吸练习",
                            "正念冥想",
                            "适度运动"
                        ],
                        "mood_tracking": True
                    }
                })

            # Create module in database
            try:
                created_module_db = await health_plan_repo.create_plan_module(plan_id, module_data)
                logger.info(f"Successfully created module {module_data['module_type']} for plan {plan_id}")
            except Exception as db_error:
                logger.warning(f"Failed to save module to database: {db_error}, continuing with in-memory module")
                created_module_db = None

            # Create API model for response
            module = HealthPlanModule(
                module_type=module_data["module_type"],
                title=module_data["title"],
                description=module_data["description"],
                content=module_data["content"],
                duration_days=module_data["duration_days"]
            )
            modules.append(module)

        # Create health plan API model for response
        health_plan = HealthPlan(
            plan_id=plan_id,
            title=plan_data["title"],
            description=plan_data["description"],
            modules=modules,
            duration_days=plan_data["duration_days"],
            status=plan_data["status"],
            progress=plan_data["progress"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Generate recommendations
        recommendations = [
            "建议每天记录您的进展",
            "保持计划的一致性很重要",
            "如有不适请及时调整计划",
            "定期评估和更新目标"
        ]

        return HealthPlanGenerateResponse(
            message="Health plan generated successfully",
            plan=health_plan,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Failed to generate health plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate health plan"
        )


@app.get("/api/v1/health-plan/plans/{plan_id}", response_model=HealthPlanResponse, tags=["Health Plans"])
async def get_health_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific health plan by ID

    Args:
        plan_id: Health plan ID
        current_user_id: Authenticated user ID

    Returns:
        Health plan details

    Raises:
        HTTPException: If plan not found or access denied
    """
    try:
        # Mock implementation - return sample plan
        from ..models.api_models import HealthPlan, HealthPlanModule

        sample_modules = [
            HealthPlanModule(
                module_type="diet",
                title="营养饮食计划",
                description="个性化的营养饮食建议",
                content={
                    "daily_calories": 2000,
                    "meal_plan": "详细的每日餐食安排"
                },
                duration_days=30
            )
        ]

        plan = HealthPlan(
            plan_id=plan_id,
            title="个性化健康计划",
            description="根据您的需求定制的健康管理方案",
            modules=sample_modules,
            duration_days=30,
            status="active",
            progress=25.0,
            created_at=datetime.now() - timedelta(days=7),
            updated_at=datetime.now()
        )

        return HealthPlanResponse(
            message="Health plan retrieved successfully",
            plan=plan
        )

    except Exception as e:
        logger.error(f"Failed to get health plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health plan"
        )


@app.put("/api/v1/health-plan/plans/{plan_id}", response_model=HealthPlanResponse, tags=["Health Plans"])
async def update_health_plan(
    plan_id: str,
    plan_data: HealthPlanRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update a health plan

    Args:
        plan_id: Health plan ID
        plan_data: Updated plan data
        current_user_id: Authenticated user ID

    Returns:
        Updated health plan

    Raises:
        HTTPException: If plan not found or update fails
    """
    try:
        # Mock implementation - return updated plan
        from ..models.api_models import HealthPlan, HealthPlanModule

        # Generate modules based on request
        modules = []
        for module_type in plan_data.modules:
            if module_type == "diet":
                modules.append(HealthPlanModule(
                    module_type="diet",
                    title="个性化饮食计划",
                    description="根据您的目标和偏好定制的营养计划",
                    content={
                        "daily_calories": 2000,
                        "goals": plan_data.goals,
                        "preferences": plan_data.preferences or {},
                        "recommendations": [
                            "多吃蔬菜水果",
                            "控制碳水化合物摄入",
                            "增加蛋白质比例"
                        ]
                    },
                    duration_days=plan_data.duration_days
                ))
            elif module_type == "exercise":
                modules.append(HealthPlanModule(
                    module_type="exercise",
                    title="运动健身计划",
                    description="适合您体能水平的运动方案",
                    content={
                        "weekly_frequency": 4,
                        "session_duration": 45,
                        "intensity": "moderate",
                        "exercises": [
                            "有氧运动",
                            "力量训练",
                            "柔韧性训练"
                        ]
                    },
                    duration_days=plan_data.duration_days
                ))

        updated_plan = HealthPlan(
            plan_id=plan_id,
            title=f"更新的{plan_data.duration_days}天健康计划",
            description=f"基于您的目标：{', '.join(plan_data.goals)}",
            modules=modules,
            duration_days=plan_data.duration_days,
            status="active",
            progress=0.0,
            created_at=datetime.now() - timedelta(days=7),
            updated_at=datetime.now()
        )

        return HealthPlanResponse(
            message="Health plan updated successfully",
            plan=updated_plan
        )

    except Exception as e:
        logger.error(f"Failed to update health plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update health plan"
        )


@app.delete("/api/v1/health-plan/plans/{plan_id}", response_model=BaseResponse, tags=["Health Plans"])
async def delete_health_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a health plan

    Args:
        plan_id: Health plan ID
        current_user_id: Authenticated user ID

    Returns:
        Deletion confirmation

    Raises:
        HTTPException: If plan not found or deletion fails
    """
    try:
        # Mock implementation - simulate deletion
        logger.info(f"Deleting health plan {plan_id} for user {current_user_id}")

        return BaseResponse(
            message="Health plan deleted successfully"
        )

    except Exception as e:
        logger.error(f"Failed to delete health plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete health plan"
        )


@app.get("/api/v1/health-plan/plans/{plan_id}/export", tags=["Health Plans"])
async def export_health_plan(
    plan_id: str,
    format: str = "pdf",
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Export health plan in specified format

    Args:
        plan_id: Health plan ID
        format: Export format (pdf, json, txt)
        current_user_id: Authenticated user ID

    Returns:
        Exported plan file

    Raises:
        HTTPException: If plan not found or export fails
    """
    try:
        # Mock implementation - return export confirmation
        logger.info(f"Exporting health plan {plan_id} in {format} format for user {current_user_id}")

        if format not in ["pdf", "json", "txt"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid export format. Supported formats: pdf, json, txt"
            )

        # In a real implementation, this would generate and return the actual file
        return BaseResponse(
            message=f"Health plan exported successfully in {format} format",
            data={"export_format": format, "plan_id": plan_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export health plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export health plan"
        )


@app.post("/api/v1/health-plan/plans/{plan_id}/feedback", response_model=BaseResponse, tags=["Health Plans"])
async def save_plan_feedback(
    plan_id: str,
    feedback_data: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Save feedback for a health plan

    Args:
        plan_id: Health plan ID
        feedback_data: Feedback data
        current_user_id: Authenticated user ID

    Returns:
        Feedback save confirmation

    Raises:
        HTTPException: If plan not found or feedback save fails
    """
    try:
        # Mock implementation - save feedback
        logger.info(f"Saving feedback for health plan {plan_id} from user {current_user_id}")

        return BaseResponse(
            message="Plan feedback saved successfully",
            data={"plan_id": plan_id, "feedback_id": f"feedback_{plan_id}_{int(datetime.now().timestamp())}"}
        )

    except Exception as e:
        logger.error(f"Failed to save plan feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save plan feedback"
        )


@app.get("/api/v1/health-plan/plans/{plan_id}/progress", response_model=BaseResponse, tags=["Health Plans"])
async def get_plan_progress(
    plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get progress for a health plan

    Args:
        plan_id: Health plan ID
        current_user_id: Authenticated user ID

    Returns:
        Plan progress data

    Raises:
        HTTPException: If plan not found or progress retrieval fails
    """
    try:
        # Mock implementation - return progress data
        progress_data = {
            "plan_id": plan_id,
            "overall_progress": 65.5,
            "module_progress": {
                "diet": 70.0,
                "exercise": 60.0,
                "weight": 65.0
            },
            "daily_progress": [
                {"date": "2024-01-01", "progress": 10.0},
                {"date": "2024-01-02", "progress": 20.0},
                {"date": "2024-01-03", "progress": 35.0},
                {"date": "2024-01-04", "progress": 50.0},
                {"date": "2024-01-05", "progress": 65.5}
            ],
            "total_tasks": 20,
            "completed_tasks": 13,
            "last_updated": datetime.now().isoformat()
        }

        return BaseResponse(
            message="Plan progress retrieved successfully",
            data=progress_data
        )

    except Exception as e:
        logger.error(f"Failed to get plan progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plan progress"
        )


@app.put("/api/v1/health-plan/plans/{plan_id}/progress", response_model=BaseResponse, tags=["Health Plans"])
async def update_plan_progress(
    plan_id: str,
    progress_data: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update progress for a health plan

    Args:
        plan_id: Health plan ID
        progress_data: Progress update data
        current_user_id: Authenticated user ID

    Returns:
        Progress update confirmation

    Raises:
        HTTPException: If plan not found or progress update fails
    """
    try:
        # Mock implementation - update progress
        logger.info(f"Updating progress for health plan {plan_id} from user {current_user_id}")

        return BaseResponse(
            message="Plan progress updated successfully",
            data={
                "plan_id": plan_id,
                "updated_progress": progress_data.get("progress", 0),
                "updated_at": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Failed to update plan progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update plan progress"
        )


@app.get("/api/v1/health-plan/templates", response_model=BaseResponse, tags=["Health Plans"])
async def get_plan_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get health plan templates

    Args:
        category: Template category filter
        difficulty: Difficulty level filter
        current_user_id: Authenticated user ID

    Returns:
        List of plan templates

    Raises:
        HTTPException: If template retrieval fails
    """
    try:
        # Mock implementation - return template data
        templates = [
            {
                "id": "template_weight_loss_beginner",
                "name": "减重入门计划",
                "description": "适合初学者的减重计划，包含饮食和运动指导",
                "category": "weight_loss",
                "difficulty_level": "beginner",
                "duration_days": 30,
                "modules": ["diet", "exercise", "weight"],
                "goals": ["减重", "健康饮食", "建立运动习惯"],
                "usage_count": 156,
                "rating": 4.5
            },
            {
                "id": "template_fitness_intermediate",
                "name": "健身进阶计划",
                "description": "适合有一定基础的健身爱好者",
                "category": "fitness",
                "difficulty_level": "intermediate",
                "duration_days": 60,
                "modules": ["exercise", "weight", "mental"],
                "goals": ["增强体质", "肌肉增长", "提高耐力"],
                "usage_count": 89,
                "rating": 4.7
            },
            {
                "id": "template_wellness_beginner",
                "name": "全面健康计划",
                "description": "综合性的健康管理计划",
                "category": "wellness",
                "difficulty_level": "beginner",
                "duration_days": 90,
                "modules": ["diet", "exercise", "sleep", "mental"],
                "goals": ["整体健康", "生活平衡", "压力管理"],
                "usage_count": 234,
                "rating": 4.3
            }
        ]

        # Apply filters
        if category:
            templates = [t for t in templates if t["category"] == category]
        if difficulty:
            templates = [t for t in templates if t["difficulty_level"] == difficulty]

        return BaseResponse(
            message="Plan templates retrieved successfully",
            data={"templates": templates, "total_count": len(templates)}
        )

    except Exception as e:
        logger.error(f"Failed to get plan templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plan templates"
        )


@app.post("/api/v1/health-plan/templates/{template_id}/create", response_model=HealthPlanResponse, tags=["Health Plans"])
async def create_from_template(
    template_id: str,
    custom_data: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a health plan from template

    Args:
        template_id: Template ID
        custom_data: Customization data
        current_user_id: Authenticated user ID

    Returns:
        Created health plan

    Raises:
        HTTPException: If template not found or plan creation fails
    """
    try:
        # Mock implementation - create plan from template
        from ..models.api_models import HealthPlan, HealthPlanModule

        # Generate plan ID
        plan_id = f"plan_{current_user_id}_{int(datetime.now().timestamp())}"

        # Mock template data
        template_modules = [
            HealthPlanModule(
                module_type="diet",
                title="模板饮食计划",
                description="基于模板的个性化饮食建议",
                content={
                    "daily_calories": custom_data.get("target_calories", 2000),
                    "template_id": template_id,
                    "customizations": custom_data
                },
                duration_days=custom_data.get("duration_days", 30)
            )
        ]

        plan = HealthPlan(
            plan_id=plan_id,
            title=f"基于模板的健康计划",
            description=f"使用模板 {template_id} 创建的个性化计划",
            modules=template_modules,
            duration_days=custom_data.get("duration_days", 30),
            status="active",
            progress=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return HealthPlanResponse(
            message="Health plan created from template successfully",
            plan=plan
        )

    except Exception as e:
        logger.error(f"Failed to create plan from template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create plan from template"
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

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
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

    yield

    # Shutdown
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
            if method == "post" and path in ["/api/v1/auth/login", "/api/v1/auth/register"]:
                continue  # Skip auth for login and register endpoints

            # Add security requirement to protected endpoints
            openapi_schema["paths"][path][method]["security"] = get_security_requirements()

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================================
# EXPORT FOR EXTERNAL USE
# ============================================================================

__all__ = ["app"]