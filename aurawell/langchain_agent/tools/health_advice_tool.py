"""
LangChain Health Advice Tool

Integrates HealthAdviceService into LangChain agent toolkit.
Provides comprehensive health advice generation as a callable tool.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..services.health_advice_service import HealthAdviceService
from ..services.parsers import HealthAdviceResponse
from .adapter import HealthToolAdapter

logger = logging.getLogger(__name__)


class HealthAdviceTool:
    """
    LangChain tool for generating comprehensive health advice
    
    Integrates the three main tool chains through HealthAdviceService:
    - UserProfileLookup (via UserRepository)
    - CalcMetrics (via health calculations)
    - SearchKnowledge (via DeepSeek AI)
    """
    
    def __init__(self, user_id: str):
        """
        Initialize health advice tool
        
        Args:
            user_id: User identifier for personalized advice
        """
        self.user_id = user_id
        self.service = HealthAdviceService()
        self.logger = logger
        
    async def generate_five_section_advice(
        self,
        goal_type: Optional[str] = None,
        duration_weeks: int = 4,
        special_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive health advice with five required sections
        
        Args:
            goal_type: Health goal (weight_loss, muscle_gain, general_wellness)
            duration_weeks: Planning duration in weeks
            special_requirements: Special health requirements (comma-separated)
            
        Returns:
            Structured health advice with all five modules
        """
        try:
            self.logger.info(f"Generating five-section health advice for user: {self.user_id}")
            
            # Parse special requirements
            requirements_list = []
            if special_requirements:
                requirements_list = [req.strip() for req in special_requirements.split(',')]
            
            # Generate comprehensive advice
            advice_response = await self.service.generate_comprehensive_advice(
                user_id=self.user_id,
                goal_type=goal_type,
                duration_weeks=duration_weeks,
                special_requirements=requirements_list
            )
            
            # Format response for LangChain consumption
            return {
                "success": True,
                "advice": {
                    "diet": {
                        "title": advice_response.diet.title,
                        "content": advice_response.diet.content,
                        "recommendations": advice_response.diet.recommendations
                    },
                    "exercise": {
                        "title": advice_response.exercise.title,
                        "content": advice_response.exercise.content,
                        "recommendations": advice_response.exercise.recommendations
                    },
                    "weight": {
                        "title": advice_response.weight.title,
                        "content": advice_response.weight.content,
                        "recommendations": advice_response.weight.recommendations
                    },
                    "sleep": {
                        "title": advice_response.sleep.title,
                        "content": advice_response.sleep.content,
                        "recommendations": advice_response.sleep.recommendations
                    },
                    "mental_health": {
                        "title": advice_response.mental_health.title,
                        "content": advice_response.mental_health.content,
                        "recommendations": advice_response.mental_health.recommendations
                    }
                },
                "summary": advice_response.summary,
                "generated_at": advice_response.generated_at,
                "user_id": advice_response.user_id,
                "formatted_text": self._format_advice_text(advice_response)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating five-section advice: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "生成健康建议时遇到问题，请稍后重试"
            }
    
    async def generate_quick_topic_advice(self, topic: str) -> Dict[str, Any]:
        """
        Generate quick advice for specific health topic
        
        Args:
            topic: Health topic (diet, exercise, weight, sleep, mental)
            
        Returns:
            Quick advice for the specified topic
        """
        try:
            self.logger.info(f"Generating quick advice for topic: {topic}")
            
            advice_text = await self.service.generate_quick_advice(
                user_id=self.user_id,
                topic=topic
            )
            
            return {
                "success": True,
                "topic": topic,
                "advice": advice_text,
                "user_id": self.user_id,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating quick advice for topic {topic}: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "message": f"生成{topic}建议时遇到问题，请稍后重试"
            }
    
    def _format_advice_text(self, advice_response: HealthAdviceResponse) -> str:
        """
        Format advice response as readable text
        
        Args:
            advice_response: Structured health advice response
            
        Returns:
            Formatted text suitable for display
        """
        formatted_text = f"""
# 个性化健康管理建议

*生成时间：{advice_response.generated_at}*
*用户ID：{advice_response.user_id}*

## 🍎 饮食建议

{advice_response.diet.content}

**核心推荐：**
{self._format_recommendations(advice_response.diet.recommendations)}

## 🏃‍♂️ 运动计划

{advice_response.exercise.content}

**核心推荐：**
{self._format_recommendations(advice_response.exercise.recommendations)}

## ⚖️ 体重管理

{advice_response.weight.content}

**核心推荐：**
{self._format_recommendations(advice_response.weight.recommendations)}

## 😴 睡眠优化

{advice_response.sleep.content}

**核心推荐：**
{self._format_recommendations(advice_response.sleep.recommendations)}

## 🧠 心理健康

{advice_response.mental_health.content}

**核心推荐：**
{self._format_recommendations(advice_response.mental_health.recommendations)}

---

## 📝 总结

{advice_response.summary}

**重要提醒：** 以上建议仅供参考，如有具体健康问题请咨询专业医生。
"""
        return formatted_text
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations list as bullet points"""
        if not recommendations:
            return "• 暂无具体推荐"
        return "\n".join([f"• {rec}" for rec in recommendations])
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get LangChain tool schema for this health advice tool
        
        Returns:
            Tool schema compatible with LangChain
        """
        return {
            "name": "generate_health_advice",
            "description": "生成包含饮食、运动、体重、睡眠、心理健康五个模块的完整健康管理建议",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_type": {
                        "type": "string",
                        "description": "健康目标类型",
                        "enum": ["weight_loss", "muscle_gain", "general_wellness", "endurance", "strength"]
                    },
                    "duration_weeks": {
                        "type": "integer",
                        "description": "计划执行周期（周）",
                        "minimum": 1,
                        "maximum": 52,
                        "default": 4
                    },
                    "special_requirements": {
                        "type": "string", 
                        "description": "特殊健康要求或限制，用逗号分隔"
                    }
                }
            }
        }
    
    def get_quick_advice_schema(self) -> Dict[str, Any]:
        """
        Get schema for quick topic advice tool
        
        Returns:
            Quick advice tool schema
        """
        return {
            "name": "generate_quick_health_advice",
            "description": "为特定健康话题生成快速建议",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "健康话题",
                        "enum": ["diet", "exercise", "weight", "sleep", "mental"]
                    }
                },
                "required": ["topic"]
            }
        }


