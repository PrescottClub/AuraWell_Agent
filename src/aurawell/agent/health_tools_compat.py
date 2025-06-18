"""
健康工具函数兼容性层
为传统的 agent/health_tools.py 导入提供兼容性支持

这个模块确保现有代码可以继续使用传统的导入路径，
同时在后台使用迁移后的LangChain健康工具函数。
"""

import warnings
import logging
from typing import List, Dict, Any

# 导入迁移后的函数
from ..langchain_agent.tools.health_functions import (
    get_user_activity_summary as _new_get_user_activity_summary,
    analyze_sleep_quality as _new_analyze_sleep_quality,
    get_health_insights as _new_get_health_insights,
    update_health_goals as _new_update_health_goals,
    analyze_nutrition_intake as _new_analyze_nutrition_intake,
    get_migration_status,
)

logger = logging.getLogger(__name__)

# 兼容性警告消息
DEPRECATION_WARNING = """
⚠️  DEPRECATION WARNING: 
传统的 agent/health_tools.py 已被弃用。
请更新您的代码以使用新的 langchain_agent/tools/health_functions.py

迁移指南:
- 旧: from aurawell.agent.health_tools import get_user_activity_summary
- 新: from aurawell.langchain_agent.tools.health_functions import get_user_activity_summary

或使用适配器:
- from aurawell.langchain_agent.tools.health_functions_adapter import get_health_functions_adapter

此兼容性层将在未来版本中移除。
"""


def _show_deprecation_warning(function_name: str):
    """显示弃用警告"""
    warnings.warn(
        f"函数 '{function_name}' 已从传统 agent/health_tools.py 迁移到 langchain_agent/tools/。"
        f"请更新您的导入路径。{DEPRECATION_WARNING}",
        DeprecationWarning,
        stacklevel=3
    )
    logger.warning(f"使用了已弃用的函数: {function_name}")


# ============================================================================
# 兼容性函数包装器
# ============================================================================

async def get_user_activity_summary(user_id: str, days: int = 7) -> List[dict]:
    """
    获取用户活动摘要 - 兼容性包装器
    
    ⚠️ DEPRECATED: 请使用 langchain_agent.tools.health_functions.get_user_activity_summary
    """
    _show_deprecation_warning("get_user_activity_summary")
    return await _new_get_user_activity_summary(user_id, days)


async def analyze_sleep_quality(user_id: str, date_range: str) -> List[dict]:
    """
    分析睡眠质量 - 兼容性包装器
    
    ⚠️ DEPRECATED: 请使用 langchain_agent.tools.health_functions.analyze_sleep_quality
    """
    _show_deprecation_warning("analyze_sleep_quality")
    return await _new_analyze_sleep_quality(user_id, date_range)


async def get_health_insights(user_id: str) -> List[dict]:
    """
    获取健康洞察 - 兼容性包装器
    
    ⚠️ DEPRECATED: 请使用 langchain_agent.tools.health_functions.get_health_insights
    """
    _show_deprecation_warning("get_health_insights")
    return await _new_get_health_insights(user_id)


async def update_health_goals(user_id: str, goals: dict) -> dict:
    """
    更新健康目标 - 兼容性包装器
    
    ⚠️ DEPRECATED: 请使用 langchain_agent.tools.health_functions.update_health_goals
    """
    _show_deprecation_warning("update_health_goals")
    return await _new_update_health_goals(user_id, goals)


async def analyze_nutrition_intake(user_id: str, date_range: str = "7_days") -> dict:
    """
    分析营养摄入 - 兼容性包装器
    
    ⚠️ DEPRECATED: 请使用 langchain_agent.tools.health_functions.analyze_nutrition_intake
    """
    _show_deprecation_warning("analyze_nutrition_intake")
    return await _new_analyze_nutrition_intake(user_id, date_range)


# ============================================================================
# 模拟传统函数（尚未迁移的函数）
# ============================================================================

async def generate_exercise_plan(user_id: str, goal_type: str = "general_fitness", duration_weeks: int = 4) -> dict:
    """
    生成运动计划 - 模拟实现
    
    ⚠️ DEPRECATED: 此函数尚未完全迁移，返回模拟数据
    """
    _show_deprecation_warning("generate_exercise_plan")
    
    logger.info(f"[COMPAT] Generating exercise plan for user {user_id}")
    
    return {
        "success": True,
        "plan_type": goal_type,
        "duration_weeks": duration_weeks,
        "exercises": [
            {
                "name": "快走",
                "type": "有氧运动",
                "duration_minutes": 30,
                "frequency_per_week": 5,
                "intensity": "中等",
            },
            {
                "name": "俯卧撑",
                "type": "力量训练",
                "sets": 3,
                "reps": 10,
                "frequency_per_week": 3,
                "intensity": "中等",
            },
        ],
        "note": "这是兼容性模拟数据，请迁移到新的工具函数",
    }


