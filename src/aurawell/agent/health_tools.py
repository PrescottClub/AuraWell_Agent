"""
⚠️ DEPRECATED: AuraWell健康工具集合 - 兼容性重定向

此文件已被弃用，所有功能已迁移到 langchain_agent/tools/health_functions.py
为了保持向后兼容性，此文件现在重定向到兼容性层。

请更新您的代码以使用新的导入路径：
旧: from aurawell.agent.health_tools import get_user_activity_summary
新: from aurawell.langchain_agent.tools.health_functions import get_user_activity_summary

此兼容性层将在未来版本中移除。
"""

# 重定向到兼容性层
from .health_tools_compat import (
    get_user_activity_summary,
    analyze_sleep_quality,
    get_health_insights,
    update_health_goals,
    analyze_nutrition_intake,
    generate_exercise_plan,
    generate_health_report,
    manage_weight_goals,
    get_compatibility_info,
    show_migration_guide,
)

from typing import Dict, Any
import warnings

# 显示弃用警告
warnings.warn(
    "agent.health_tools 已被弃用，请使用 langchain_agent.tools.health_functions",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "get_user_activity_summary",
    "analyze_sleep_quality",
    "get_health_insights",
    "update_health_goals",
    "analyze_nutrition_intake",
    "generate_exercise_plan",
    "generate_health_report",
    "manage_weight_goals",
    "get_compatibility_info",
    "show_migration_guide",
] 