"""
LangChain 健康工具适配器
将现有的健康工具适配到LangChain框架
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .adapter import HealthToolAdapter, tool_registry
# 注意：这里我们将使用现有的健康工具函数，而不是HealthTools类
from ...agent import health_tools

logger = logging.getLogger(__name__)


class LangChainHealthTools:
    """
    LangChain 健康工具集合
    将现有的健康工具适配到LangChain框架
    """
    
    def __init__(self, user_id: str):
        """
        初始化LangChain健康工具

        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        # 使用现有的健康工具函数，而不是类实例
        self._register_tools()
    
    def _register_tools(self) -> None:
        """注册所有健康工具到LangChain适配器"""

        # 注册用户活动摘要工具
        activity_adapter = HealthToolAdapter(
            name="get_user_activity_summary",
            description="获取用户活动摘要数据",
            original_tool=health_tools.get_user_activity_summary
        )
        tool_registry.register_tool(activity_adapter)

        # 注册睡眠质量分析工具
        sleep_adapter = HealthToolAdapter(
            name="analyze_sleep_quality",
            description="分析用户睡眠质量",
            original_tool=health_tools.analyze_sleep_quality
        )
        tool_registry.register_tool(sleep_adapter)

        # 注册健康洞察工具
        insights_adapter = HealthToolAdapter(
            name="get_health_insights",
            description="获取个性化健康洞察",
            original_tool=health_tools.get_health_insights
        )
        tool_registry.register_tool(insights_adapter)

        # 注册营养建议工具
        nutrition_adapter = HealthToolAdapter(
            name="get_nutrition_recommendations",
            description="获取营养建议",
            original_tool=health_tools.get_nutrition_recommendations
        )
        tool_registry.register_tool(nutrition_adapter)

        # 注册运动计划工具
        exercise_adapter = HealthToolAdapter(
            name="create_exercise_plan",
            description="创建个性化运动计划",
            original_tool=health_tools.create_exercise_plan
        )
        tool_registry.register_tool(exercise_adapter)
        
        logger.info(f"为用户 {self.user_id} 注册了 {len(tool_registry.get_all_tools())} 个健康工具")
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        获取可用的健康工具列表
        
        Returns:
            List[Dict[str, Any]]: 工具信息列表
        """
        tools = []
        for tool in tool_registry.get_all_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "schema": tool.get_schema()
            })
        return tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        执行健康工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        return await tool_registry.execute_tool(tool_name, **kwargs)
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """
        获取用户健康数据摘要
        
        Returns:
            Dict[str, Any]: 健康数据摘要
        """
        try:
            # 获取最近的健康数据
            recent_data = await self.execute_tool(
                "query_health_data",
                data_type="all",
                start_date=(datetime.now() - timedelta(days=7)).isoformat(),
                end_date=datetime.now().isoformat()
            )
            
            # 获取健康建议
            advice = await self.execute_tool("get_health_advice")
            
            return {
                "success": True,
                "summary": {
                    "recent_data": recent_data.get("result", {}),
                    "health_advice": advice.get("result", {}),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"获取健康摘要失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取健康摘要失败"
            }
    
    async def analyze_health_trend(self, data_type: str, days: int = 30) -> Dict[str, Any]:
        """
        分析健康数据趋势
        
        Args:
            data_type: 数据类型（weight, blood_pressure, heart_rate等）
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        try:
            # 获取历史数据
            historical_data = await self.execute_tool(
                "query_health_data",
                data_type=data_type,
                start_date=(datetime.now() - timedelta(days=days)).isoformat(),
                end_date=datetime.now().isoformat()
            )
            
            if not historical_data.get("success"):
                return historical_data
            
            data_points = historical_data.get("result", {}).get("data", [])
            
            if len(data_points) < 2:
                return {
                    "success": True,
                    "trend": "insufficient_data",
                    "message": "数据点不足，无法分析趋势"
                }
            
            # 简单趋势分析
            values = [point.get("value", 0) for point in data_points if point.get("value")]
            if not values:
                return {
                    "success": True,
                    "trend": "no_data",
                    "message": "没有有效的数据值"
                }
            
            # 计算趋势
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first * 1.05:
                trend = "increasing"
            elif avg_second < avg_first * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                "success": True,
                "trend": trend,
                "data_type": data_type,
                "period_days": days,
                "data_points_count": len(data_points),
                "average_first_half": avg_first,
                "average_second_half": avg_second,
                "change_percentage": ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"分析健康趋势失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "分析健康趋势失败"
            }
