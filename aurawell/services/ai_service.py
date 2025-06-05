"""
AI Service for AuraWell

Handles AI-powered analysis, insights generation, and recommendations.
Provides async interface to DeepSeek AI and other AI services.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from .base_service import BaseService, ServiceResult, ServiceStatus

logger = logging.getLogger(__name__)


class AIService(BaseService):
    """
    Service for AI-powered health analysis and recommendations
    
    Provides async methods for:
    - Health data analysis using AI
    - Personalized recommendations generation
    - Natural language processing
    - Pattern recognition and insights
    """
    
    def __init__(self, deepseek_client=None):
        """
        Initialize AI service
        
        Args:
            deepseek_client: DeepSeek client instance
        """
        super().__init__("AIService")
        self.deepseek_client = deepseek_client
        self._request_count = 0
        self._error_count = 0
        self._last_request_time = None
    
    async def _initialize_service(self) -> None:
        """Initialize AI service"""
        # Initialize DeepSeek client if not provided
        if not self.deepseek_client:
            try:
                # Use lazy import to avoid circular dependencies
                import os
                if os.getenv('DEEPSEEK_API_KEY'):
                    from ..core.deepseek_client import DeepSeekClient
                    self.deepseek_client = DeepSeekClient()
                    self.logger.info("DeepSeek client initialized")
                else:
                    self.logger.warning("DEEPSEEK_API_KEY not found, AI features will be limited")
            except Exception as e:
                self.logger.warning(f"Failed to initialize DeepSeek client: {e}")
        
        self.logger.info("AI service initialized")
    
    async def _shutdown_service(self) -> None:
        """Shutdown AI service"""
        self.deepseek_client = None
        self.logger.info("AI service shutdown")
    
    async def _perform_health_check(self) -> Optional[Dict[str, Any]]:
        """Perform AI service health check"""
        health_details = {
            "deepseek_available": self.deepseek_client is not None,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "last_request": self._last_request_time.isoformat() if self._last_request_time else None
        }
        
        # Test AI connectivity
        if self.deepseek_client:
            try:
                # Simple test request
                test_result = await self.analyze_text("Test health check", max_tokens=10)
                if test_result.success:
                    health_details["connectivity_test"] = "success"
                else:
                    health_details["connectivity_test"] = f"failed: {test_result.error}"
                    self._health_status = ServiceStatus.DEGRADED
            except Exception as e:
                health_details["connectivity_test"] = f"error: {str(e)}"
                self._health_status = ServiceStatus.DEGRADED
        
        return health_details
    
    async def analyze_health_data(self, user_profile: Dict[str, Any], 
                                 health_data: Dict[str, List[Dict[str, Any]]]) -> ServiceResult[Dict[str, Any]]:
        """
        Analyze health data using AI
        
        Args:
            user_profile: User profile information
            health_data: Dictionary containing different types of health data
            
        Returns:
            ServiceResult with AI analysis results
        """
        try:
            if not self.deepseek_client:
                return ServiceResult.error_result(
                    error="AI service not available",
                    error_code="AI_UNAVAILABLE"
                )
            
            # Prepare data summary for AI analysis
            data_summary = self._prepare_health_data_summary(user_profile, health_data)
            
            # Create AI prompt for health analysis
            messages = [
                {
                    "role": "system",
                    "content": """你是AuraWell的专业健康分析师。基于用户的健康数据，提供专业的分析和建议。
                    请以JSON格式返回分析结果，包含以下字段：
                    - insights: 健康洞察列表
                    - recommendations: 建议列表
                    - risk_factors: 风险因素
                    - positive_trends: 积极趋势
                    - overall_score: 整体健康评分(1-10)"""
                },
                {
                    "role": "user",
                    "content": f"请分析以下健康数据：\n{data_summary}"
                }
            ]
            
            # Get AI response
            ai_result = await self._make_ai_request(messages, temperature=0.3, max_tokens=1000)
            
            if not ai_result.success:
                return ai_result
            
            # Parse AI response
            try:
                import json
                analysis_result = json.loads(ai_result.data)
            except json.JSONDecodeError:
                # Fallback: use raw text response
                analysis_result = {
                    "insights": [ai_result.data],
                    "recommendations": ["基于AI分析的个性化建议"],
                    "risk_factors": [],
                    "positive_trends": [],
                    "overall_score": 7.0
                }
            
            self.logger.info(f"AI health analysis completed for user {user_profile.get('user_id')}")
            return ServiceResult.success_result(analysis_result)
            
        except Exception as e:
            self._error_count += 1
            self.logger.error(f"Error in AI health analysis: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="AI_ANALYSIS_ERROR"
            )
    
    async def generate_health_plan(self, user_profile: Dict[str, Any],
                                  user_preferences: Dict[str, Any],
                                  insights: List[Dict[str, Any]]) -> ServiceResult[Dict[str, Any]]:
        """
        Generate personalized health plan using AI
        
        Args:
            user_profile: User profile information
            user_preferences: User preferences and goals
            insights: Recent health insights
            
        Returns:
            ServiceResult with generated health plan
        """
        try:
            if not self.deepseek_client:
                return ServiceResult.error_result(
                    error="AI service not available",
                    error_code="AI_UNAVAILABLE"
                )
            
            # Prepare context for AI
            context = {
                "user_profile": {
                    "age": user_profile.get("age"),
                    "gender": user_profile.get("gender"),
                    "activity_level": user_profile.get("activity_level"),
                    "goals": user_profile.get("primary_goal"),
                    "daily_steps_goal": user_profile.get("daily_steps_goal"),
                    "sleep_goal": user_profile.get("sleep_duration_goal_hours")
                },
                "preferences": user_preferences,
                "recent_insights": [
                    {
                        "type": insight.get("insight_type"),
                        "priority": insight.get("priority"),
                        "title": insight.get("title")
                    } for insight in insights[:5]  # Top 5 insights
                ]
            }
            
            # Create AI prompt for health plan generation
            messages = [
                {
                    "role": "system",
                    "content": """你是AuraWell的健康计划专家。基于用户信息和健康洞察，制定个性化的30天健康计划。
                    请以JSON格式返回计划，包含以下字段：
                    - title: 计划标题
                    - description: 计划描述
                    - goals: 目标列表 [{"type": "goal_type", "target": value, "timeframe": "daily/weekly"}]
                    - daily_recommendations: 每日建议 [{"time": "morning/afternoon/evening", "activity": "活动", "duration": minutes}]
                    - weekly_targets: 周目标 {"exercise_sessions": 3, "rest_days": 1}
                    - tips: 实用建议列表"""
                },
                {
                    "role": "user",
                    "content": f"请为以下用户制定健康计划：\n{context}"
                }
            ]
            
            # Get AI response
            ai_result = await self._make_ai_request(messages, temperature=0.5, max_tokens=1500)
            
            if not ai_result.success:
                return ai_result
            
            # Parse AI response
            try:
                import json
                plan_result = json.loads(ai_result.data)
            except json.JSONDecodeError:
                # Fallback: create basic plan structure
                plan_result = {
                    "title": "AI个性化健康计划",
                    "description": ai_result.data,
                    "goals": [
                        {"type": "daily_steps", "target": user_profile.get("daily_steps_goal", 10000), "timeframe": "daily"},
                        {"type": "sleep_hours", "target": user_profile.get("sleep_duration_goal_hours", 8.0), "timeframe": "daily"}
                    ],
                    "daily_recommendations": [
                        {"time": "morning", "activity": "晨间运动", "duration": 30},
                        {"time": "evening", "activity": "放松活动", "duration": 15}
                    ],
                    "weekly_targets": {"exercise_sessions": 3, "meditation_sessions": 5},
                    "tips": ["保持规律作息", "均衡饮食", "适量运动"]
                }
            
            self.logger.info(f"AI health plan generated for user {user_profile.get('user_id')}")
            return ServiceResult.success_result(plan_result)
            
        except Exception as e:
            self._error_count += 1
            self.logger.error(f"Error in AI health plan generation: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="AI_PLAN_ERROR"
            )
    
    async def analyze_text(self, text: str, context: Optional[str] = None,
                          temperature: float = 0.7, max_tokens: int = 500) -> ServiceResult[str]:
        """
        Analyze text using AI
        
        Args:
            text: Text to analyze
            context: Optional context for analysis
            temperature: AI temperature parameter
            max_tokens: Maximum tokens in response
            
        Returns:
            ServiceResult with AI analysis
        """
        try:
            if not self.deepseek_client:
                return ServiceResult.error_result(
                    error="AI service not available",
                    error_code="AI_UNAVAILABLE"
                )
            
            # Create messages
            messages = [
                {
                    "role": "system",
                    "content": context or "你是一个专业的健康助手，请分析用户的文本并提供有用的见解。"
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
            
            # Get AI response
            ai_result = await self._make_ai_request(messages, temperature, max_tokens)
            return ai_result
            
        except Exception as e:
            self._error_count += 1
            self.logger.error(f"Error in AI text analysis: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="AI_TEXT_ERROR"
            )
    
    async def _make_ai_request(self, messages: List[Dict[str, str]], 
                              temperature: float = 0.7, max_tokens: int = 1000) -> ServiceResult[str]:
        """
        Make request to AI service
        
        Args:
            messages: List of message dictionaries
            temperature: AI temperature parameter
            max_tokens: Maximum tokens in response
            
        Returns:
            ServiceResult with AI response
        """
        try:
            self._request_count += 1
            self._last_request_time = datetime.now(timezone.utc)
            
            # Make async AI request
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.deepseek_client.get_deepseek_response(
                    messages=messages,
                    model_name="deepseek-r1",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            )
            
            return ServiceResult.success_result(response.content)
            
        except Exception as e:
            self._error_count += 1
            raise e
    
    def _prepare_health_data_summary(self, user_profile: Dict[str, Any], 
                                   health_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Prepare health data summary for AI analysis"""
        summary_parts = []
        
        # User profile summary
        age = user_profile.get('age', '未知')
        gender = user_profile.get('gender', '未知')
        summary_parts.append(f"用户信息: {age}岁, {gender}")
        
        # Activity data summary
        activity_data = health_data.get('activity', [])
        if activity_data:
            avg_steps = sum(data.get('steps', 0) for data in activity_data) / len(activity_data)
            summary_parts.append(f"活动数据: 最近{len(activity_data)}天平均步数{int(avg_steps)}步")
        
        # Sleep data summary
        sleep_data = health_data.get('sleep', [])
        if sleep_data:
            avg_sleep = sum(data.get('duration_hours', 0) for data in sleep_data) / len(sleep_data)
            summary_parts.append(f"睡眠数据: 最近{len(sleep_data)}天平均睡眠{avg_sleep:.1f}小时")
        
        # Nutrition data summary
        nutrition_data = health_data.get('nutrition', [])
        if nutrition_data:
            avg_calories = sum(data.get('calories', 0) for data in nutrition_data) / len(nutrition_data)
            summary_parts.append(f"营养数据: 最近{len(nutrition_data)}天平均摄入{int(avg_calories)}卡路里")
        
        return "; ".join(summary_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get AI service statistics"""
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "last_request": self._last_request_time.isoformat() if self._last_request_time else None,
            "deepseek_available": self.deepseek_client is not None
        }
