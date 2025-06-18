"""
健康工具辅助函数模块

包含健康工具所需的各种辅助函数和数据处理逻辑。
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


def _personalize_exercise_plan(
    base_plan: dict, user_profile, current_activity_level: str
) -> dict:
    """个性化调整运动计划"""
    personalized_plan = base_plan.copy()

    # 根据用户年龄调整
    if user_profile and user_profile.age:
        if user_profile.age > 50:
            # 50岁以上用户减少强度
            for week in personalized_plan["weekly_schedule"]:
                week["cardio_duration"] = int(week["cardio_duration"] * 0.8)
                week["strength_duration"] = int(week["strength_duration"] * 0.8)
        elif user_profile.age < 25:
            # 年轻用户可以增加强度
            for week in personalized_plan["weekly_schedule"]:
                week["cardio_duration"] = int(week["cardio_duration"] * 1.1)
                week["strength_duration"] = int(week["strength_duration"] * 1.1)

    # 根据当前活动水平调整
    activity_adjustments = {
        "inactive": 0.6,
        "lightly_active": 0.8,
        "moderately_active": 1.0,
        "very_active": 1.2,
    }

    adjustment = activity_adjustments.get(current_activity_level, 1.0)
    for week in personalized_plan["weekly_schedule"]:
        week["cardio_duration"] = int(week["cardio_duration"] * adjustment)
        week["strength_duration"] = int(week["strength_duration"] * adjustment)

    return personalized_plan


def _calculate_expected_results(
    goal_type: str, duration_weeks: int, fitness_level: str, user_profile
) -> dict:
    """计算预期运动效果"""
    results = {}

    # 基础预期效果
    if goal_type == "weight_loss":
        # 预期每周减重0.5-1kg
        expected_weight_loss = duration_weeks * 0.75
        results["weight_change_kg"] = f"-{expected_weight_loss:.1f}"
        results["body_fat_reduction"] = f"{duration_weeks * 0.5:.1f}%"
        results["fitness_improvement"] = "中等"

    elif goal_type == "muscle_gain":
        # 预期每周增肌0.1-0.3kg
        expected_muscle_gain = duration_weeks * 0.2
        results["muscle_gain_kg"] = f"+{expected_muscle_gain:.1f}"
        results["strength_increase"] = f"{duration_weeks * 5:.0f}%"
        results["fitness_improvement"] = "显著"

    elif goal_type == "endurance":
        results["cardio_improvement"] = f"{duration_weeks * 10:.0f}%"
        results["resting_heart_rate"] = f"-{duration_weeks * 2:.0f} bpm"
        results["fitness_improvement"] = "显著"

    else:  # general_fitness
        results["overall_fitness"] = f"{duration_weeks * 8:.0f}%"
        results["energy_level"] = "显著提升"
        results["fitness_improvement"] = "良好"

    # 根据健身水平调整
    level_multipliers = {
        "beginner": 1.2,  # 初学者效果更明显
        "intermediate": 1.0,
        "advanced": 0.8,  # 高级者改善空间较小
    }

    multiplier = level_multipliers[fitness_level]

    # 调整数值结果
    for key, value in results.items():
        if isinstance(value, str) and any(char.isdigit() for char in value):
            try:
                # 提取数字并调整
                import re

                numbers = re.findall(r"-?\d+\.?\d*", value)
                if numbers:
                    original_num = float(numbers[0])
                    adjusted_num = original_num * multiplier
                    results[key] = value.replace(numbers[0], f"{adjusted_num:.1f}")
            except:
                pass

    return results


def _get_tracking_metrics(goal_type: str) -> List[dict]:
    """获取追踪指标"""
    base_metrics = [
        {"name": "体重", "unit": "kg", "frequency": "每周"},
        {"name": "运动时长", "unit": "分钟", "frequency": "每次"},
        {"name": "心率", "unit": "bpm", "frequency": "运动中"},
    ]

    goal_specific_metrics = {
        "weight_loss": [
            {"name": "体脂率", "unit": "%", "frequency": "每两周"},
            {"name": "腰围", "unit": "cm", "frequency": "每周"},
            {"name": "卡路里消耗", "unit": "kcal", "frequency": "每次"},
        ],
        "muscle_gain": [
            {"name": "肌肉量", "unit": "kg", "frequency": "每两周"},
            {"name": "力量指标", "unit": "kg", "frequency": "每周"},
            {"name": "蛋白质摄入", "unit": "g", "frequency": "每日"},
        ],
        "endurance": [
            {"name": "最大心率", "unit": "bpm", "frequency": "每月"},
            {"name": "恢复心率", "unit": "bpm", "frequency": "每次"},
            {"name": "运动距离", "unit": "km", "frequency": "每次"},
        ],
        "general_fitness": [
            {"name": "柔韧性", "unit": "cm", "frequency": "每两周"},
            {"name": "平衡能力", "unit": "秒", "frequency": "每周"},
            {"name": "睡眠质量", "unit": "分", "frequency": "每日"},
        ],
    }

    return base_metrics + goal_specific_metrics.get(goal_type, [])


def _get_safety_guidelines(fitness_level: str) -> List[str]:
    """获取安全指导"""
    base_guidelines = [
        "运动前进行5-10分钟热身",
        "运动后进行5-10分钟拉伸",
        "保持充足的水分补充",
        "如感到不适立即停止运动",
        "循序渐进，避免过度训练",
    ]

    level_specific = {
        "beginner": [
            "从低强度开始，逐步增加",
            "重点学习正确的动作姿势",
            "每周至少休息2天",
            "考虑寻求专业指导",
        ],
        "intermediate": [
            "注意动作质量胜过数量",
            "定期评估和调整计划",
            "注意身体信号，适时休息",
        ],
        "advanced": ["注意预防运动损伤", "定期进行功能性评估", "平衡训练强度和恢复"],
    }

    return base_guidelines + level_specific.get(fitness_level, [])


def _get_exercise_library(goal_type: str, fitness_level: str) -> dict:
    """获取运动库"""

    # 基础运动库
    cardio_exercises = {
        "beginner": ["快走", "慢跑", "游泳", "骑行", "椭圆机"],
        "intermediate": ["跑步", "游泳", "骑行", "跳绳", "有氧操"],
        "advanced": ["高强度间歇跑", "游泳", "骑行", "拳击", "综合训练"],
    }

    strength_exercises = {
        "beginner": ["俯卧撑", "深蹲", "平板支撑", "哑铃训练", "阻力带训练"],
        "intermediate": ["杠铃训练", "哑铃训练", "器械训练", "功能性训练", "核心训练"],
        "advanced": [
            "复合动作",
            "爆发力训练",
            "功能性训练",
            "专项训练",
            "高级核心训练",
        ],
    }

    flexibility_exercises = ["静态拉伸", "动态拉伸", "瑜伽", "普拉提", "泡沫轴放松"]

    # 根据目标调整
    goal_adjustments = {
        "weight_loss": {
            "cardio_focus": True,
            "recommended_cardio": ["跑步", "游泳", "骑行", "有氧操"],
            "recommended_strength": ["全身训练", "循环训练"],
        },
        "muscle_gain": {
            "strength_focus": True,
            "recommended_strength": ["杠铃训练", "哑铃训练", "器械训练"],
            "recommended_cardio": ["低强度有氧"],
        },
        "endurance": {
            "cardio_focus": True,
            "recommended_cardio": ["长距离跑", "游泳", "骑行"],
            "recommended_strength": ["功能性训练"],
        },
        "general_fitness": {
            "balanced": True,
            "recommended_cardio": ["多样化有氧"],
            "recommended_strength": ["全身训练"],
        },
    }

    return {
        "cardio": cardio_exercises[fitness_level],
        "strength": strength_exercises[fitness_level],
        "flexibility": flexibility_exercises,
        "goal_specific": goal_adjustments[goal_type],
    }


def _get_progression_plan(goal_type: str, duration_weeks: int) -> List[dict]:
    """获取进阶计划"""

    # 基础进阶模式
    progression_phases = []

    if duration_weeks <= 4:
        # 短期计划
        progression_phases = [
            {"phase": "适应期", "weeks": "1-2", "focus": "建立习惯，学习动作"},
            {"phase": "提升期", "weeks": "3-4", "focus": "增加强度，巩固技术"},
        ]
    elif duration_weeks <= 8:
        # 中期计划
        progression_phases = [
            {"phase": "基础期", "weeks": "1-2", "focus": "建立基础，适应训练"},
            {"phase": "发展期", "weeks": "3-6", "focus": "逐步提升强度和技术"},
            {"phase": "巩固期", "weeks": "7-8", "focus": "巩固成果，准备下阶段"},
        ]
    else:
        # 长期计划
        progression_phases = [
            {"phase": "基础期", "weeks": "1-3", "focus": "建立基础，适应训练"},
            {"phase": "发展期", "weeks": "4-8", "focus": "技术提升，强度增加"},
            {"phase": "强化期", "weeks": "9-12", "focus": "高强度训练，突破平台"},
            {"phase": "维持期", "weeks": "13+", "focus": "维持成果，预防倒退"},
        ]

    # 根据目标调整进阶重点
    goal_specific_adjustments = {
        "weight_loss": "逐步增加有氧运动强度和时长",
        "muscle_gain": "逐步增加重量和训练量",
        "endurance": "逐步增加运动时长和强度",
        "general_fitness": "全面均衡发展各项能力",
    }

    for phase in progression_phases:
        phase["goal_specific_focus"] = goal_specific_adjustments[goal_type]

    return progression_phases


def _generate_health_report_content(user_data: dict, analysis_period: dict) -> dict:
    """生成健康报告内容"""

    report_sections = {
        "executive_summary": {
            "title": "健康状况概览",
            "content": _generate_executive_summary(user_data, analysis_period),
        },
        "activity_analysis": {
            "title": "运动活动分析",
            "content": _analyze_activity_trends(user_data.get("activity_data", [])),
        },
        "sleep_analysis": {
            "title": "睡眠质量分析",
            "content": _analyze_sleep_trends(user_data.get("sleep_data", [])),
        },
        "nutrition_analysis": {
            "title": "营养摄入分析",
            "content": _analyze_nutrition_trends(user_data.get("nutrition_data", [])),
        },
        "health_metrics": {
            "title": "健康指标趋势",
            "content": _analyze_health_metrics(user_data),
        },
        "recommendations": {
            "title": "个性化建议",
            "content": _generate_comprehensive_recommendations(user_data),
        },
        "goals_progress": {
            "title": "目标达成情况",
            "content": _analyze_goals_progress(user_data),
        },
    }

    return report_sections


def _generate_executive_summary(user_data: dict, analysis_period: dict) -> str:
    """生成执行摘要"""

    profile = user_data.get("profile", {})
    activity_data = user_data.get("activity_data", [])
    sleep_data = user_data.get("sleep_data", [])

    # 计算关键指标
    avg_steps = (
        sum(a.get("steps", 0) for a in activity_data) / len(activity_data)
        if activity_data
        else 0
    )
    avg_sleep = (
        sum(s.get("duration_hours", 0) for s in sleep_data) / len(sleep_data)
        if sleep_data
        else 0
    )

    # 生成摘要
    summary = f"""
    在{analysis_period.get('days', 30)}天的分析期间内，您的健康状况总体表现如下：
    
    • 日均步数：{avg_steps:.0f}步
    • 平均睡眠：{avg_sleep:.1f}小时
    • 整体健康评分：{_calculate_overall_health_score(user_data)}/100
    
    主要亮点：{_identify_health_highlights(user_data)}
    需要关注：{_identify_health_concerns(user_data)}
    """

    return summary.strip()


def _calculate_overall_health_score(user_data: dict) -> int:
    """计算整体健康评分"""

    scores = []

    # 活动评分
    activity_data = user_data.get("activity_data", [])
    if activity_data:
        avg_steps = sum(a.get("steps", 0) for a in activity_data) / len(activity_data)
        activity_score = min(100, (avg_steps / 10000) * 100)
        scores.append(activity_score)

    # 睡眠评分
    sleep_data = user_data.get("sleep_data", [])
    if sleep_data:
        avg_sleep = sum(s.get("duration_hours", 0) for s in sleep_data) / len(
            sleep_data
        )
        sleep_score = (
            100 if 7 <= avg_sleep <= 9 else max(0, 100 - abs(avg_sleep - 8) * 20)
        )
        scores.append(sleep_score)

    # 营养评分（如果有数据）
    nutrition_data = user_data.get("nutrition_data", [])
    if nutrition_data:
        # 简化的营养评分
        nutrition_score = 75  # 默认中等评分
        scores.append(nutrition_score)

    return int(sum(scores) / len(scores)) if scores else 50


def _identify_health_highlights(user_data: dict) -> str:
    """识别健康亮点"""
    highlights = []

    activity_data = user_data.get("activity_data", [])
    if activity_data:
        avg_steps = sum(a.get("steps", 0) for a in activity_data) / len(activity_data)
        if avg_steps >= 10000:
            highlights.append("步数目标达成良好")

    sleep_data = user_data.get("sleep_data", [])
    if sleep_data:
        avg_sleep = sum(s.get("duration_hours", 0) for s in sleep_data) / len(
            sleep_data
        )
        if 7 <= avg_sleep <= 9:
            highlights.append("睡眠时长理想")

    return "、".join(highlights) if highlights else "继续努力保持健康习惯"


def _identify_health_concerns(user_data: dict) -> str:
    """识别健康关注点"""
    concerns = []

    activity_data = user_data.get("activity_data", [])
    if activity_data:
        avg_steps = sum(a.get("steps", 0) for a in activity_data) / len(activity_data)
        if avg_steps < 5000:
            concerns.append("日常活动量偏低")

    sleep_data = user_data.get("sleep_data", [])
    if sleep_data:
        avg_sleep = sum(s.get("duration_hours", 0) for s in sleep_data) / len(
            sleep_data
        )
        if avg_sleep < 6.5:
            concerns.append("睡眠时间不足")
        elif avg_sleep > 9.5:
            concerns.append("睡眠时间过长")

    return "、".join(concerns) if concerns else "暂无明显健康风险"


# 健康报告相关辅助函数
def _calculate_key_health_metrics(user_data: dict, period_days: int) -> dict:
    """计算关键健康指标"""

    metrics = {}

    # 活动指标
    activity_data = user_data.get("activity_data", [])
    if activity_data:
        total_steps = sum(a.get("steps", 0) for a in activity_data)
        avg_steps = total_steps / len(activity_data)
        active_days = len([a for a in activity_data if a.get("steps", 0) >= 5000])

        metrics["activity"] = {
            "avg_daily_steps": round(avg_steps),
            "total_steps": total_steps,
            "active_days": active_days,
            "activity_consistency": round((active_days / len(activity_data)) * 100, 1),
        }

    # 睡眠指标
    sleep_data = user_data.get("sleep_data", [])
    if sleep_data:
        avg_sleep = sum(s.get("duration_hours", 0) for s in sleep_data) / len(
            sleep_data
        )
        good_sleep_days = len(
            [s for s in sleep_data if 7 <= s.get("duration_hours", 0) <= 9]
        )

        metrics["sleep"] = {
            "avg_sleep_hours": round(avg_sleep, 1),
            "good_sleep_days": good_sleep_days,
            "sleep_consistency": round((good_sleep_days / len(sleep_data)) * 100, 1),
        }

    # 营养指标
    nutrition_data = user_data.get("nutrition_data", [])
    if nutrition_data:
        avg_calories = sum(n.get("calories", 0) for n in nutrition_data) / len(
            nutrition_data
        )

        metrics["nutrition"] = {
            "avg_daily_calories": round(avg_calories),
            "tracking_days": len(nutrition_data),
        }

    return metrics


def _calculate_data_completeness(user_data: dict, period_days: int) -> dict:
    """计算数据完整性"""

    completeness = {}

    activity_days = len(user_data.get("activity_data", []))
    sleep_days = len(user_data.get("sleep_data", []))
    nutrition_days = len(user_data.get("nutrition_data", []))

    completeness["activity"] = round((activity_days / period_days) * 100, 1)
    completeness["sleep"] = round((sleep_days / period_days) * 100, 1)
    completeness["nutrition"] = round((nutrition_days / period_days) * 100, 1)
    completeness["overall"] = round(
        (activity_days + sleep_days + nutrition_days) / (period_days * 3) * 100, 1
    )

    return completeness


def _get_immediate_actions(user_data: dict) -> List[str]:
    """获取即时行动建议"""

    actions = []

    # 基于活动数据
    activity_data = user_data.get("activity_data", [])
    if activity_data:
        recent_avg_steps = sum(a.get("steps", 0) for a in activity_data[-7:]) / min(
            7, len(activity_data)
        )
        if recent_avg_steps < 5000:
            actions.append("增加日常步行，目标每天至少5000步")

    # 基于睡眠数据
    sleep_data = user_data.get("sleep_data", [])
    if sleep_data:
        recent_avg_sleep = sum(
            s.get("duration_hours", 0) for s in sleep_data[-7:]
        ) / min(7, len(sleep_data))
        if recent_avg_sleep < 6.5:
            actions.append("改善睡眠习惯，确保每晚至少7小时睡眠")

    # 基于营养数据
    nutrition_data = user_data.get("nutrition_data", [])
    if len(nutrition_data) < 7:
        actions.append("开始记录饮食，了解营养摄入情况")

    return actions[:3]  # 最多3个即时行动


def _get_short_term_goals(user_data: dict) -> List[str]:
    """获取短期目标建议"""

    goals = []

    # 活动目标
    activity_data = user_data.get("activity_data", [])
    if activity_data:
        avg_steps = sum(a.get("steps", 0) for a in activity_data) / len(activity_data)
        if avg_steps < 8000:
            goals.append(f"4周内将日均步数提升至{min(avg_steps + 2000, 10000):.0f}步")

    # 睡眠目标
    sleep_data = user_data.get("sleep_data", [])
    if sleep_data:
        good_sleep_ratio = len(
            [s for s in sleep_data if 7 <= s.get("duration_hours", 0) <= 9]
        ) / len(sleep_data)
        if good_sleep_ratio < 0.8:
            goals.append("4周内80%的夜晚保证7-9小时优质睡眠")

    # 体重目标（如果有相关数据）
    profile = user_data.get("profile")
    if profile and hasattr(profile, "weight_kg") and hasattr(profile, "height_cm"):
        from ..utils.health_calculations import calculate_bmi

        bmi = calculate_bmi(profile.height_cm, profile.weight_kg)
        if bmi > 25:
            goals.append("4周内减重1-2公斤，改善身体成分")
        elif bmi < 18.5:
            goals.append("4周内健康增重1-2公斤")

    return goals[:3]


def _get_long_term_objectives(user_data: dict) -> List[str]:
    """获取长期目标建议"""

    objectives = [
        "建立并维持规律的运动习惯",
        "保持稳定的睡眠作息",
        "养成均衡的饮食习惯",
        "定期进行健康检查和评估",
        "持续学习健康知识，提升健康素养",
    ]

    return objectives


# 体重管理相关辅助函数
def _analyze_weight_trends(
    weight_history: List[dict], current_weight: float, target_weight: float = None
) -> dict:
    """分析体重趋势"""

    if len(weight_history) < 2:
        return {
            "trend": "insufficient_data",
            "trend_description": "数据不足，无法分析趋势",
            "weekly_change": 0,
            "monthly_change": 0,
        }

    # 按日期排序
    sorted_history = sorted(weight_history, key=lambda x: x["date"])

    # 计算趋势
    first_weight = sorted_history[0]["weight_kg"]
    last_weight = sorted_history[-1]["weight_kg"]
    total_change = last_weight - first_weight

    # 计算时间跨度
    from datetime import datetime

    first_date = datetime.fromisoformat(sorted_history[0]["date"])
    last_date = datetime.fromisoformat(sorted_history[-1]["date"])
    days_span = (last_date - first_date).days

    if days_span == 0:
        days_span = 1

    # 计算变化率
    weekly_change = (total_change / days_span) * 7
    monthly_change = (total_change / days_span) * 30

    # 判断趋势
    if abs(total_change) < 0.5:
        trend = "stable"
        trend_description = "体重保持稳定"
    elif total_change > 0:
        trend = "increasing"
        trend_description = f"体重呈上升趋势，{days_span}天内增加{total_change:.1f}kg"
    else:
        trend = "decreasing"
        trend_description = (
            f"体重呈下降趋势，{days_span}天内减少{abs(total_change):.1f}kg"
        )

    return {
        "trend": trend,
        "trend_description": trend_description,
        "total_change_kg": round(total_change, 1),
        "weekly_change_kg": round(weekly_change, 2),
        "monthly_change_kg": round(monthly_change, 1),
        "analysis_days": days_span,
    }


def _get_bmi_category(bmi: float) -> str:
    """获取BMI分类"""

    if bmi < 18.5:
        return "偏瘦"
    elif 18.5 <= bmi < 24:
        return "正常"
    elif 24 <= bmi < 28:
        return "超重"
    else:
        return "肥胖"


def _get_healthy_weight_range(height_cm: float) -> dict:
    """获取健康体重范围"""

    height_m = height_cm / 100
    min_weight = 18.5 * (height_m**2)
    max_weight = 24 * (height_m**2)

    return {
        "min_kg": round(min_weight, 1),
        "max_kg": round(max_weight, 1),
        "range_description": f"{min_weight:.1f}-{max_weight:.1f}kg",
    }


def _generate_weight_management_recommendations(
    current_weight: float, target_weight: float, weight_analysis: dict, user_profile
) -> List[str]:
    """生成体重管理建议"""

    recommendations = []

    if not target_weight:
        recommendations.append("建议设定明确的体重目标，有助于制定具体的管理计划")
        return recommendations

    weight_diff = target_weight - current_weight

    if abs(weight_diff) < 1:
        recommendations.append("您已接近目标体重，建议专注于维持当前体重")
    elif weight_diff < 0:  # 需要减重
        recommendations.extend(
            [
                f"目标减重{abs(weight_diff):.1f}kg，建议每周减重0.5-1kg",
                "创造每日300-500卡路里的热量缺口",
                "增加有氧运动，每周至少150分钟中等强度运动",
                "控制饮食份量，选择低热量高营养密度的食物",
            ]
        )
    else:  # 需要增重
        recommendations.extend(
            [
                f"目标增重{weight_diff:.1f}kg，建议每周增重0.3-0.5kg",
                "增加健康的高热量食物摄入",
                "进行力量训练，促进肌肉增长",
                "确保充足的蛋白质摄入",
            ]
        )

    # 基于当前趋势的建议
    trend = weight_analysis.get("trend", "stable")
    if trend == "stable" and abs(weight_diff) > 2:
        recommendations.append("当前体重稳定，需要调整饮食或运动计划以达到目标")
    elif trend == "increasing" and weight_diff < 0:
        recommendations.append("当前体重上升趋势，需要立即调整饮食和运动习惯")
    elif trend == "decreasing" and weight_diff > 0:
        recommendations.append("当前体重下降趋势，需要增加营养摄入")

    return recommendations


def _calculate_weight_timeline(
    current_weight: float, target_weight: float, weight_analysis: dict
) -> dict:
    """计算体重达成时间线"""

    if not target_weight:
        return {"message": "未设定目标体重，无法计算时间线"}

    weight_diff = abs(target_weight - current_weight)

    if weight_diff < 0.5:
        return {"estimated_weeks": 0, "message": "已接近目标体重"}

    # 安全的减重/增重速度
    safe_weekly_change = 0.5  # kg/week

    estimated_weeks = weight_diff / safe_weekly_change
    estimated_months = estimated_weeks / 4.33

    return {
        "estimated_weeks": round(estimated_weeks),
        "estimated_months": round(estimated_months, 1),
        "target_weekly_change": (
            safe_weekly_change
            if target_weight < current_weight
            else -safe_weekly_change
        ),
        "message": f"按照安全速度，预计需要{estimated_weeks:.0f}周（约{estimated_months:.1f}个月）达到目标",
    }


def _get_weight_management_motivation_tips(weight_analysis: dict) -> List[str]:
    """获取体重管理激励建议"""

    tips = [
        "设定小目标，每次成功都值得庆祝",
        "记录进步，不仅仅是体重数字",
        "寻找支持，与朋友家人分享目标",
        "关注感受，体重只是健康的一个指标",
        "保持耐心，健康的改变需要时间",
    ]

    trend = weight_analysis.get("trend", "stable")

    if trend == "decreasing":
        tips.insert(0, "很好！体重下降趋势正确，继续保持")
    elif trend == "increasing":
        tips.insert(0, "不要气馁，调整策略，重新开始")
    else:
        tips.insert(0, "体重稳定是好事，现在专注于改善身体成分")

    return tips
