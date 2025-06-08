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

    async def call_tool(self, tool_name: str, parameters: dict):
        """
        调用指定的工具

        Args:
            tool_name: 工具名称
            parameters: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool_func = self.tools[tool_name]

        try:
            # 调用工具函数
            result = await tool_func(**parameters)
            return result
        except Exception as e:
            import logging
            logging.exception(f"An error occurred while executing tool '{tool_name}': {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed to execute tool '{tool_name}'"
            }

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

        # 6. 营养分析工具
        self.register_tool(
            name="analyze_nutrition_intake",
            func=health_tools.analyze_nutrition_intake,
            schema={
                "type": "function",
                "function": {
                    "name": "analyze_nutrition_intake",
                    "description": "分析用户的营养摄入情况，提供营养评估和建议",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"},
                            "date": {"type": "string", "description": "分析日期，格式为 YYYY-MM-DD"},
                            "meals": {
                                "type": "array",
                                "description": "餐食列表",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "meal_type": {"type": "string", "description": "餐食类型，如 breakfast, lunch, dinner"},
                                        "foods": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {"type": "string", "description": "食物名称"},
                                                    "amount": {"type": "number", "description": "食物数量"},
                                                    "unit": {"type": "string", "description": "单位，如 g, kg, 个"}
                                                },
                                                "required": ["name", "amount", "unit"]
                                            }
                                        }
                                    },
                                    "required": ["meal_type", "foods"]
                                }
                            }
                        },
                        "required": ["user_id", "date", "meals"]
                    }
                }
            }
        )

        # 7. 运动计划生成工具
        self.register_tool(
            name="generate_exercise_plan",
            func=health_tools.generate_exercise_plan,
            schema={
                "type": "function",
                "function": {
                    "name": "generate_exercise_plan",
                    "description": "基于用户目标生成个性化运动计划",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"},
                            "goal_type": {
                                "type": "string",
                                "description": "运动目标类型",
                                "enum": ["weight_loss", "muscle_gain", "endurance", "general_fitness"]
                            },
                            "duration_weeks": {
                                "type": "integer",
                                "description": "计划持续周数，默认4周",
                                "minimum": 1,
                                "maximum": 52
                            },
                            "fitness_level": {
                                "type": "string",
                                "description": "健身水平",
                                "enum": ["beginner", "intermediate", "advanced"]
                            }
                        },
                        "required": ["user_id", "goal_type"]
                    }
                }
            }
        )

        # 8. 健康报告生成工具
        self.register_tool(
            name="generate_health_report",
            func=health_tools.generate_health_report,
            schema={
                "type": "function",
                "function": {
                    "name": "generate_health_report",
                    "description": "生成综合健康分析报告",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"},
                            "report_type": {
                                "type": "string",
                                "description": "报告类型",
                                "enum": ["comprehensive", "activity", "sleep", "nutrition"],
                                "default": "comprehensive"
                            },
                            "period_days": {
                                "type": "integer",
                                "description": "分析周期天数，默认30天",
                                "minimum": 7,
                                "maximum": 365,
                                "default": 30
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            }
        )

        # 9. 体重管理工具
        self.register_tool(
            name="track_weight_progress",
            func=health_tools.track_weight_progress,
            schema={
                "type": "function",
                "function": {
                    "name": "track_weight_progress",
                    "description": "追踪体重变化和进度，提供体重管理建议",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "用户的唯一标识符"},
                            "current_weight": {
                                "type": "number",
                                "description": "当前体重(kg)",
                                "minimum": 30,
                                "maximum": 300
                            },
                            "target_weight": {
                                "type": "number",
                                "description": "目标体重(kg)，可选",
                                "minimum": 30,
                                "maximum": 300
                            },
                            "period_days": {
                                "type": "integer",
                                "description": "分析周期天数，默认90天",
                                "minimum": 7,
                                "maximum": 365,
                                "default": 90
                            }
                        },
                        "required": ["user_id", "current_weight"]
                    }
                }
            }
        )