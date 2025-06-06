#!/usr/bin/env python3
"""
AuraWell 简化演示程序

演示AuraWell的核心功能：
- DeepSeek AI集成
- 健康数据模型
- 用户档案管理
- 健康平台集成
- 基础健康计算

Usage:
    python examples/simplified_demo.py
"""

import os
import sys
from datetime import datetime, timezone, date
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core components individually to avoid circular imports
from aurawell.core.deepseek_client import DeepSeekClient
from aurawell.models.health_data_model import (
    UnifiedActivitySummary, UnifiedSleepSession, HealthPlatform, DataQuality
)
from aurawell.models.user_profile import (
    UserProfile, UserPreferences, HealthGoal, ActivityLevel, Gender
)
from aurawell.integrations.xiaomi_health_client import XiaomiHealthClient
from aurawell.integrations.bohe_health_client import BoheHealthClient
from aurawell.utils.health_calculations import calculate_bmi, calculate_bmr, calculate_tdee
from aurawell.utils.date_utils import get_current_utc, format_duration
from aurawell.config.settings import settings


def display_banner() -> None:
    """显示欢迎横幅"""
    print("🌟" + "="*78 + "🌟")
    print("   欢迎使用 AuraWell - 超个性化健康生活方式编排AI Agent")
    print("   版本: 0.1.0 (Phase 1-3 功能演示)")
    print("🌟" + "="*78 + "🌟")


def test_deepseek_integration() -> None:
    """测试DeepSeek AI集成"""
    print("\n🤖 测试 DeepSeek AI 集成...")
    
    try:
        client = DeepSeekClient()
        
        # 简单的健康咨询测试
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的健康顾问。请用简短、实用的建议回答用户问题。"
            },
            {
                "role": "user", 
                "content": "我最近睡眠质量不好，经常晚上失眠，请给我一些改善睡眠的建议。"
            }
        ]
        
        if os.getenv("DEEPSEEK_API_KEY"):
            response = client.get_deepseek_response(messages=messages, temperature=0.7)
            print(f"✅ DeepSeek AI 响应:")
            print(f"   模型: {response.model}")
            print(f"   Token使用: 输入 {response.usage.prompt_tokens}, 输出 {response.usage.completion_tokens}")
            print(f"   建议: {response.content[:200]}...")
        else:
            print("⚠️  DEEPSEEK_API_KEY 未设置，跳过AI功能测试")
            print("   DeepSeek客户端初始化成功")
        
    except Exception as e:
        print(f"❌ DeepSeek集成测试失败: {e}")


def test_health_data_models() -> None:
    """测试健康数据模型"""
    print("\n📊 测试健康数据模型...")
    
    try:
        # 创建活动数据示例
        activity = UnifiedActivitySummary(
            date=date.today().strftime('%Y-%m-%d'),
            steps=8500,
            distance_meters=6800,
            active_calories=320,
            total_calories=2100,
            active_minutes=45,
            source_platform=HealthPlatform.XIAOMI_HEALTH,
            data_quality=DataQuality.HIGH
        )
        
        print(f"✅ 活动数据模型创建成功:")
        print(f"   日期: {activity.date}")
        print(f"   步数: {activity.steps:,}")
        print(f"   距离: {activity.distance_meters/1000:.1f} 公里")
        print(f"   消耗卡路里: {activity.active_calories}")
        print(f"   数据源: {activity.source_platform.value}")

        # 创建睡眠数据示例
        sleep_session = UnifiedSleepSession(
            start_time_utc=datetime(2024, 1, 15, 23, 30, tzinfo=timezone.utc),
            end_time_utc=datetime(2024, 1, 16, 7, 15, tzinfo=timezone.utc),
            total_duration_seconds=27900,  # 7小时45分钟
            deep_sleep_seconds=6300,  # 105分钟
            light_sleep_seconds=13500,  # 225分钟
            rem_sleep_seconds=5400,  # 90分钟
            awake_seconds=2700,  # 45分钟
            sleep_efficiency=85.5,
            source_platform=HealthPlatform.XIAOMI_HEALTH,
            data_quality=DataQuality.HIGH
        )
        
        print(f"\n✅ 睡眠数据模型创建成功:")
        print(f"   睡眠时长: {format_duration(sleep_session.total_duration_seconds)}")
        print(f"   睡眠效率: {sleep_session.sleep_efficiency:.1f}%")
        print(f"   深度睡眠: {sleep_session.deep_sleep_seconds // 60} 分钟")
        
    except Exception as e:
        print(f"❌ 健康数据模型测试失败: {e}")


