"""
健康指标常量配置
统一管理所有健康相关的阈值和默认值
"""

from typing import Dict, Any

# ==================== 步数相关常量 ====================
STEPS_CONSTANTS = {
    "DEFAULT_DAILY_TARGET": 10000,
    "LOW_ACTIVITY_THRESHOLD": 5000,
    "MODERATE_ACTIVITY_BASE": 8500,
    "HIGH_ACTIVITY_BASE": 12000,
    "EXCELLENT_ACTIVITY_BASE": 15000,
    "VARIANCE_SAMPLES": [8500, 9200, 7800],  # 用于生成测试数据
}

# ==================== 睡眠相关常量 ====================
SLEEP_CONSTANTS = {
    "RECOMMENDED_HOURS": 8.0,
    "MINIMUM_HOURS": 6.5,
    "OPTIMAL_HOURS": 7.5,
    "EXCELLENT_HOURS": 8.5,
    "DEFAULT_QUALITY_SCORE": 85.2,
    "POOR_QUALITY_THRESHOLD": 60.0,
    "GOOD_QUALITY_THRESHOLD": 80.0,
    "EXCELLENT_QUALITY_THRESHOLD": 90.0,
    "DEEP_SLEEP_PERCENTAGE_BASE": 20,
}

# ==================== 卡路里相关常量 ====================
CALORIES_CONSTANTS = {
    "DAILY_INTAKE_BASE": 2000,
    "DAILY_BURN_BASE": 2100,
    "MODERATE_BURN_SAMPLES": [2100, 2300, 1900],  # 用于测试数据
    "PROTEIN_DAILY_BASE": 80,  # 克
    "CARB_DAILY_BASE": 250,  # 克
    "ACTIVITY_MINUTES_BASE": 45,
}

# ==================== 心率相关常量 ====================
HEART_RATE_CONSTANTS = {
    "RESTING_HR_NORMAL": 68,
    "MAX_HR_BASE": 150,
    "AVERAGE_HR_BASE": 85,
    "HR_ZONE_MULTIPLIERS": {
        "rest": 1.0,
        "fat_burn": 1.2,
        "cardio": 1.5,
        "peak": 1.8,
    },
}

# ==================== 体重相关常量 ====================
WEIGHT_CONSTANTS = {
    "HEALTHY_WEEKLY_LOSS": -0.2,  # kg/周
    "MODERATE_CHANGE_THRESHOLD": 0.5,  # kg
    "BMI_CHANGE_BASE": -0.2,
    "WEIGHT_CHANGE_VARIANCE": 0.3,
}

# ==================== 趋势分析常量 ====================
TREND_CONSTANTS = {
    "STEPS_IMPROVEMENT_PERCENT": 5.2,
    "CALORIES_STABLE_PERCENT": 1.1,
    "SLEEP_IMPROVEMENT_HOURS": 0.3,
    "SLEEP_QUALITY_IMPROVEMENT": 2.1,
    "OVERALL_HEALTH_SCORE_BASE": 82.5,
    "OVERALL_HEALTH_PREVIOUS": 79.3,
    "IMPROVEMENT_PERCENT": 4.0,
}

# ==================== 挑战赛相关常量 ====================
CHALLENGE_CONSTANTS = {
    "DEFAULT_DURATION_DAYS": 7,
    "MAX_PARTICIPANTS": 20,
    "MIN_PARTICIPANTS": 2,
    "FAMILY_POINTS_BASE": 150,
    "FAMILY_RANK_BASE": 5,
    "CHALLENGE_TYPES": ["activity", "nutrition", "sleep", "weight_loss", "consistency"],
}

# ==================== 报告生成常量 ====================
REPORT_CONSTANTS = {
    "MAX_MEMBERS_PER_REPORT": 10,
    "MIN_MEMBERS_PER_REPORT": 1,
    "REPORT_VERSION": "3.0.0",
    "DEFAULT_REPORT_DAYS": 30,
    "KEY_INSIGHTS_MAX": 5,
    "RECOMMENDATIONS_MAX": 5,
}

# ==================== 提醒和告警常量 ====================
ALERT_CONSTANTS = {
    "LOW_ACTIVITY_ALERT_THRESHOLD": 5000,  # 步数
    "INSUFFICIENT_SLEEP_THRESHOLD": 6.5,  # 小时
    "SIGNIFICANT_WEIGHT_CHANGE": 1.0,  # kg
    "ALERT_TYPES": [
        "low_activity",
        "insufficient_sleep",
        "significant_weight_change",
        "irregular_heart_rate",
        "missed_goals",
    ],
}

# ==================== 家庭管理常量 ====================
FAMILY_CONSTANTS = {
    "MAX_FAMILIES_PER_USER": 3,
    "MAX_MEMBERS_PER_FAMILY": 10,
    "INVITATION_EXPIRY_HOURS": 72,
    "MIN_FAMILY_NAME_LENGTH": 2,
    "MAX_FAMILY_NAME_LENGTH": 50,
}

# ==================== 测试数据生成常量 ====================
TEST_DATA_CONSTANTS = {
    "MOCK_MEMBER_COUNT": 4,
    "SAMPLE_NAMES": ["张小明", "李小红", "王小刚", "刘小美"],
    "SAMPLE_AVATARS": ["avatar1.jpg", "avatar2.jpg", "avatar3.jpg", "avatar4.jpg"],
    "STREAK_DAYS_BASE": 5,
    "BADGE_SAMPLES": ["坚持达人", "步数之王", "早睡早起", "运动健将"],
}

# ==================== 整合配置字典 ====================
HEALTH_CONSTANTS = {
    "steps": STEPS_CONSTANTS,
    "sleep": SLEEP_CONSTANTS,
    "calories": CALORIES_CONSTANTS,
    "heart_rate": HEART_RATE_CONSTANTS,
    "weight": WEIGHT_CONSTANTS,
    "trends": TREND_CONSTANTS,
    "challenges": CHALLENGE_CONSTANTS,
    "reports": REPORT_CONSTANTS,
    "alerts": ALERT_CONSTANTS,
    "family": FAMILY_CONSTANTS,
    "test_data": TEST_DATA_CONSTANTS,
}


def get_health_constant(category: str, key: str, default: Any = None) -> Any:
    """
    获取健康常量值

    Args:
        category: 常量类别 (steps, sleep, calories等)
        key: 常量键名
        default: 默认值

    Returns:
        常量值或默认值
    """
    return HEALTH_CONSTANTS.get(category, {}).get(key, default)


def get_category_constants(category: str) -> Dict[str, Any]:
    """
    获取指定类别的所有常量

    Args:
        category: 常量类别

    Returns:
        该类别的所有常量字典
    """
    return HEALTH_CONSTANTS.get(category, {})
