"""
AuraWell健康工具集合 - 兼容性重定向到核心模块

此文件现在重定向到统一的核心健康工具模块 (core.health_tools)
认知核心优化后，所有健康工具功能已整合到单一核心模块中。

新的导入路径：
推荐: from aurawell.core.health_tools import get_user_activity_summary
兼容: from aurawell.agent.health_tools import get_user_activity_summary

版本: 2.0.0 (认知核心优化版本)
"""

# 重定向到统一核心模块
from ..core.health_tools import (
    get_user_activity_summary,
    analyze_sleep_quality,
    get_health_insights,
    update_health_goals,
    analyze_nutrition_intake,
    generate_exercise_plan,
    check_achievements,
    get_available_health_functions,
    get_health_function,
    get_core_module_info,
)

from typing import Dict, Any
import warnings
import logging

logger = logging.getLogger(__name__)

# 显示优化信息
logger.info("✅ 健康工具已优化：使用统一核心模块 (core.health_tools)")

# 兼容性函数
def get_compatibility_info() -> Dict[str, Any]:
    """获取兼容性信息"""
    core_info = get_core_module_info()
    return {
        "status": "optimized",
        "version": "2.0.0",
        "optimization": "认知核心优化完成",
        "core_module": core_info,
        "migration_message": "所有健康工具已整合到 core.health_tools 模块",
        "benefits": [
            "消除认知冗余",
            "统一API接口",
            "提升性能",
            "简化维护",
            "保持完整兼容性",
        ],
        "available_functions": list(get_available_health_functions().keys()),
    }


def show_migration_guide():
    """显示迁移指南"""
    info = get_compatibility_info()

    print("=" * 80)
    print("🎯 AuraWell 健康工具认知核心优化完成")
    print("=" * 80)
    print(f"📊 状态: {info['status']}")
    print(f"🔄 版本: {info['version']}")
    print(f"✨ 优化: {info['optimization']}")
    print()

    print("🚀 优化收益:")
    for benefit in info['benefits']:
        print(f"   ✅ {benefit}")
    print()

    print("📖 新的推荐导入方式:")
    print("   from aurawell.core.health_tools import get_user_activity_summary")
    print()

    print("🔧 可用功能:")
    for func in info['available_functions']:
        print(f"   • {func}")
    print()

    print("💡 提示: 现有代码无需修改，兼容性已完全保证")
    print("=" * 80)


# 模拟已移除的函数（为了兼容性）
async def generate_health_report(user_id: str) -> dict:
    """生成健康报告 - 重定向到核心洞察功能"""
    logger.info(f"generate_health_report 已重定向到 get_health_insights")
    insights = await get_health_insights(user_id)
    return {
        "status": "success",
        "user_id": user_id,
        "report_type": "health_insights",
        "insights": insights,
        "message": "健康报告已生成（基于健康洞察）",
    }


async def manage_weight_goals(user_id: str, action: str, **kwargs) -> dict:
    """体重目标管理 - 重定向到核心目标功能"""
    logger.info(f"manage_weight_goals 已重定向到 update_health_goals")

    if action == "set" and "weight_target" in kwargs:
        goals = {"weight_target": kwargs["weight_target"]}
        if "target_date" in kwargs:
            goals["target_date"] = kwargs["target_date"]
        return await update_health_goals(user_id, goals)
    else:
        return {
            "status": "error",
            "message": "Invalid action or missing weight_target",
            "available_actions": ["set"],
        }


__all__ = [
    # 核心健康工具函数
    "get_user_activity_summary",
    "analyze_sleep_quality",
    "get_health_insights",
    "update_health_goals",
    "analyze_nutrition_intake",
    "generate_exercise_plan",
    "check_achievements",

    # 兼容性函数
    "generate_health_report",
    "manage_weight_goals",
    "get_compatibility_info",
    "show_migration_guide",

    # 工具管理函数
    "get_available_health_functions",
    "get_health_function",
    "get_core_module_info",
]