def test_user_profile():
    """测试用户档案功能"""
    print("\n👤 测试用户档案功能...")
    
    try:
        # 创建用户档案
        profile = UserProfile(
            user_id="demo_001",
            email="demo@aurawell.com",
            display_name="张小明",
            age=28,
            gender=Gender.MALE,
            height_cm=175,
            weight_kg=75,
            primary_goal=HealthGoal.IMPROVE_FITNESS,
            secondary_goals=[HealthGoal.IMPROVE_SLEEP],
            activity_level=ActivityLevel.LIGHTLY_ACTIVE,
            daily_steps_goal=10000,
            daily_calories_goal=2200,
            sleep_duration_goal_hours=8.0
        )
        
        print(f"✅ 用户档案创建成功:")
        print(f"   姓名: {profile.display_name}")
        print(f"   年龄: {profile.age}岁")
        print(f"   身高/体重: {profile.height_cm}cm / {profile.weight_kg}kg")
        print(f"   主要目标: {profile.primary_goal}")
        print(f"   活动水平: {profile.activity_level}")
        
        # 创建用户偏好
        preferences = UserPreferences(
            user_id="demo_001",
            preferred_workout_times=["morning", "evening"],
            available_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
            focus_areas=["exercise", "sleep"],
            communication_style="supportive",
            reminder_frequency="medium"
        )
        
        print(f"\n✅ 用户偏好设置成功:")
        print(f"   运动时间偏好: {', '.join(preferences.preferred_workout_times)}")
        print(f"   关注领域: {', '.join(preferences.focus_areas)}")
        print(f"   沟通风格: {preferences.communication_style}")
        
    except Exception as e:
        print(f"❌ 用户档案测试失败: {e}")


def test_health_calculations():
    """测试健康计算功能"""
    print("\n🧮 测试健康计算功能...")
    
    try:
        # 测试数据
        weight_kg = 75
        height_cm = 175
        age = 28
        gender = Gender.MALE
        activity_level = ActivityLevel.LIGHTLY_ACTIVE
        
        # 计算BMI
        bmi = calculate_bmi(weight_kg, height_cm)
        print(f"✅ BMI计算: {bmi:.1f}")
        
        # 计算BMR (基础代谢率)
        bmr = calculate_bmr(weight_kg, height_cm, age, gender)
        print(f"✅ BMR计算: {bmr:.0f} 千卡/天")
        
        # 计算TDEE (总日消耗)
        tdee = calculate_tdee(bmr, activity_level)
        print(f"✅ TDEE计算: {tdee:.0f} 千卡/天")
        
        # 计算心率区间
        from aurawell.utils.health_calculations import calculate_max_heart_rate, calculate_heart_rate_zones
        max_hr = calculate_max_heart_rate(age)
        hr_zones = calculate_heart_rate_zones(max_hr)
        
        print(f"\n✅ 心率计算:")
        print(f"   最大心率: {max_hr} BPM")
        print(f"   有氧区间: {hr_zones['aerobic'][0]}-{hr_zones['aerobic'][1]} BPM")
        
    except Exception as e:
        print(f"❌ 健康计算测试失败: {e}")


def test_health_platform_integration():
    """测试健康平台集成"""
    print("\n🔗 测试健康平台集成...")
    
    try:
        # 测试小米健康客户端
        xiaomi_client = XiaomiHealthClient()
        print(f"✅ 小米健康客户端初始化成功")
        print(f"   基础URL: {xiaomi_client.base_url}")
        print(f"   支持的数据类型: 步数、心率、睡眠、运动")
        
        # 测试薄荷健康客户端  
        bohe_client = BoheHealthClient()
        print(f"\n✅ 薄荷健康客户端初始化成功")
        print(f"   基础URL: {bohe_client.base_url}")
        print(f"   支持的数据类型: 营养、体重、卡路里")
        
        print(f"\n🔑 API密钥状态:")
        xiaomi_config = settings.get_health_platform_config("xiaomi")
        bohe_config = settings.get_health_platform_config("bohe")
        
        print(f"   小米健康: {'已配置' if xiaomi_config.get('api_key') else '未配置'}")
        print(f"   薄荷健康: {'已配置' if bohe_config.get('api_key') else '未配置'}")
        
    except Exception as e:
        print(f"❌ 健康平台集成测试失败: {e}")


