"""
AuraWell Basic Demo Script

This script demonstrates the basic functionality of the AuraWell health lifestyle 
orchestration AI Agent, including:
- DeepSeek AI integration
- Health data models
- User profile management
- Basic health recommendations

Usage:
    python examples/basic_demo.py

Note: Make sure to set your DEEPSEEK_API_KEY in the environment before running.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aurawell.core.deepseek_client import DeepSeekClient, create_health_tools
from aurawell.models.health_data_model import (
    UnifiedActivitySummary, 
    UnifiedSleepSession, 
    HealthPlatform, 
    DataQuality
)
from aurawell.models.user_profile import (
    UserProfile, 
    UserPreferences, 
    HealthGoal, 
    ActivityLevel,
    create_default_user_profile
)


def demo_deepseek_integration():
    """Demonstrate DeepSeek AI integration"""
    print("🤖 AuraWell DeepSeek Integration Demo")
    print("=" * 50)
    
    try:
        # Initialize DeepSeek client
        client = DeepSeekClient()
        tools = create_health_tools()
        
        # Create a sample conversation
        messages = [
            {
                "role": "system",
                "content": """你是AuraWell健康助手，专注于个性化健康建议。你的任务是：
1. 根据用户的健康数据和日程安排提供建议
2. 使用动机式访谈技巧鼓励用户
3. 提供具体、可行的健康改善建议
4. 保持友好、支持性的语调"""
            },
            {
                "role": "user",
                "content": """我是一个30岁的程序员，最近工作很忙，睡眠质量不好，平时缺乏运动。
