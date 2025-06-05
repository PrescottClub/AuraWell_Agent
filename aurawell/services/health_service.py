"""
Health Service for AuraWell

Handles health data processing, analysis, and insight generation.
Coordinates between health data repositories, AI services, and orchestrator.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta

from .base_service import BaseService, ServiceResult, ServiceStatus

logger = logging.getLogger(__name__)


class HealthService(BaseService):
    """
    Service for health data management and analysis
    
    Provides async methods for:
    - Health data storage and retrieval
    - Health insights generation
    - Health plan creation and management
    - Data synchronization from external platforms
    """
    
    def __init__(self, health_repository=None, insight_repository=None, 
                 plan_repository=None, orchestrator=None, database_manager=None):
        """
        Initialize health service
        
        Args:
            health_repository: Health data repository instance
            insight_repository: Insight repository instance
            plan_repository: Plan repository instance
            orchestrator: AuraWell orchestrator instance
            database_manager: Database manager instance
        """
        super().__init__("HealthService")
        self.health_repository = health_repository
        self.insight_repository = insight_repository
        self.plan_repository = plan_repository
        self.orchestrator = orchestrator
        self.database_manager = database_manager
        self._analysis_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 600  # 10 minutes
    
    async def _initialize_service(self) -> None:
        """Initialize health service"""
        if self.database_manager and not self.database_manager.is_connected():
            if not self.database_manager.connect():
                raise RuntimeError("Failed to connect to database")
        
        # Initialize repositories if not provided
        if not self.health_repository and self.database_manager:
            from ..database.repositories import HealthDataRepository
            self.health_repository = HealthDataRepository(self.database_manager)
        
        if not self.insight_repository and self.database_manager:
            from ..database.repositories import InsightRepository
            self.insight_repository = InsightRepository(self.database_manager)
        
        if not self.plan_repository and self.database_manager:
            from ..database.repositories import PlanRepository
            self.plan_repository = PlanRepository(self.database_manager)
        
        # Initialize orchestrator if not provided
        if not self.orchestrator:
            try:
                from ..core.orchestrator_v2 import AuraWellOrchestrator
                self.orchestrator = AuraWellOrchestrator()
            except Exception as e:
                self.logger.warning(f"Failed to initialize orchestrator: {e}")
        
        self.logger.info("Health service initialized")
    
    async def _shutdown_service(self) -> None:
        """Shutdown health service"""
        self._analysis_cache.clear()
        self.logger.info("Health service shutdown")
    
    async def _perform_health_check(self) -> Optional[Dict[str, Any]]:
        """Perform health service health check"""
        health_details = {
            "cache_size": len(self._analysis_cache),
            "repositories_available": {
                "health_data": self.health_repository is not None,
                "insights": self.insight_repository is not None,
                "plans": self.plan_repository is not None
            },
            "orchestrator_available": self.orchestrator is not None,
            "database_connected": self.database_manager.is_connected() if self.database_manager else False
        }
        
        # Test database connectivity
        if self.health_repository:
            try:
                # Try to get health data (with limit 1 to minimize impact)
                test_data = await self.get_health_data("test_user", limit=1)
                health_details["database_test"] = "success"
            except Exception as e:
                health_details["database_test"] = f"failed: {str(e)}"
                self._health_status = ServiceStatus.DEGRADED
        
        return health_details
    
    async def store_health_data(self, user_id: str, data_type: str, 
                               date: str, data: Dict[str, Any],
                               source_platform: Optional[str] = None,
                               data_quality: Optional[str] = None) -> ServiceResult[bool]:
        """
        Store health data for a user
        
        Args:
            user_id: User identifier
            data_type: Type of health data ('activity', 'sleep', 'heart_rate', 'nutrition')
            date: Date in YYYY-MM-DD format
            data: Health data dictionary
            source_platform: Source platform name
            data_quality: Data quality indicator
            
        Returns:
            ServiceResult with storage success status
        """
        try:
            # Create health data model
            from ..database.models import HealthDataModel
            health_data = HealthDataModel(
                user_id=user_id,
                data_type=data_type,
                date=date,
                data_json=data,
                source_platform=source_platform,
                data_quality=data_quality
            )
            
            # Store in database
            if self.health_repository:
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self.health_repository.store_health_data, health_data
                )
                
                if not success:
                    return ServiceResult.error_result(
                        error="Failed to store health data in database",
                        error_code="DATABASE_ERROR"
                    )
            
            # Clear analysis cache for this user
            self._clear_user_cache(user_id)
            
            self.logger.info(f"Stored {data_type} data for user {user_id} on {date}")
            return ServiceResult.success_result(True)
            
        except Exception as e:
            self.logger.error(f"Error storing health data: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    async def get_health_data(self, user_id: str, data_type: Optional[str] = None,
                             start_date: Optional[str] = None, end_date: Optional[str] = None,
                             limit: int = 100) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Get health data for a user
        
        Args:
            user_id: User identifier
            data_type: Optional data type filter
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            limit: Maximum number of records
            
        Returns:
            ServiceResult with list of health data
        """
        try:
            if self.health_repository:
                health_data_list = await asyncio.get_event_loop().run_in_executor(
                    None, self.health_repository.get_health_data,
                    user_id, data_type, start_date, end_date, limit
                )
                
                data_list = [data.to_dict() for data in health_data_list]
                return ServiceResult.success_result(data_list)
            
            return ServiceResult.success_result([])
            
        except Exception as e:
            self.logger.error(f"Error getting health data for user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    async def analyze_health_data(self, user_id: str, user_profile: Dict[str, Any],
                                 days_back: int = 7) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Analyze health data and generate insights
        
        Args:
            user_id: User identifier
            user_profile: User profile data
            days_back: Number of days to analyze
            
        Returns:
            ServiceResult with list of insights
        """
        try:
            # Check cache first
            cache_key = f"{user_id}_{days_back}"
            cached_analysis = self._get_cached_analysis(cache_key)
            if cached_analysis:
                return ServiceResult.success_result(cached_analysis)
            
            # Get recent health data
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Get different types of health data
            activity_result = await self.get_health_data(user_id, 'activity', start_date, end_date)
            sleep_result = await self.get_health_data(user_id, 'sleep', start_date, end_date)
            heart_rate_result = await self.get_health_data(user_id, 'heart_rate', start_date, end_date)
            nutrition_result = await self.get_health_data(user_id, 'nutrition', start_date, end_date)
            
            # Convert to format expected by orchestrator
            activity_data = [item['data_json'] for item in activity_result.data] if activity_result.success else []
            sleep_data = [item['data_json'] for item in sleep_result.data] if sleep_result.success else []
            heart_rate_data = [item['data_json'] for item in heart_rate_result.data] if heart_rate_result.success else []
            nutrition_data = [item['data_json'] for item in nutrition_result.data] if nutrition_result.success else []
            
            # Use orchestrator to analyze data
            insights = []
            if self.orchestrator:
                try:
                    insights = self.orchestrator.analyze_user_health_data(
                        user_profile=user_profile,
                        activity_data=activity_data,
                        sleep_data=sleep_data,
                        heart_rate_data=heart_rate_data,
                        nutrition_data=nutrition_data
                    )
                    
                    # Convert insights to dict format
                    insights_data = []
                    for insight in insights:
                        insight_dict = {
                            'insight_id': insight.insight_id,
                            'insight_type': insight.insight_type.value,
                            'priority': insight.priority.value,
                            'title': insight.title,
                            'description': insight.description,
                            'recommendations': insight.recommendations,
                            'data_points': insight.data_points,
                            'confidence_score': insight.confidence_score,
                            'generated_at': insight.generated_at.isoformat()
                        }
                        insights_data.append(insight_dict)
                        
                        # Store insight in database
                        if self.insight_repository:
                            from ..database.models import InsightModel
                            insight_model = InsightModel(
                                insight_id=insight.insight_id,
                                user_id=user_id,
                                insight_type=insight.insight_type.value,
                                priority=insight.priority.value,
                                title=insight.title,
                                description=insight.description,
                                recommendations=insight.recommendations,
                                data_points=insight.data_points,
                                confidence_score=insight.confidence_score,
                                generated_at=insight.generated_at,
                                expires_at=insight.expires_at
                            )
                            
                            await asyncio.get_event_loop().run_in_executor(
                                None, self.insight_repository.store_insight, insight_model
                            )
                    
                    insights = insights_data
                    
                except Exception as e:
                    self.logger.warning(f"Orchestrator analysis failed: {e}")
                    insights = []
            
            # Cache the analysis
            self._cache_analysis(cache_key, insights)
            
            self.logger.info(f"Analyzed health data for user {user_id}, generated {len(insights)} insights")
            return ServiceResult.success_result(insights)
            
        except Exception as e:
            self.logger.error(f"Error analyzing health data for user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )

    async def get_user_insights(self, user_id: str, insight_type: Optional[str] = None,
                               priority: Optional[str] = None, active_only: bool = True,
                               limit: int = 50) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Get insights for a user

        Args:
            user_id: User identifier
            insight_type: Optional insight type filter
            priority: Optional priority filter
            active_only: Only return non-expired insights
            limit: Maximum number of insights

        Returns:
            ServiceResult with list of insights
        """
        try:
            if self.insight_repository:
                insights = await asyncio.get_event_loop().run_in_executor(
                    None, self.insight_repository.get_user_insights,
                    user_id, insight_type, priority, active_only, limit
                )

                insights_data = []
                for insight in insights:
                    insight_dict = {
                        'insight_id': insight.insight_id,
                        'user_id': insight.user_id,
                        'insight_type': insight.insight_type,
                        'priority': insight.priority,
                        'title': insight.title,
                        'description': insight.description,
                        'recommendations': insight.recommendations,
                        'data_points': insight.data_points,
                        'confidence_score': insight.confidence_score,
                        'generated_at': insight.generated_at.isoformat() if insight.generated_at else None,
                        'expires_at': insight.expires_at.isoformat() if insight.expires_at else None
                    }
                    insights_data.append(insight_dict)

                return ServiceResult.success_result(insights_data)

            return ServiceResult.success_result([])

        except Exception as e:
            self.logger.error(f"Error getting insights for user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )

    async def get_user_health_plan(self, user_id: str, active_only: bool = True) -> ServiceResult[Optional[Dict[str, Any]]]:
        """
        Get current health plan for a user

        Args:
            user_id: User identifier
            active_only: Only return non-expired plans

        Returns:
            ServiceResult with health plan data or None
        """
        try:
            if self.plan_repository:
                plan = await asyncio.get_event_loop().run_in_executor(
                    None, self.plan_repository.get_user_plan, user_id, active_only
                )

                if plan:
                    plan_dict = {
                        'plan_id': plan.plan_id,
                        'user_id': plan.user_id,
                        'title': plan.title,
                        'description': plan.description,
                        'goals': plan.goals,
                        'daily_recommendations': plan.daily_recommendations,
                        'weekly_targets': plan.weekly_targets,
                        'created_at': plan.created_at.isoformat() if plan.created_at else None,
                        'valid_until': plan.valid_until.isoformat() if plan.valid_until else None,
                        'last_updated': plan.last_updated.isoformat() if plan.last_updated else None
                    }
                    return ServiceResult.success_result(plan_dict)

            return ServiceResult.success_result(None)

        except Exception as e:
            self.logger.error(f"Error getting health plan for user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )

    async def get_daily_recommendations(self, user_id: str,
                                      target_date: Optional[datetime] = None) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Get daily recommendations for a user

        Args:
            user_id: User identifier
            target_date: Target date for recommendations

        Returns:
            ServiceResult with list of daily recommendations
        """
        try:
            # Get current health plan
            plan_result = await self.get_user_health_plan(user_id)

            if plan_result.success and plan_result.data:
                recommendations = plan_result.data.get('daily_recommendations', [])
                return ServiceResult.success_result(recommendations)

            # Fallback: use orchestrator
            if self.orchestrator:
                try:
                    recommendations = self.orchestrator.get_daily_recommendations(
                        user_id, target_date
                    )
                    return ServiceResult.success_result(recommendations)
                except Exception as e:
                    self.logger.warning(f"Orchestrator recommendations failed: {e}")

            # Default recommendations
            default_recommendations = [
                {
                    "time": "morning",
                    "type": "exercise",
                    "title": "晨间步行",
                    "description": "进行20-30分钟的轻松步行",
                    "duration_minutes": 25,
                    "priority": "medium"
                },
                {
                    "time": "afternoon",
                    "type": "hydration",
                    "title": "补充水分",
                    "description": "确保已饮用足够的水",
                    "priority": "high"
                },
                {
                    "time": "evening",
                    "type": "relaxation",
                    "title": "放松活动",
                    "description": "进行冥想或深呼吸练习",
                    "duration_minutes": 10,
                    "priority": "low"
                }
            ]

            return ServiceResult.success_result(default_recommendations)

        except Exception as e:
            self.logger.error(f"Error getting daily recommendations for user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )

    def _cache_analysis(self, cache_key: str, analysis_data: List[Dict[str, Any]]) -> None:
        """Cache analysis data with timestamp"""
        self._analysis_cache[cache_key] = {
            'data': analysis_data,
            'cached_at': datetime.now(timezone.utc).timestamp()
        }

    def _get_cached_analysis(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get analysis from cache if not expired"""
        cached_entry = self._analysis_cache.get(cache_key)
        if not cached_entry:
            return None

        # Check if cache entry is expired
        now = datetime.now(timezone.utc).timestamp()
        if now - cached_entry['cached_at'] > self._cache_ttl:
            self._analysis_cache.pop(cache_key, None)
            return None

        return cached_entry['data']

    def _clear_user_cache(self, user_id: str) -> None:
        """Clear cache entries for a specific user"""
        keys_to_remove = [key for key in self._analysis_cache.keys() if key.startswith(user_id)]
        for key in keys_to_remove:
            self._analysis_cache.pop(key, None)

    def clear_cache(self) -> None:
        """Clear all analysis cache"""
        self._analysis_cache.clear()
        self.logger.info("Health analysis cache cleared")
    
    async def create_health_plan(self, user_id: str, user_profile: Dict[str, Any],
                                user_preferences: Optional[Dict[str, Any]] = None) -> ServiceResult[Dict[str, Any]]:
        """
        Create a personalized health plan
        
        Args:
            user_id: User identifier
            user_profile: User profile data
            user_preferences: User preferences data
            
        Returns:
            ServiceResult with health plan data
        """
        try:
            # Get recent insights
            insights_result = await self.get_user_insights(user_id, limit=5)
            recent_insights = insights_result.data if insights_result.success else []
            
            # Use orchestrator to create plan
            if self.orchestrator:
                try:
                    # Convert insights back to orchestrator format
                    insight_objects = []
                    for insight_data in recent_insights:
                        from ..core.orchestrator_v2 import HealthInsight, InsightType, InsightPriority
                        insight_obj = HealthInsight(
                            insight_id=insight_data['insight_id'],
                            insight_type=InsightType(insight_data['insight_type']),
                            priority=InsightPriority(insight_data['priority']),
                            title=insight_data['title'],
                            description=insight_data['description'],
                            recommendations=insight_data['recommendations'],
                            data_points=insight_data['data_points'],
                            confidence_score=insight_data['confidence_score'],
                            generated_at=datetime.fromisoformat(insight_data['generated_at'])
                        )
                        insight_objects.append(insight_obj)
                    
                    health_plan = self.orchestrator.create_personalized_health_plan(
                        user_profile=user_profile,
                        user_preferences=user_preferences or {},
                        recent_insights=insight_objects
                    )
                    
                    # Convert plan to dict format
                    plan_dict = {
                        'plan_id': health_plan.plan_id,
                        'user_id': health_plan.user_id,
                        'title': health_plan.title,
                        'description': health_plan.description,
                        'goals': health_plan.goals,
                        'daily_recommendations': health_plan.daily_recommendations,
                        'weekly_targets': health_plan.weekly_targets,
                        'created_at': health_plan.created_at.isoformat(),
                        'valid_until': health_plan.valid_until.isoformat(),
                        'last_updated': health_plan.last_updated.isoformat()
                    }
                    
                    # Store plan in database
                    if self.plan_repository:
                        from ..database.models import PlanModel
                        plan_model = PlanModel(
                            plan_id=health_plan.plan_id,
                            user_id=health_plan.user_id,
                            title=health_plan.title,
                            description=health_plan.description,
                            goals=health_plan.goals,
                            daily_recommendations=health_plan.daily_recommendations,
                            weekly_targets=health_plan.weekly_targets,
                            created_at=health_plan.created_at,
                            valid_until=health_plan.valid_until,
                            last_updated=health_plan.last_updated
                        )
                        
                        await asyncio.get_event_loop().run_in_executor(
                            None, self.plan_repository.store_plan, plan_model
                        )
                    
                    self.logger.info(f"Created health plan {health_plan.plan_id} for user {user_id}")
                    return ServiceResult.success_result(plan_dict)
                    
                except Exception as e:
                    self.logger.warning(f"Orchestrator plan creation failed: {e}")
            
            # Fallback: create basic plan
            basic_plan = {
                'plan_id': f"basic_plan_{user_id}_{int(datetime.now().timestamp())}",
                'user_id': user_id,
                'title': "基础健康计划",
                'description': "基于您的基本信息制定的健康计划",
                'goals': [
                    {"type": "daily_steps", "target": user_profile.get('daily_steps_goal', 10000)},
                    {"type": "sleep_hours", "target": user_profile.get('sleep_duration_goal_hours', 8.0)}
                ],
                'daily_recommendations': [
                    {"time": "morning", "activity": "轻度运动", "duration": 30},
                    {"time": "evening", "activity": "放松时间", "duration": 15}
                ],
                'weekly_targets': {"exercise_sessions": 3, "rest_days": 1},
                'created_at': datetime.now(timezone.utc).isoformat(),
                'valid_until': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            return ServiceResult.success_result(basic_plan)
            
        except Exception as e:
            self.logger.error(f"Error creating health plan for user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