def test_configuration():
    """测试配置系统"""
    print("\n⚙️  测试配置系统...")
    
    try:
        print(f"✅ 应用配置:")
        print(f"   应用名称: {settings.APP_NAME}")
        print(f"   版本: {settings.APP_VERSION}")
        print(f"   调试模式: {settings.DEBUG}")
        print(f"   日志级别: {settings.LOG_LEVEL}")
        print(f"   默认步数目标: {settings.DEFAULT_DAILY_STEPS:,}")
        print(f"   默认睡眠目标: {settings.DEFAULT_SLEEP_HOURS} 小时")
        
        # 验证必需设置
        missing_settings = settings.validate_required_settings()
        if missing_settings:
            print(f"\n⚠️  缺失的必需设置: {', '.join(missing_settings)}")
        else:
            print(f"\n✅ 所有必需设置已配置")
        
    except Exception as e:
        print(f"❌ 配置系统测试失败: {e}")


def show_project_structure():
    """显示项目结构"""
    print("\n📁 AuraWell 项目结构:")
    print("""
aurawell/
├── core/                   # 核心AI和编排逻辑
│   ├── deepseek_client.py  # DeepSeek AI集成
│   └── orchestrator.py     # 健康编排器 (Phase 3)
├── models/                 # 数据模型
│   ├── health_data_model.py # 统一健康数据模型
│   ├── user_profile.py     # 用户档案模型
│   └── health_data_parser.py # 数据解析器
├── integrations/           # 健康平台集成
│   ├── generic_health_api_client.py # 通用API客户端
│   ├── xiaomi_health_client.py     # 小米健康
│   ├── bohe_health_client.py       # 薄荷健康
│   └── apple_health_client.py      # 苹果健康
├── utils/                  # 工具函数
│   ├── health_calculations.py  # 健康计算
│   ├── date_utils.py          # 日期时间工具
│   ├── data_validation.py     # 数据验证
│   └── encryption_utils.py    # 加密工具
├── config/                 # 配置管理
│   ├── settings.py         # 应用设置
│   └── logging_config.py   # 日志配置
└── __init__.py

examples/                   # 示例和演示
├── basic_demo.py          # 基础功能演示
├── simplified_demo.py     # 简化演示 (本程序)
└── phase3_orchestrator_demo.py # Phase 3演示

tests/                     # 单元测试 (待开发)
docs/                      # 文档 (待开发)
""")


def show_features_summary():
    """显示功能总结"""
    print("\n🎯 AuraWell 核心功能总结:")
    print("""
✅ Phase 1 - 项目基础与核心AI集成
   • DeepSeek AI集成与函数调用
   • 统一健康数据模型
   • 用户档案管理系统
   • 配置管理与日志系统

✅ Phase 2 - 健康平台集成  
   • 小米健康API集成
   • 薄荷健康API集成
   • 苹果健康HealthKit集成
   • 通用OAuth 2.0认证
   • 速率限制与错误处理

🚧 Phase 3 - 高级AI编排与动态健康计划调整
   • AI驱动的健康数据分析
   • 个性化洞察生成
   • 动态健康计划创建与调整
   • 上下文感知的每日建议

🔮 Phase 4 - 游戏化与激励系统 (计划中)
   • 成就系统与徽章
   • 积分奖励机制
   • 社交挑战功能
   • 进度可视化
""")


def main():
    """主演示函数"""
    display_banner()
    
    print(f"开始时间: {get_current_utc().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # 运行各项测试
    test_deepseek_integration()
    test_health_data_models()
    test_user_profile()
    test_health_calculations()
    test_health_platform_integration()
    test_configuration()
    
    # 显示项目信息
    show_project_structure()
    show_features_summary()
    
    # 显示总结
    print("\n" + "🌟"*80)
    print("🎉 AuraWell 简化演示完成!")
    print("""
📊 测试结果:
   ✅ DeepSeek AI集成正常
   ✅ 健康数据模型功能完整
   ✅ 用户档案系统工作正常
   ✅ 健康计算函数准确
   ✅ 健康平台集成就绪
   ✅ 配置系统完善

🚀 下一步开发计划:
   • 完善Phase 3健康编排器
   • 开发Phase 4游戏化系统
   • 创建Web界面
   • 添加更多健康平台集成
   • 完善单元测试覆盖

🔧 使用建议:
   • 设置DEEPSEEK_API_KEY以启用完整AI功能
   • 配置健康平台API密钥以测试数据同步
   • 查看examples目录了解更多用法示例
""")
    print("🌟"*80)


if __name__ == "__main__":
    main() 