我想改善我的健康状况，特别是睡眠和运动方面。你能帮我制定一个合理的健康计划吗？"""
            }
        ]
        
        # Get AI response
        print("正在咨询AuraWell健康助手...")
        response = client.get_deepseek_response(
            messages=messages,
            tools=tools,
            model_name="deepseek-r1",
            temperature=0.7
        )
        
        print(f"\n🎯 AuraWell建议:\n{response.content}")
        
        if response.tool_calls:
            print(f"\n🔧 建议的数据获取操作:")
            for tool_call in response.tool_calls:
                print(f"- {tool_call['function']['name']}: {tool_call['function']['arguments']}")
        
        if response.usage:
            print(f"\n📊 API使用情况:")
            print(f"- 模型: {response.usage.model}")
            print(f"- 总Token数: {response.usage.total_tokens}")
            print(f"- 输入Token: {response.usage.prompt_tokens}")
            print(f"- 输出Token: {response.usage.completion_tokens}")
        
    except Exception as e:
        print(f"❌ DeepSeek演示失败: {e}")
        print("请确保在环境变量中设置了 DEEPSEEK_API_KEY")


def demo_health_data_models():
    """Demonstrate health data models"""
    print("\n📊 健康数据模型演示")
    print("=" * 50)
    
    # Create sample activity data
    today = datetime.now(timezone.utc).date().isoformat()
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    
    activity_today = UnifiedActivitySummary(
        date=today,
        steps=8500,
        distance_meters=6800,
        active_calories=320,
        total_calories=420,
        active_minutes=45,
        source_platform=HealthPlatform.XIAOMI_HEALTH,
        data_quality=DataQuality.HIGH
    )
    
    activity_yesterday = UnifiedActivitySummary(
        date=yesterday,
        steps=12000,
        distance_meters=9600,
        active_calories=480,
        total_calories=580,
        active_minutes=65,
        source_platform=HealthPlatform.APPLE_HEALTH,
        data_quality=DataQuality.HIGH
    )
    
    print(f"📱 今日活动数据 ({activity_today.source_platform.value}):")
    print(f"- 步数: {activity_today.steps:,} 步")
    print(f"- 距离: {activity_today.distance_meters/1000:.1f} 公里")
    print(f"- 活跃卡路里: {activity_today.active_calories} 千卡")
    print(f"- 活跃时间: {activity_today.active_minutes} 分钟")
    
    print(f"\n📱 昨日活动数据 ({activity_yesterday.source_platform.value}):")
    print(f"- 步数: {activity_yesterday.steps:,} 步")
    print(f"- 距离: {activity_yesterday.distance_meters/1000:.1f} 公里")
    print(f"- 活跃卡路里: {activity_yesterday.active_calories} 千卡")
    print(f"- 活跃时间: {activity_yesterday.active_minutes} 分钟")
    
    # Create sample sleep data
    last_night = UnifiedSleepSession(
        start_time_utc=datetime.now(timezone.utc).replace(hour=23, minute=30) - timedelta(days=1),
        end_time_utc=datetime.now(timezone.utc).replace(hour=7, minute=15),
        total_duration_seconds=7*3600 + 45*60,  # 7小时45分钟
        deep_sleep_seconds=2*3600 + 30*60,      # 2小时30分钟深睡
        light_sleep_seconds=4*3600 + 45*60,     # 4小时45分钟浅睡
        rem_sleep_seconds=30*60,                # 30分钟REM
        sleep_efficiency=85.5,
        source_platform=HealthPlatform.XIAOMI_HEALTH,
        data_quality=DataQuality.HIGH
    )
    
    print(f"\n🌙 昨晚睡眠数据:")
    print(f"- 入睡时间: {last_night.start_time_utc.strftime('%H:%M')}")
    print(f"- 起床时间: {last_night.end_time_utc.strftime('%H:%M')}")
    print(f"- 总睡眠时长: {last_night.total_duration_seconds//3600}小时{(last_night.total_duration_seconds%3600)//60}分钟")
    print(f"- 深睡时长: {last_night.deep_sleep_seconds//3600}小时{(last_night.deep_sleep_seconds%3600)//60}分钟")
    print(f"- 睡眠效率: {last_night.sleep_efficiency}%")


def demo_user_profile():
    """Demonstrate user profile management"""
    print("\n👤 用户配置文件演示")
    print("=" * 50)
    
    # Create a sample user profile
    user_profile = create_default_user_profile(
        user_id="demo_user_001",
        email="demo@aurawell.ai"
    )
    
    # Customize the profile
    user_profile.age = 30
    user_profile.gender = "male"
    user_profile.height_cm = 175
    user_profile.weight_kg = 70
    user_profile.activity_level = ActivityLevel.LIGHTLY_ACTIVE
    user_profile.primary_goal = HealthGoal.IMPROVE_FITNESS
    user_profile.secondary_goals = [HealthGoal.IMPROVE_SLEEP, HealthGoal.STRESS_REDUCTION]
    user_profile.daily_steps_goal = 8000
    user_profile.connected_platforms = [HealthPlatform.XIAOMI_HEALTH, HealthPlatform.APPLE_HEALTH]
    
    print(f"👨 用户信息:")
    print(f"- 用户ID: {user_profile.user_id}")
    print(f"- 年龄: {user_profile.age}岁")
    print(f"- 身高: {user_profile.height_cm}cm")
    print(f"- 体重: {user_profile.weight_kg}kg")
    print(f"- 活跃度: {user_profile.activity_level.value}")
    
    print(f"\n🎯 健康目标:")
    print(f"- 主要目标: {user_profile.primary_goal.value}")
    print(f"- 次要目标: {', '.join([goal.value for goal in user_profile.secondary_goals])}")
    print(f"- 每日步数目标: {user_profile.daily_steps_goal:,}步")
    print(f"- 睡眠时长目标: {user_profile.sleep_duration_goal_hours}小时")
    
    print(f"\n📱 已连接平台:")
    for platform in user_profile.connected_platforms:
        print(f"- {platform.value}")
    
    # Calculate BMI
    from aurawell.models.user_profile import calculate_bmi_from_profile, get_recommended_daily_calories
    
    bmi = calculate_bmi_from_profile(user_profile)
    recommended_calories = get_recommended_daily_calories(user_profile)
    
    print(f"\n📈 健康指标:")
    print(f"- BMI: {bmi:.1f}")
    print(f"- 推荐日摄入卡路里: {recommended_calories}千卡")


def demo_health_recommendations():
    """Demonstrate health recommendations based on data"""
    print("\n💡 健康建议生成演示")
    print("=" * 50)
    
    print("📋 基于演示数据的健康洞察:")
    print("\n🚶‍♂️ 活动分析:")
    print("- 今天步数(8,500)低于昨天(12,000)，建议增加日常活动")
    print("- 活跃时间45分钟较好，继续保持")
    print("- 建议目标：争取每天达到10,000步")
    
    print("\n😴 睡眠分析:")
    print("- 昨晚睡眠时长7小时45分钟，接近理想的8小时")
    print("- 深睡比例(32%)良好，有助于身体恢复")
    print("- 睡眠效率85.5%优秀")
    print("- 建议：保持规律的睡眠时间")
    
    print("\n🎯 个性化建议:")
    print("- 考虑到您是程序员，建议每小时起身活动5分钟")
    print("- 睡前1小时避免屏幕时间，有助于提高睡眠质量")
    print("- 可以尝试简单的办公室运动，如拉伸或深蹲")
    print("- 建议设置运动提醒，保持规律的活动习惯")


def main():
    """Main demo function"""
    print("🌟 欢迎使用AuraWell - 超个性化健康生活方式编排AI Agent")
    print("🚀 Version 0.1.0 - Phase 2 Development Demo")
    print("=" * 70)
    
    # Run demonstrations
    demo_deepseek_integration()
    demo_health_data_models()
    demo_user_profile()
    demo_health_recommendations()
    
    print("\n" + "=" * 70)
    print("✅ AuraWell基础功能演示完成！")
    print("\n🔧 已实现功能:")
    print("- ✅ DeepSeek AI集成与函数调用")
    print("- ✅ 统一健康数据模型")
    print("- ✅ 用户配置文件管理")
    print("- ✅ 多平台数据标准化")
    print("- ✅ 安全的API密钥管理")
    
    print("\n🚧 下一步开发:")
    print("- 🔄 数据解析和规范化层")
    print("- 🧠 动态健康计划调整逻辑")
    print("- 🎮 游戏化和微干预系统")
    print("- 📊 高级生物特征洞察")
    
    print("\n💡 使用提示:")
    print("1. 设置环境变量 DEEPSEEK_API_KEY 来启用AI功能")
    print("2. 根据需要配置其他健康平台的API密钥")
    print("3. 查看 README.md 了解完整的项目架构")
    print("\n🎉 感谢体验AuraWell！")


if __name__ == "__main__":
    main() 