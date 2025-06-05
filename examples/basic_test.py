#!/usr/bin/env python3
"""
基础测试程序 - 逐步检查模块导入
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("1. 基础Python导入测试...")
try:
    from datetime import datetime, date
    from typing import Dict, List, Any
    print("✅ 基础模块导入成功")
except Exception as e:
    print(f"❌ 基础模块导入失败: {e}")
    sys.exit(1)

print("\n2. AuraWell 核心模块测试...")
try:
    from aurawell.config.settings import settings
    print("✅ 配置模块导入成功")
except Exception as e:
    print(f"❌ 配置模块导入失败: {e}")
    sys.exit(1)

print("\n3. 工具模块测试...")
try:
    from aurawell.utils.date_utils import get_current_utc
    print("✅ 日期工具导入成功")
except Exception as e:
    print(f"❌ 日期工具导入失败: {e}")

try:
    from aurawell.utils.health_calculations import calculate_bmi
    print("✅ 健康计算导入成功")
except Exception as e:
    print(f"❌ 健康计算导入失败: {e}")

print("\n4. 数据模型测试...")
try:
    from aurawell.models.health_data_model import HealthPlatform
    print("✅ 健康数据模型导入成功")
except Exception as e:
    print(f"❌ 健康数据模型导入失败: {e}")

print("\n5. 用户档案模型测试...")
try:
    from aurawell.models.user_profile import ActivityLevel, HealthGoal
    print("✅ 用户档案枚举导入成功")
except Exception as e:
    print(f"❌ 用户档案枚举导入失败: {e}")

try:
    from aurawell.models.user_profile import UserProfile, UserPreferences
    print("✅ 用户档案模型导入成功")
except Exception as e:
    print(f"❌ 用户档案模型导入失败: {e}")

print("\n6. AI客户端测试...")
try:
    from aurawell.core.deepseek_client import DeepSeekClient
    print("✅ DeepSeek客户端导入成功")
except Exception as e:
    print(f"❌ DeepSeek客户端导入失败: {e}")

print("\n7. 游戏化模块测试...")
try:
    from aurawell.gamification.achievement_system import AchievementManager
    print("✅ 成就系统导入成功")
except Exception as e:
    print(f"❌ 成就系统导入失败: {e}")

print("\n🎉 所有模块导入测试完成！")
print(f"当前时间: {get_current_utc()}")
print(f"应用配置: {settings.APP_NAME} v{settings.APP_VERSION}") 