#!/usr/bin/env python3
"""
AuraWell Phase 3 Orchestrator Demo

Demonstrates the complete health orchestration system including:
- Health data analysis and insight generation
- Personalized health plan creation
- Dynamic plan adjustments
- AI-powered daily recommendations
- Context-aware suggestions

Usage:
    python examples/phase3_orchestrator_demo.py

Requirements:
    - DEEPSEEK_API_KEY environment variable set
    - All AuraWell dependencies installed
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aurawell.core.orchestrator import AuraWellOrchestrator, HealthInsight, HealthPlan
from aurawell.core.deepseek_client import DeepSeekClient
from aurawell.models.health_data_model import (
    UnifiedActivitySummary, UnifiedSleepSession, UnifiedHeartRateSample, 
    NutritionEntry, HealthPlatform, DataQuality
)
from aurawell.models.user_profile import (
    UserProfile, UserPreferences, HealthGoal, ActivityLevel, Gender
)
from aurawell.utils.health_calculations import calculate_bmi, calculate_bmr, calculate_tdee
from aurawell.utils.date_utils import get_current_utc, get_days_ago
from aurawell.config.logging_config import setup_logging


def create_sample_user_profile() -> UserProfile:
    """Create a sample user profile for demonstration"""
    return UserProfile(
        user_id="demo_user_001",
        email="demo@aurawell.com",
        display_name="张小明",
        age=28,
        gender=Gender.MALE,
        height_cm=175,
        weight_kg=75,
        primary_goal=HealthGoal.IMPROVE_FITNESS,
        secondary_goals=[HealthGoal.IMPROVE_SLEEP, HealthGoal.REDUCE_STRESS],
        activity_level=ActivityLevel.LIGHTLY_ACTIVE,
        daily_steps_goal=10000,
        daily_calories_goal=2200,
        sleep_duration_goal_hours=8.0,
        weekly_exercise_goal_minutes=150
    )


def create_sample_user_preferences() -> UserPreferences:
    """Create sample user preferences"""
    return UserPreferences(
        user_id="demo_user_001",
        preferred_workout_times=["morning", "evening"],
        available_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
        focus_areas=["activity", "sleep", "stress"],
        communication_style="encouraging",
        reminder_frequency="medium",
        data_sharing_consent=True,
        notification_enabled=True
    )


def generate_sample_activity_data() -> List[UnifiedActivitySummary]:
    """Generate sample activity data for the past week"""
    activities = []
    
    for i in range(7):
        date = get_days_ago(i)
        
        # Simulate varying activity levels
        if i == 0:  # Today - lower activity
            steps = 6500
            active_calories = 280
        elif i in [1, 3, 5]:  # Some active days
            steps = 12000 + (i * 200)
            active_calories = 450 + (i * 30)
        else:  # Moderate days
            steps = 8500 + (i * 100)
            active_calories = 350 + (i * 20)
        
        activity = UnifiedActivitySummary(
            date=date,
            steps=steps,
            distance_meters=steps * 0.75,  # Rough conversion
            active_calories=active_calories,
            total_calories=active_calories + 1800,  # Add BMR
            exercise_minutes=30 if i in [1, 3, 5] else 15,
            standing_hours=8,
            data_source=HealthPlatform.XIAOMI_HEALTH,
            timestamp_utc=datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc),
            data_quality=DataQuality.HIGH
        )
        activities.append(activity)
    
    return activities


def generate_sample_sleep_data() -> List[UnifiedSleepSession]:
    """Generate sample sleep data for the past week"""
    sleep_sessions = []
    
    for i in range(7):
        date = get_days_ago(i)
        
        # Simulate varying sleep quality
        if i == 0:  # Last night - poor sleep
            duration_hours = 6.5
            efficiency = 75
        elif i in [2, 4]:  # Some good nights
            duration_hours = 8.2
            efficiency = 88
        else:  # Average nights
            duration_hours = 7.5
            efficiency = 82
        
        bedtime = datetime.combine(date, datetime.min.time()).replace(
            hour=23, minute=30, tzinfo=timezone.utc
        )
        wake_time = bedtime + timedelta(hours=duration_hours)
        
        sleep_session = UnifiedSleepSession(
            date=date,
            bedtime_utc=bedtime,
            wake_time_utc=wake_time,
            total_duration_seconds=int(duration_hours * 3600),
            sleep_duration_seconds=int(duration_hours * 3600 * efficiency / 100),
            sleep_efficiency=efficiency,
            deep_sleep_minutes=int(duration_hours * 60 * 0.25),
            rem_sleep_minutes=int(duration_hours * 60 * 0.20),
            light_sleep_minutes=int(duration_hours * 60 * 0.55),
            awake_minutes=int(duration_hours * 60 * (1 - efficiency / 100)),
            data_source=HealthPlatform.XIAOMI_HEALTH,
            data_quality=DataQuality.HIGH
        )
        sleep_sessions.append(sleep_session)
    
    return sleep_sessions


def generate_sample_heart_rate_data() -> List[UnifiedHeartRateSample]:
    """Generate sample heart rate data"""
    hr_samples = []
    
    # Generate some heart rate samples for today
    base_time = get_current_utc().replace(hour=9, minute=0, second=0, microsecond=0)
    
    for i in range(10):
        sample_time = base_time + timedelta(hours=i)
        
        # Simulate varying heart rates throughout the day
        if 9 <= sample_time.hour <= 11:  # Morning
            bpm = 65 + (i * 2)
        elif 12 <= sample_time.hour <= 14:  # Afternoon
            bpm = 70 + (i * 1)
        elif 15 <= sample_time.hour <= 17:  # Active period
            bpm = 85 + (i * 3)
        else:  # Evening
            bpm = 68 + (i * 1)
        
        sample = UnifiedHeartRateSample(
            timestamp_utc=sample_time,
            bpm=bpm,
            context="resting" if bpm < 80 else "active",
            data_source=HealthPlatform.XIAOMI_HEALTH,
            data_quality=DataQuality.HIGH
        )
        hr_samples.append(sample)
    
    return hr_samples


def generate_sample_nutrition_data() -> List[NutritionEntry]:
    """Generate sample nutrition data"""
    nutrition_entries = []
    
    for i in range(3):  # Last 3 days
        date = get_days_ago(i)
        
        # Simulate daily nutrition intake
        if i == 0:  # Today - incomplete
            calories = 1600
            protein = 80
            carbs = 200
            fat = 50
        else:  # Previous days
            calories = 2100 + (i * 50)
            protein = 110 + (i * 10)
            carbs = 250 + (i * 20)
            fat = 70 + (i * 5)
        
        entry = NutritionEntry(
            food_name="每日营养总计",
            brand=None,
            calories=calories,
            protein_grams=protein,
            carbs_grams=carbs,
            fat_grams=fat,
            fiber_grams=25,
            sugar_grams=40,
            sodium_mg=2000,
            serving_size="1天",
            meal_type="summary",
            timestamp_utc=datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc),
            data_source=HealthPlatform.BOHE_HEALTH
        )
        nutrition_entries.append(entry)
    
    return nutrition_entries


def display_health_insights(insights: List[HealthInsight]):
    """Display health insights in a formatted way"""
    print("\n" + "="*60)
    print("🔍 健康洞察报告")
    print("="*60)
    
    for i, insight in enumerate(insights, 1):
        print(f"\n📊 洞察 {i}: {insight.title}")
        print(f"类型: {insight.insight_type}")
        print(f"置信度: {insight.confidence:.0%}")
        print(f"描述: {insight.description}")
        print(f"数据来源: {', '.join(insight.data_sources)}")
        
        if insight.actionable_recommendations:
            print("💡 建议行动:")
            for j, rec in enumerate(insight.actionable_recommendations, 1):
                print(f"   {j}. {rec}")
        
        print("-" * 40)


def display_health_plan(plan: HealthPlan):
    """Display health plan in a formatted way"""
    print("\n" + "="*60)
    print("📋 个性化健康计划")
    print("="*60)
    
    print(f"计划类型: {plan.plan_type}")
    print(f"创建时间: {plan.created_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"有效性评分: {plan.effectiveness_score:.0%}")
    
    print(f"\n🎯 健康目标:")
    for goal in plan.goals:
        print(f"   • {goal.value}")
    
    print(f"\n🏃 运动计划:")
    for activity in plan.activities:
        print(f"   • {activity['description']}")
        print(f"     持续时间: {activity['duration_minutes']}分钟")
        print(f"     频率: {activity['frequency']}")
        print(f"     强度: {activity['intensity']}")
    
    print(f"\n🍎 营养目标:")
    for key, value in plan.nutrition_targets.items():
        if isinstance(value, (int, float)):
            print(f"   • {key}: {value:.0f}")
        else:
            print(f"   • {key}: {value}")
    
    print(f"\n😴 睡眠目标:")
    for key, value in plan.sleep_targets.items():
        print(f"   • {key}: {value}")


def display_daily_recommendations(recommendations: List[Dict[str, Any]]):
    """Display daily recommendations"""
    print("\n" + "="*60)
    print("💡 今日个性化建议")
    print("="*60)
    
    for i, rec in enumerate(recommendations, 1):
        priority_emoji = {"high": "🔥", "medium": "⭐", "low": "💭"}
        emoji = priority_emoji.get(rec.get("priority", "medium"), "💭")
        
        print(f"\n{emoji} 建议 {i}: {rec['title']}")
        print(f"类别: {rec.get('category', 'general')}")
        print(f"优先级: {rec.get('priority', 'medium')}")
        print(f"预计时长: {rec.get('estimated_duration', '未知')}")
        print(f"描述: {rec['description']}")
        print("-" * 40)


def simulate_context_data() -> Dict[str, Any]:
    """Simulate current context data"""
    current_time = get_current_utc()
    
    return {
        "current_time": current_time.isoformat(),
        "weather": "晴朗，22°C",
        "schedule": [
            {"time": "14:00", "event": "工作会议"},
            {"time": "17:30", "event": "健身房时间"},
            {"time": "19:00", "event": "晚餐时间"}
        ],
        "recent_activity": {
            "steps_today": 6500,
            "last_workout": "2天前",
            "sleep_last_night": "6.5小时"
        },
        "user_mood": "有点疲惫",
        "available_time": "30分钟"
    }


def main():
    """Main demonstration function"""
    print("🌟 欢迎使用 AuraWell - 超个性化健康生活方式编排AI Agent")
    print("Phase 3: 高级AI编排与动态健康计划调整演示")
    print("="*80)
    
    # Setup logging
    setup_logging(log_level="INFO", enable_console=True, enable_structured=False)
    
    # Check API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  警告: 未设置 DEEPSEEK_API_KEY 环境变量")
        print("某些AI功能将无法正常工作")
        print("请设置 DEEPSEEK_API_KEY 以体验完整功能")
    
    try:
        # Initialize the orchestrator
        print("\n🚀 初始化AuraWell健康编排器...")
        orchestrator = AuraWellOrchestrator()
        
        # Create sample user data
        print("👤 创建示例用户档案...")
        user_profile = create_sample_user_profile()
        user_preferences = create_sample_user_preferences()
        
        print(f"用户: {user_profile.display_name}")
        print(f"年龄: {user_profile.age}岁, 性别: {user_profile.gender.value}")
        print(f"身高: {user_profile.height_cm}cm, 体重: {user_profile.weight_kg}kg")
        print(f"主要目标: {user_profile.primary_goal.value}")
        print(f"活动水平: {user_profile.activity_level.value}")
        
        # Calculate basic health metrics
        bmi = calculate_bmi(user_profile.weight_kg, user_profile.height_cm)
        bmr = calculate_bmr(
            user_profile.weight_kg, user_profile.height_cm, 
            user_profile.age, user_profile.gender
        )
        tdee = calculate_tdee(bmr, user_profile.activity_level)
        
        print(f"\n📊 基础健康指标:")
        print(f"BMI: {bmi:.1f}")
        print(f"基础代谢率 (BMR): {bmr:.0f} 千卡/天")
        print(f"总日消耗 (TDEE): {tdee:.0f} 千卡/天")
        
        # Generate sample health data
        print("\n📈 生成模拟健康数据...")
        activity_data = generate_sample_activity_data()
        sleep_data = generate_sample_sleep_data()
        heart_rate_data = generate_sample_heart_rate_data()
        nutrition_data = generate_sample_nutrition_data()
        
        print(f"活动数据: {len(activity_data)} 天")
        print(f"睡眠数据: {len(sleep_data)} 天")
        print(f"心率数据: {len(heart_rate_data)} 个样本")
        print(f"营养数据: {len(nutrition_data)} 天")
        
        # Analyze health data and generate insights
        print("\n🔍 分析健康数据并生成洞察...")
        insights = orchestrator.analyze_user_health_data(
            user_profile=user_profile,
            activity_data=activity_data,
            sleep_data=sleep_data,
            heart_rate_data=heart_rate_data,
            nutrition_data=nutrition_data
        )
        
        display_health_insights(insights)
        
        # Create personalized health plan
        print("\n📋 创建个性化健康计划...")
        health_plan = orchestrator.create_personalized_health_plan(
            user_profile=user_profile,
            user_preferences=user_preferences,
            recent_insights=insights
        )
        
        display_health_plan(health_plan)
        
        # Generate daily recommendations with context
        print("\n💡 生成今日个性化建议...")
        current_context = simulate_context_data()
        
        daily_recommendations = orchestrator.generate_daily_recommendations(
            user_profile=user_profile,
            user_preferences=user_preferences,
            current_context=current_context
        )
        
        display_daily_recommendations(daily_recommendations)
        
        # Simulate plan adjustment based on performance
        print("\n🔄 模拟动态计划调整...")
        
        # Simulate performance data
        performance_data = {
            "adherence_rate": 0.75,  # 75% adherence to plan
            "activity_completion": 0.65,  # 65% of activity goals met
            "sleep_quality": 0.70,  # 70% sleep quality score
            "user_satisfaction": 0.80  # 80% user satisfaction
        }
        
        # Simulate user feedback
        user_feedback = {
            "plan_difficulty": "适中",
            "time_constraints": "工作日时间紧张",
            "favorite_activities": ["快步走", "瑜伽"],
            "challenges": ["睡眠不足", "工作压力大"]
        }
        
        print("性能数据:")
        for key, value in performance_data.items():
            print(f"   • {key}: {value:.0%}")
        
        print("\n用户反馈:")
        for key, value in user_feedback.items():
            print(f"   • {key}: {value}")
        
        adjusted_plan = orchestrator.adjust_plan_dynamically(
            user_profile=user_profile,
            performance_data=performance_data,
            feedback=user_feedback
        )
        
        print(f"\n✅ 计划已动态调整")
        print(f"调整时间: {adjusted_plan.last_adjusted.strftime('%Y-%m-%d %H:%M')}")
        print(f"新的有效性评分: {adjusted_plan.effectiveness_score:.0%}")
        
        # Show summary
        print("\n" + "="*80)
        print("📊 AuraWell Phase 3 演示总结")
        print("="*80)
        print(f"✅ 分析了 {len(activity_data)} 天的活动数据")
        print(f"✅ 生成了 {len(insights)} 个健康洞察")
        print(f"✅ 创建了个性化健康计划 ({health_plan.plan_type})")
        print(f"✅ 提供了 {len(daily_recommendations)} 个今日建议")
        print(f"✅ 完成了动态计划调整")
        
        print(f"\n🎯 Phase 3 核心功能展示:")
        print("   • AI驱动的健康数据分析")
        print("   • 个性化洞察生成")
        print("   • 动态健康计划创建")
        print("   • 上下文感知的每日建议")
        print("   • 基于表现的智能计划调整")
        
        print(f"\n🚀 下一步: Phase 4 - 游戏化与激励系统")
        print("即将推出: 成就系统、积分奖励、社交挑战等功能")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n谢谢使用 AuraWell! 🌟")


if __name__ == "__main__":
    main() 