async def generate_health_report(user_id: str, report_type: str = "weekly") -> dict:
    """
    生成健康报告 - 模拟实现
    
    ⚠️ DEPRECATED: 此函数尚未完全迁移，返回模拟数据
    """
    _show_deprecation_warning("generate_health_report")
    
    logger.info(f"[COMPAT] Generating health report for user {user_id}")
    
    return {
        "success": True,
        "report_type": report_type,
        "generated_at": "2025-01-17T10:30:00",
        "summary": "本周健康状况良好，建议继续保持当前的运动和饮食习惯。",
        "metrics": {
            "avg_steps": 8500,
            "avg_sleep_hours": 7.2,
            "exercise_sessions": 4,
        },
        "note": "这是兼容性模拟数据，请迁移到新的工具函数",
    }


async def manage_weight_goals(user_id: str, action: str, goal_data: dict = None) -> dict:
    """
    管理体重目标 - 模拟实现
    
    ⚠️ DEPRECATED: 此函数尚未完全迁移，返回模拟数据
    """
    _show_deprecation_warning("manage_weight_goals")
    
    logger.info(f"[COMPAT] Managing weight goals for user {user_id}, action: {action}")
    
    return {
        "success": True,
        "action": action,
        "current_weight": 65.0,
        "target_weight": 60.0,
        "progress": "正在进行中",
        "note": "这是兼容性模拟数据，请迁移到新的工具函数",
    }


# ============================================================================
# 兼容性信息和迁移帮助
# ============================================================================

def get_compatibility_info() -> Dict[str, Any]:
    """
    获取兼容性层信息
    
    Returns:
        兼容性层状态和迁移信息
    """
    migration_status = get_migration_status()
    
    return {
        "compatibility_layer_version": "1.0.0",
        "status": "active",
        "warning": "此兼容性层将在未来版本中移除",
        "migration_status": migration_status,
        "migrated_functions": [
            "get_user_activity_summary",
            "analyze_sleep_quality", 
            "get_health_insights",
            "update_health_goals",
            "analyze_nutrition_intake",
        ],
        "simulated_functions": [
            "generate_exercise_plan",
            "generate_health_report",
            "manage_weight_goals",
        ],
        "migration_guide": {
            "old_import": "from aurawell.agent.health_tools import get_user_activity_summary",
            "new_import": "from aurawell.langchain_agent.tools.health_functions import get_user_activity_summary",
            "adapter_import": "from aurawell.langchain_agent.tools.health_functions_adapter import get_health_functions_adapter",
        },
    }


def show_migration_guide():
    """显示迁移指南"""
    print("=" * 80)
    print("🔄 AuraWell Agent 健康工具函数迁移指南")
    print("=" * 80)
    print()
    print("📋 迁移状态:")
    
    info = get_compatibility_info()
    migration_status = info["migration_status"]
    
    print(f"   版本: {migration_status['version']}")
    print(f"   进度: {migration_status.get('migration_progress', 'N/A')}")
    print(f"   日期: {migration_status['migration_date']}")
    print()
    
    print("✅ 已迁移函数:")
    for func in info["migrated_functions"]:
        print(f"   - {func}")
    print()
    
    print("🔄 模拟函数 (待完全迁移):")
    for func in info["simulated_functions"]:
        print(f"   - {func}")
    print()
    
    print("📖 迁移示例:")
    print("   旧代码:")
    print(f"     {info['migration_guide']['old_import']}")
    print("   新代码:")
    print(f"     {info['migration_guide']['new_import']}")
    print("   或使用适配器:")
    print(f"     {info['migration_guide']['adapter_import']}")
    print()
    
    print("⚠️  重要提醒:")
    print("   - 此兼容性层将在未来版本中移除")
    print("   - 请尽快更新您的代码以使用新的导入路径")
    print("   - 新的工具函数提供更好的性能和功能")
    print("=" * 80)


# 模块级别的兼容性检查
def _check_compatibility():
    """模块加载时的兼容性检查"""
    logger.info("加载健康工具函数兼容性层")
    logger.warning("传统 agent/health_tools.py 已被弃用，请迁移到新的 langchain_agent/tools/")


# 在模块加载时执行兼容性检查
_check_compatibility()
