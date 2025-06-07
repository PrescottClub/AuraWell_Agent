#!/usr/bin/env python3
"""
AuraWell SQLAlchemy数据库集成测试

测试新的数据库层功能：
- 数据库连接和初始化
- 用户档案CRUD操作
- 健康数据存储和检索
- 成就系统数据管理
- Repository模式验证

Usage:
    python test_database_integration.py
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, date, timezone
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """测试数据库连接"""
    print("\n🔗 测试数据库连接...")
    
    try:
        from aurawell.database.connection import DatabaseManager
        
        # 使用内存SQLite数据库进行测试
        db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
        
        # 初始化数据库
        await db_manager.initialize()
        
        # 健康检查
        is_healthy = await db_manager.health_check()
        
        print(f"✅ 数据库连接成功: {is_healthy}")
        print(f"   数据库URL: {db_manager.database_url}")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


async def test_database_models():
    """测试数据库模型"""
    print("\n📊 测试数据库模型...")
    
    try:
        from aurawell.database.models import (
            UserProfileDB, ActivitySummaryDB, SleepSessionDB,
            HeartRateSampleDB, NutritionEntryDB, AchievementProgressDB
        )
        
        # 验证模型类存在
        models = [
            UserProfileDB, ActivitySummaryDB, SleepSessionDB,
            HeartRateSampleDB, NutritionEntryDB, AchievementProgressDB
        ]
        
        print(f"✅ 数据库模型验证成功: {len(models)} 个模型")
        for model in models:
            print(f"   - {model.__name__}: {model.__tablename__}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库模型验证失败: {e}")
        return False


async def test_user_repository():
    """测试用户Repository"""
    print("\n👤 测试用户Repository...")
    
    try:
        from aurawell.database.connection import DatabaseManager
        from aurawell.repositories.user_repository import UserRepository
        from aurawell.models.user_profile import UserProfile, Gender, ActivityLevel
        from aurawell.models.enums import HealthPlatform
        
        # 初始化数据库
        db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
        await db_manager.initialize()
        
        async with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            
            # 创建测试用户
            test_user = UserProfile(
                user_id="test_user_001",
                display_name="测试用户",
                email="test@example.com",
                age=28,
                gender=Gender.MALE,
                height_cm=175.0,
                weight_kg=70.0,
                activity_level=ActivityLevel.MODERATELY_ACTIVE,
                daily_steps_goal=10000,
                connected_platforms=[HealthPlatform.XIAOMI_HEALTH],
                platform_user_ids={"xiaomi_health": "xiaomi_123"}
            )
            
            # 保存用户
            user_db = await user_repo.create_user(test_user)
            print(f"✅ 用户创建成功: {user_db.user_id}")
            
            # 查询用户
            retrieved_user = await user_repo.get_user_by_id("test_user_001")
            print(f"✅ 用户查询成功: {retrieved_user.display_name}")
            
            # 更新用户
            await user_repo.update_user_profile("test_user_001", age=29)
            updated_user = await user_repo.get_user_by_id("test_user_001")
            print(f"✅ 用户更新成功: 年龄 {updated_user.age}")
            
            # 添加平台连接
            await user_repo.add_platform_connection(
                "test_user_001", "xiaomi_health", "xiaomi_123",
                access_token="test_token", is_active=True
            )
            connections = await user_repo.get_platform_connections("test_user_001")
            print(f"✅ 平台连接成功: {len(connections)} 个连接")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ 用户Repository测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_data_repository():
    """测试健康数据Repository"""
    print("\n💓 测试健康数据Repository...")
    
    try:
        from aurawell.database.connection import DatabaseManager
        from aurawell.repositories.health_data_repository import HealthDataRepository
        from aurawell.repositories.user_repository import UserRepository
        from aurawell.models.health_data_model import (
            UnifiedActivitySummary, UnifiedSleepSession, UnifiedHeartRateSample
        )
        from aurawell.models.user_profile import UserProfile, Gender
        from aurawell.models.enums import HealthPlatform, DataQuality, HeartRateType
        
        # 初始化数据库
        db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
        await db_manager.initialize()
        
        async with db_manager.get_session() as session:
            # 先创建用户
            user_repo = UserRepository(session)
            test_user = UserProfile(
                user_id="test_user_001",
                display_name="测试用户",
                age=28,
                gender=Gender.MALE
            )
            await user_repo.create_user(test_user)

            health_repo = HealthDataRepository(session)

            # 测试活动数据
            activity = UnifiedActivitySummary(
                date="2025-01-15",
                steps=12000,
                distance_meters=8500.0,
                active_calories=450.0,
                total_calories=2200.0,
                active_minutes=60,
                source_platform=HealthPlatform.XIAOMI_HEALTH,
                data_quality=DataQuality.HIGH
            )
            
            activity_db = await health_repo.save_activity_summary("test_user_001", activity)
            print(f"✅ 活动数据保存成功: {activity_db.steps} 步")
            
            # 查询活动数据
            activities = await health_repo.get_activity_summaries("test_user_001", limit=5)
            print(f"✅ 活动数据查询成功: {len(activities)} 条记录")
            
            # 测试睡眠数据
            sleep = UnifiedSleepSession(
                start_time_utc=datetime(2025, 1, 14, 22, 30, tzinfo=timezone.utc),
                end_time_utc=datetime(2025, 1, 15, 7, 0, tzinfo=timezone.utc),
                total_duration_seconds=450*60,  # 450 minutes in seconds
                deep_sleep_seconds=120*60,
                light_sleep_seconds=280*60,
                rem_sleep_seconds=50*60,
                sleep_efficiency=85.0,  # percentage
                source_platform=HealthPlatform.XIAOMI_HEALTH,
                data_quality=DataQuality.HIGH
            )
            
            sleep_db = await health_repo.save_sleep_session("test_user_001", sleep)
            print(f"✅ 睡眠数据保存成功: {sleep_db.total_sleep_minutes} 分钟")
            
            # 测试心率数据
            heart_rate = UnifiedHeartRateSample(
                timestamp_utc=datetime.now(timezone.utc),
                bpm=72,
                measurement_type=HeartRateType.RESTING,
                context="morning_measurement",
                source_platform=HealthPlatform.XIAOMI_HEALTH,
                data_quality=DataQuality.HIGH
            )
            
            hr_db = await health_repo.save_heart_rate_sample("test_user_001", heart_rate)
            print(f"✅ 心率数据保存成功: {hr_db.bpm} BPM")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ 健康数据Repository测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_achievement_repository():
    """测试成就Repository"""
    print("\n🏆 测试成就Repository...")
    
    try:
        from aurawell.database.connection import DatabaseManager
        from aurawell.repositories.achievement_repository import AchievementRepository
        from aurawell.repositories.user_repository import UserRepository
        from aurawell.models.user_profile import UserProfile, Gender
        
        # 初始化数据库
        db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
        await db_manager.initialize()
        
        async with db_manager.get_session() as session:
            # 先创建用户
            user_repo = UserRepository(session)
            test_user = UserProfile(
                user_id="test_user_001",
                display_name="测试用户",
                age=28,
                gender=Gender.MALE
            )
            await user_repo.create_user(test_user)

            achievement_repo = AchievementRepository(session)

            # 保存成就进度
            achievement_db = await achievement_repo.save_achievement_progress(
                user_id="test_user_001",
                achievement_type="daily_steps",
                achievement_level="bronze",
                current_value=8000.0,
                target_value=10000.0,
                is_unlocked=False
            )
            print(f"✅ 成就进度保存成功: {achievement_db.progress_percentage}%")
            
            # 解锁成就
            await achievement_repo.save_achievement_progress(
                user_id="test_user_001",
                achievement_type="daily_steps",
                achievement_level="bronze",
                current_value=12000.0,
                target_value=10000.0,
                is_unlocked=True,
                unlocked_at=datetime.now(timezone.utc)
            )
            
            # 查询用户成就
            achievements = await achievement_repo.get_user_achievements("test_user_001")
            print(f"✅ 成就查询成功: {len(achievements)} 个成就")
            
            # 获取成就统计
            stats = await achievement_repo.get_achievement_stats("test_user_001")
            print(f"✅ 成就统计: {stats['unlocked_achievements']}/{stats['total_achievements']} 已解锁")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ 成就Repository测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database_service():
    """测试数据库服务"""
    print("\n🔧 测试数据库服务...")
    
    try:
        from aurawell.services.database_service import DatabaseService
        from aurawell.database.connection import DatabaseManager
        from aurawell.models.user_profile import UserProfile, Gender, ActivityLevel
        from aurawell.models.health_data_model import UnifiedActivitySummary
        from aurawell.models.enums import HealthPlatform, DataQuality
        
        # 初始化数据库服务
        db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
        db_service = DatabaseService(db_manager)
        
        # 健康检查
        is_healthy = await db_service.health_check()
        print(f"✅ 数据库服务健康检查: {is_healthy}")
        
        # 创建用户
        test_user = UserProfile(
            user_id="service_test_001",
            display_name="服务测试用户",
            email="service@example.com",
            age=25,
            gender=Gender.FEMALE,
            activity_level=ActivityLevel.VERY_ACTIVE
        )
        
        success = await db_service.create_user_profile(test_user)
        print(f"✅ 用户创建: {success}")
        
        # 保存活动数据
        activity = UnifiedActivitySummary(
            date="2025-01-15",
            steps=15000,
            distance_meters=12000.0,
            active_calories=600.0,
            source_platform=HealthPlatform.XIAOMI_HEALTH,
            data_quality=DataQuality.HIGH
        )
        
        success = await db_service.save_activity_data("service_test_001", activity)
        print(f"✅ 活动数据保存: {success}")
        
        # 获取活动摘要
        summary = await db_service.get_activity_summary("service_test_001", days=7)
        print(f"✅ 活动摘要查询: {len(summary)} 条记录")
        
        # 更新成就进度
        success = await db_service.update_achievement_progress(
            "service_test_001", "daily_steps", "silver", 15000.0, 15000.0
        )
        print(f"✅ 成就进度更新: {success}")
        
        # 获取数据库统计
        stats = await db_service.get_database_stats()
        print(f"✅ 数据库统计: {stats['users']} 用户, {stats['activity_records']} 活动记录")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database_migrations():
    """测试数据库迁移"""
    print("\n🔄 测试数据库迁移...")
    
    try:
        from aurawell.database.migrations import DatabaseMigrator
        from aurawell.database.connection import DatabaseManager
        
        # 初始化数据库管理器
        db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
        migrator = DatabaseMigrator(db_manager)
        
        # 初始化数据库
        success = await migrator.initialize_database()
        print(f"✅ 数据库初始化: {success}")
        
        # 验证模式
        valid = await migrator.validate_schema()
        print(f"✅ 模式验证: {valid}")
        
        # 获取表信息
        table_info = await migrator.get_table_info()
        print(f"✅ 表信息: {len(table_info)} 个表")
        for table_name, info in table_info.items():
            print(f"   - {table_name}: {info['column_count']} 列")
        
        await db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有数据库集成测试"""
    print("🚀 AuraWell SQLAlchemy数据库集成测试")
    print("=" * 50)
    
    tests = [
        ("数据库连接", test_database_connection),
        ("数据库模型", test_database_models),
        ("用户Repository", test_user_repository),
        ("健康数据Repository", test_health_data_repository),
        ("成就Repository", test_achievement_repository),
        ("数据库服务", test_database_service),
        ("数据库迁移", test_database_migrations),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有数据库集成测试通过！SQLAlchemy集成成功！")
        return True
    else:
        print("⚠️  部分测试失败，请检查错误信息")
        return False


if __name__ == "__main__":
    asyncio.run(main())