class HealthAdviceToolAdapter(HealthToolAdapter):
    """
    Adapter to integrate HealthAdviceTool into LangChain Agent toolkit
    """
    
    def __init__(self, user_id: str):
        """
        Initialize the adapter
        
        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        self.health_advice_tool = HealthAdviceTool(user_id)
        
        # Initialize base adapter
        super().__init__(
            name="health_advice_generator",
            description="Comprehensive health advice generator with five modules",
            original_tool=self.health_advice_tool.generate_five_section_advice
        )
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute health advice generation
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Execution result
        """
        try:
            # Extract parameters
            goal_type = kwargs.get("goal_type")
            duration_weeks = kwargs.get("duration_weeks", 4)
            special_requirements = kwargs.get("special_requirements")
            
            # Generate advice
            result = await self.health_advice_tool.generate_five_section_advice(
                goal_type=goal_type,
                duration_weeks=duration_weeks,
                special_requirements=special_requirements
            )
            
            return result
            
        except Exception as e:
            logger.error(f"HealthAdviceToolAdapter execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": self.name
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LangChain"""
        return self.health_advice_tool.get_tool_schema()


# Tool registration for LangChain agent
def register_health_advice_tools(user_id: str, tool_registry) -> None:
    """
    Register health advice tools with the tool registry
    
    Args:
        user_id: User identifier
        tool_registry: LangChain tool registry
    """
    try:
        # Register comprehensive health advice tool
        advice_adapter = HealthAdviceToolAdapter(user_id)
        tool_registry.register_tool(advice_adapter)
        
        # Register quick advice tool
        health_tool = HealthAdviceTool(user_id)
        quick_adapter = HealthToolAdapter(
            name="quick_health_advice",
            description="Quick advice for specific health topics",
            original_tool=health_tool.generate_quick_topic_advice
        )
        tool_registry.register_tool(quick_adapter)
        
        logger.info(f"Registered health advice tools for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to register health advice tools: {e}")
        raise 