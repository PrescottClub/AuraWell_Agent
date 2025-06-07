from typing import List, Dict, Callable

# 导入健康工具函数
from aurawell.agent import health_tools

class HealthToolsRegistry:
    """健康工具注册中心，基于现有功能封装"""
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        # schema现在存储完整的工具定义
        self.tool_schemas: List[dict] = []
        self._register_default_tools()
    
    def register_tool(self, name: str, func: Callable, schema: dict):
        """注册新工具"""
        self.tools[name] = func
        # 我们将完整的 "function" schema 存起来给AI
        self.tool_schemas.append(schema)
    
    def get_tool(self, name: str) -> Callable:
        """获取工具函数"""
        return self.tools.get(name)
    
    def get_tools_schema(self) -> List[dict]:
        """获取所有工具的OpenAI Function Calling schema"""
        return self.tool_schemas

    def _register_default_tools(self):
        """注册默认的工具集"""
        # 1. 获取用户活动摘要
        self.register_tool(
            name="get_user_activity_summary",
            func=health_tools.get_user_activity_summary,
            schema={
                "type": "function",
                "function": {
                    "name": "get_user_activity_summary",
                    "description": "获取用户在指定天数内的活动摘要",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"},
                            "days": {"type": "integer", "description": "要查询的过去天数，默认为7天"}
                        },
                        "required": ["user_id"]
                    }
                }
            }
        )

        # 2. 分析睡眠质量
        self.register_tool(
            name="analyze_sleep_quality",
            func=health_tools.analyze_sleep_quality,
            schema={
                "type": "function",
                "function": {
                    "name": "analyze_sleep_quality",
                    "description": "分析用户在指定日期范围内的睡眠质量",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"},
                            "date_range": {"type": "string", "description": "日期范围，例如 '2024-05-01_to_2024-05-31'"}
                        },
                        "required": ["user_id", "date_range"]
                    }
                }
            }
        )

        # 3. 获取健康洞察
        self.register_tool(
            name="get_health_insights",
            func=health_tools.get_health_insights,
            schema={
                "type": "function",
                "function": {
                    "name": "get_health_insights",
                    "description": "基于用户的整体数据生成健康洞察和建议",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"}
                        },
                        "required": ["user_id"]
                    }
                }
            }
        )

        # 4. 更新健康目标
        self.register_tool(
            name="update_health_goals",
            func=health_tools.update_health_goals,
            schema={
                "type": "function",
                "function": {
                    "name": "update_health_goals",
                    "description": "为用户更新或设置新的健康目标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"},
                            "goals": {
                                "type": "object",
                                "description": "一个包含健康目标的字典，例如 {'daily_steps': 10000, 'sleep_hours': 7.5}"
                            }
                        },
                        "required": ["user_id", "goals"]
                    }
                }
            }
        )

        # 5. 检查成就进度
        self.register_tool(
            name="check_achievements",
            func=health_tools.check_achievements,
            schema={
                "type": "function",
                "function": {
                    "name": "check_achievements",
                    "description": "检查用户已解锁的成就和当前进度",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"}
                        },
                        "required": ["user_id"]
                    }
                }
            }
        ) 