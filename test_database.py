#!/usr/bin/env python3
"""
Test script for AuraWell Database Layer
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_layer():
    """Test database layer functionality"""
    try:
        print("Testing AuraWell Database Layer...")
        
        # Import database components
        from aurawell.database.connection import DatabaseManager, DatabaseConfig, DatabaseType
        from aurawell.database.models import UserModel, HealthDataModel, InsightModel, PlanModel
        from aurawell.database.repositories import UserRepository, HealthDataRepository, InsightRepository, PlanRepository
        
        print("✅ Database components imported successfully")
        
        # Create in-memory database for testing
        config = DatabaseConfig(db_type=DatabaseType.MEMORY)
        db_manager = DatabaseManager(config)
        
        # Test connection
        if not db_manager.connect():
            raise Exception("Failed to connect to database")
        print("✅ Database connected successfully")
        
        # Test connection info
        info = db_manager.get_connection_info()
        print(f"✅ Connection info: {info}")
        
        # Initialize repositories
        user_repo = UserRepository(db_manager)
        health_repo = HealthDataRepository(db_manager)
        insight_repo = InsightRepository(db_manager)
        plan_repo = PlanRepository(db_manager)
        print("✅ Repositories initialized")
        
        # Test user operations
        test_user = UserModel(
            user_id="test_user_001",
            email="test@example.com",
            display_name="Test User",
            age=30,
            gender="male",
            height_cm=175.0,
            weight_kg=70.0,
            activity_level="moderately_active",
            primary_goal="weight_loss",
            daily_steps_goal=10000,
            sleep_duration_goal_hours=8.0,
            preferences={"notifications": True, "units": "metric"}
        )
        
        # Create user
        if user_repo.create_user(test_user):
            print("✅ User created successfully")
        else:
            raise Exception("Failed to create user")
        
        # Get user
        retrieved_user = user_repo.get_user("test_user_001")
        if retrieved_user and retrieved_user.user_id == "test_user_001":
            print("✅ User retrieved successfully")
        else:
            raise Exception("Failed to retrieve user")
        
        # Test health data operations
        test_health_data = HealthDataModel(
            user_id="test_user_001",
            data_type="activity",
            date="2025-01-15",
            data_json={
                "steps": 8500,
                "distance_meters": 6800,
                "active_calories": 350
            },
            source_platform="test_platform",
            data_quality="high"
        )
        
        if health_repo.store_health_data(test_health_data):
            print("✅ Health data stored successfully")
        else:
            raise Exception("Failed to store health data")
        
        # Get health data
        health_data_list = health_repo.get_health_data("test_user_001", data_type="activity")
        if health_data_list and len(health_data_list) > 0:
            print(f"✅ Retrieved {len(health_data_list)} health data records")
        else:
            raise Exception("Failed to retrieve health data")
        
        # Test insight operations
        test_insight = InsightModel(
            insight_id="insight_001",
            user_id="test_user_001",
            insight_type="activity_pattern",
            priority="medium",
            title="步数目标完成度较低",
            description="最近平均每日步数为 8500 步，仅达到目标的 85%",
            recommendations=["增加日常步行", "设置提醒"],
            data_points={"avg_steps": 8500, "goal_steps": 10000},
            confidence_score=0.9,
            generated_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        if insight_repo.store_insight(test_insight):
            print("✅ Insight stored successfully")
        else:
            raise Exception("Failed to store insight")
        
        # Get insights
        insights = insight_repo.get_user_insights("test_user_001")
        if insights and len(insights) > 0:
            print(f"✅ Retrieved {len(insights)} insights")
        else:
            raise Exception("Failed to retrieve insights")
        
        # Test plan operations
        test_plan = PlanModel(
            plan_id="plan_001",
            user_id="test_user_001",
            title="个性化健康计划",
            description="基于您的健康数据制定的计划",
            goals=[
                {"type": "daily_steps", "target": 10000},
                {"type": "sleep_hours", "target": 8.0}
            ],
            daily_recommendations=[
                {"time": "morning", "activity": "晨间运动", "duration": 30}
            ],
            weekly_targets={"exercise_sessions": 3},
            created_at=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc) + timedelta(days=30),
            last_updated=datetime.now(timezone.utc)
        )
        
        if plan_repo.store_plan(test_plan):
            print("✅ Plan stored successfully")
        else:
            raise Exception("Failed to store plan")
        
        # Get plan
        retrieved_plan = plan_repo.get_user_plan("test_user_001")
        if retrieved_plan and retrieved_plan.plan_id == "plan_001":
            print("✅ Plan retrieved successfully")
        else:
            raise Exception("Failed to retrieve plan")
        
        # Test list operations
        users = user_repo.list_users(limit=10)
        print(f"✅ Listed {len(users)} users")
        
        # Test system status
        status = db_manager.get_connection_info()
        print(f"✅ Database status: {status}")
        
        # Clean up
        db_manager.disconnect()
        print("✅ Database disconnected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_types():
    """Test different database types"""
    try:
        print("\nTesting different database types...")
        
        from aurawell.database.connection import DatabaseManager, DatabaseConfig, DatabaseType
        
        # Test SQLite
        sqlite_config = DatabaseConfig(db_type=DatabaseType.SQLITE, file_path="test.db")
        sqlite_manager = DatabaseManager(sqlite_config)
        
        if sqlite_manager.connect():
            print("✅ SQLite connection successful")
            sqlite_manager.disconnect()
        else:
            print("❌ SQLite connection failed")
        
        # Clean up test file
        if os.path.exists("test.db"):
            os.remove("test.db")
        
        # Test Memory database
        memory_config = DatabaseConfig(db_type=DatabaseType.MEMORY)
        memory_manager = DatabaseManager(memory_config)
        
        if memory_manager.connect():
            print("✅ Memory database connection successful")
            memory_manager.disconnect()
        else:
            print("❌ Memory database connection failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Database types test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 AuraWell Database Layer Tests")
    print("=" * 50)
    
    success1 = test_database_layer()
    success2 = test_database_types()
    
    if success1 and success2:
        print("\n🎉 All database tests passed!")
    else:
        print("\n💥 Some database tests failed!")
        sys.exit(1)
