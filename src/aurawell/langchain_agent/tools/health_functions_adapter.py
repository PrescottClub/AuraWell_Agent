"""
健康工具函数适配器
将迁移后的健康工具函数适配到LangChain Agent中，提供统一的调用接口
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .health_functions import (
    get_user_activity_summary,
    analyze_sleep_quality,
    get_health_insights,
    update_health_goals,
    analyze_nutrition_intake,
    get_available_health_functions,
    get_health_function,
    get_migration_status,
)

logger = logging.getLogger(__name__)


class HealthFunctionsAdapter:
    """
    健康工具函数适配器
    
    为LangChain Agent提供统一的健康工具函数调用接口，
    支持函数发现、参数验证、错误处理等功能。
    """

    def __init__(self, user_id: str):
        """
        初始化适配器
        
        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.logger = logger
        self._available_functions = get_available_health_functions()
        
        self.logger.info(f"HealthFunctionsAdapter initialized for user: {user_id}")
        self.logger.info(f"Available functions: {list(self._available_functions.keys())}")

    async def call_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        调用健康工具函数
        
        Args:
            function_name: 函数名称
            **kwargs: 函数参数
            
        Returns:
            函数执行结果
        """
        try:
            # 检查函数是否存在
            if function_name not in self._available_functions:
                return {
                    "success": False,
                    "error": f"Function '{function_name}' not found",
                    "available_functions": list(self._available_functions.keys()),
                }

            # 获取函数
            func = self._available_functions[function_name]
            
            # 添加user_id参数（如果函数需要）
            if "user_id" in func.__code__.co_varnames:
                kwargs["user_id"] = self.user_id

            self.logger.info(f"Calling function: {function_name} with args: {kwargs}")

            # 调用函数
            result = await func(**kwargs)
            
            # 包装结果
            return {
                "success": True,
                "function_name": function_name,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "user_id": self.user_id,
            }

        except Exception as e:
            self.logger.error(f"Error calling function {function_name}: {e}")
            return {
                "success": False,
                "function_name": function_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "user_id": self.user_id,
            }

    async def get_user_activity_summary(self, days: int = 7) -> Dict[str, Any]:
        """获取用户活动摘要"""
        return await self.call_function("get_user_activity_summary", days=days)

    async def analyze_sleep_quality(self, date_range: str) -> Dict[str, Any]:
        """分析睡眠质量"""
        return await self.call_function("analyze_sleep_quality", date_range=date_range)

    async def get_health_insights(self) -> Dict[str, Any]:
        """获取健康洞察"""
        return await self.call_function("get_health_insights")

    async def update_health_goals(self, goals: dict) -> Dict[str, Any]:
        """更新健康目标"""
        return await self.call_function("update_health_goals", goals=goals)

    async def analyze_nutrition_intake(self, date_range: str = "7_days") -> Dict[str, Any]:
        """分析营养摄入"""
        return await self.call_function("analyze_nutrition_intake", date_range=date_range)

    def get_available_functions(self) -> List[str]:
        """获取可用函数列表"""
        return list(self._available_functions.keys())

    def get_function_info(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        获取函数信息
        
        Args:
            function_name: 函数名称
            
        Returns:
            函数信息字典
        """
        if function_name not in self._available_functions:
            return None

        func = self._available_functions[function_name]
        
        return {
            "name": function_name,
            "doc": func.__doc__,
            "parameters": list(func.__code__.co_varnames),
            "module": func.__module__,
        }

    def get_migration_info(self) -> Dict[str, Any]:
        """获取迁移状态信息"""
        return get_migration_status()

    async def health_summary(self) -> Dict[str, Any]:
        """
        获取用户健康数据综合摘要
        
        Returns:
            包含多个健康指标的综合摘要
        """
        try:
            # 并行获取多个健康数据
            activity_result = await self.get_user_activity_summary(days=7)
            sleep_result = await self.analyze_sleep_quality("7_days")
            insights_result = await self.get_health_insights()
            nutrition_result = await self.analyze_nutrition_intake("7_days")

            return {
                "success": True,
                "summary_type": "comprehensive",
                "user_id": self.user_id,
                "generated_at": datetime.now().isoformat(),
                "data": {
                    "activity": activity_result.get("result", []),
                    "sleep": sleep_result.get("result", []),
                    "insights": insights_result.get("result", []),
                    "nutrition": nutrition_result.get("result", {}),
                },
                "data_quality": {
                    "activity_available": activity_result.get("success", False),
                    "sleep_available": sleep_result.get("success", False),
                    "insights_available": insights_result.get("success", False),
                    "nutrition_available": nutrition_result.get("success", False),
                },
            }

        except Exception as e:
            self.logger.error(f"Error generating health summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "生成健康摘要失败",
                "user_id": self.user_id,
            }

    async def quick_health_check(self) -> Dict[str, Any]:
        """
        快速健康检查
        
        Returns:
            简化的健康状态检查结果
        """
        try:
            # 获取基础健康洞察
            insights_result = await self.get_health_insights()
            
            if not insights_result.get("success"):
                return {
                    "success": False,
                    "message": "无法获取健康数据",
                    "user_id": self.user_id,
                }

            insights = insights_result.get("result", [])
            
            # 分析健康状态
            high_priority_issues = [
                insight for insight in insights 
                if insight.get("priority") == "high" and insight.get("action_required")
            ]
            
            achievements = [
                insight for insight in insights 
                if insight.get("type") == "achievement"
            ]

            return {
                "success": True,
                "health_status": "good" if not high_priority_issues else "needs_attention",
                "summary": {
                    "total_insights": len(insights),
                    "high_priority_issues": len(high_priority_issues),
                    "achievements": len(achievements),
                },
                "urgent_actions": high_priority_issues[:3],  # 最多3个紧急事项
                "recent_achievements": achievements[:2],  # 最多2个成就
                "user_id": self.user_id,
                "checked_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error in quick health check: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "快速健康检查失败",
                "user_id": self.user_id,
            }

    def get_adapter_info(self) -> Dict[str, Any]:
        """获取适配器信息"""
        migration_info = self.get_migration_info()
        
        return {
            "adapter_version": "1.0.0",
            "user_id": self.user_id,
            "available_functions": len(self._available_functions),
            "migration_status": migration_info,
            "features": [
                "function_discovery",
                "parameter_validation", 
                "error_handling",
                "health_summary",
                "quick_health_check",
            ],
        }


# 全局适配器实例缓存
_adapter_cache = {}


def get_health_functions_adapter(user_id: str) -> HealthFunctionsAdapter:
    """
    获取健康工具函数适配器实例（单例模式）
    
    Args:
        user_id: 用户ID
        
    Returns:
        HealthFunctionsAdapter实例
    """
    if user_id not in _adapter_cache:
        _adapter_cache[user_id] = HealthFunctionsAdapter(user_id)
        logger.info(f"Created new HealthFunctionsAdapter for user: {user_id}")
    
    return _adapter_cache[user_id]


def clear_adapter_cache(user_id: Optional[str] = None):
    """
    清除适配器缓存
    
    Args:
        user_id: 用户ID，如果为None则清除所有缓存
    """
    global _adapter_cache
    
    if user_id:
        if user_id in _adapter_cache:
            del _adapter_cache[user_id]
            logger.info(f"Cleared adapter cache for user: {user_id}")
    else:
        _adapter_cache.clear()
        logger.info("Cleared all adapter cache")
