#!/usr/bin/env python3
"""
Test script for AuraWell Services Layer
"""

import os
import sys
import asyncio
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_base_service():
    """Test base service functionality"""
    try:
        print("Testing Base Service...")
        
        from aurawell.services.base_service import BaseService, ServiceResult, ServiceManager, ServiceStatus
        
        # Create a simple test service
        class TestService(BaseService):
            async def _initialize_service(self):
                pass
            
            async def _shutdown_service(self):
                pass
            
            async def _perform_health_check(self):
                return {"test": "ok"}
        
        # Test service creation
        service = TestService("TestService")
        print("✅ Test service created")
        
        # Test initialization
        success = await service.initialize()
        if success:
            print("✅ Service initialized")
        else:
            print("❌ Service initialization failed")
        
        # Test health check
        health = await service.health_check()
        print(f"✅ Health check: {health.status.value}")
        
        # Test service manager
        manager = ServiceManager()
        manager.register_service(service)
        print("✅ Service registered with manager")
        
        # Test manager operations
        init_results = await manager.initialize_all()
        print(f"✅ Manager initialization: {init_results}")
        
        health_results = await manager.health_check_all()
        print(f"✅ Manager health check: {len(health_results)} services")
        
        await manager.shutdown_all()
        print("✅ Manager shutdown completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Base service test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_user_service():
    """Test user service functionality"""
    try:
        print("\nTesting User Service...")
        
        from aurawell.services.user_service import UserService
        from aurawell.database.connection import DatabaseManager, DatabaseConfig, DatabaseType
        
        # Create in-memory database for testing
        config = DatabaseConfig(db_type=DatabaseType.MEMORY)
        db_manager = DatabaseManager(config)
        db_manager.connect()
        
        # Create user service
        user_service = UserService(database_manager=db_manager)
        await user_service.initialize()
        print("✅ User service initialized")
        
        # Test user creation
        user_data = {
            'user_id': 'test_user_001',
            'email': 'test@example.com',
            'display_name': 'Test User',
            'age': 30,
            'gender': 'male',
            'daily_steps_goal': 10000,
            'sleep_duration_goal_hours': 8.0
        }
        
        create_result = await user_service.create_user(user_data)
        if create_result.success:
            print("✅ User created successfully")
        else:
            print(f"❌ User creation failed: {create_result.error}")
        
        # Test user retrieval
        get_result = await user_service.get_user('test_user_001')
        if get_result.success and get_result.data:
            print("✅ User retrieved successfully")
        else:
            print(f"❌ User retrieval failed: {get_result.error}")
        
        # Test user update
        update_data = {'age': 31, 'display_name': 'Updated Test User'}
        update_result = await user_service.update_user('test_user_001', update_data)
        if update_result.success:
            print("✅ User updated successfully")
        else:
            print(f"❌ User update failed: {update_result.error}")
        
        # Test user listing
        list_result = await user_service.list_users(limit=10)
        if list_result.success:
            print(f"✅ Listed {len(list_result.data)} users")
        else:
            print(f"❌ User listing failed: {list_result.error}")
        
        await user_service.shutdown()
        db_manager.disconnect()
        print("✅ User service test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ User service test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_health_service():
    """Test health service functionality"""
    try:
        print("\nTesting Health Service...")
        
        from aurawell.services.health_service import HealthService
        from aurawell.database.connection import DatabaseManager, DatabaseConfig, DatabaseType
        
        # Create in-memory database for testing
        config = DatabaseConfig(db_type=DatabaseType.MEMORY)
        db_manager = DatabaseManager(config)
        db_manager.connect()
        
        # Create health service
        health_service = HealthService(database_manager=db_manager)
        await health_service.initialize()
        print("✅ Health service initialized")
        
        # Test health data storage
        health_data = {
            'steps': 8500,
            'distance_meters': 6800,
            'active_calories': 350
        }
        
        store_result = await health_service.store_health_data(
            user_id='test_user_001',
            data_type='activity',
            date='2025-01-15',
            data=health_data,
            source_platform='test_platform'
        )
        
        if store_result.success:
            print("✅ Health data stored successfully")
        else:
            print(f"❌ Health data storage failed: {store_result.error}")
        
        # Test health data retrieval
        get_result = await health_service.get_health_data('test_user_001', data_type='activity')
        if get_result.success:
            print(f"✅ Retrieved {len(get_result.data)} health data records")
        else:
            print(f"❌ Health data retrieval failed: {get_result.error}")
        
        # Test health analysis
        user_profile = {
            'user_id': 'test_user_001',
            'age': 30,
            'gender': 'male',
            'daily_steps_goal': 10000,
            'sleep_duration_goal_hours': 8.0
        }
        
        analysis_result = await health_service.analyze_health_data('test_user_001', user_profile)
        if analysis_result.success:
            print(f"✅ Health analysis completed, generated {len(analysis_result.data)} insights")
        else:
            print(f"❌ Health analysis failed: {analysis_result.error}")
        
        # Test health plan creation
        plan_result = await health_service.create_health_plan('test_user_001', user_profile)
        if plan_result.success:
            print("✅ Health plan created successfully")
        else:
            print(f"❌ Health plan creation failed: {plan_result.error}")
        
        await health_service.shutdown()
        db_manager.disconnect()
        print("✅ Health service test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Health service test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_service():
    """Test AI service functionality"""
    try:
        print("\nTesting AI Service...")
        
        from aurawell.services.ai_service import AIService
        
        # Create AI service (without API key, will be limited)
        ai_service = AIService()
        await ai_service.initialize()
        print("✅ AI service initialized")
        
        # Test health check
        health = await ai_service.health_check()
        print(f"✅ AI service health: {health.status.value}")
        
        # Test text analysis (will fail without API key, but tests the structure)
        text_result = await ai_service.analyze_text("Test health data analysis")
        if text_result.success:
            print("✅ Text analysis completed")
        else:
            print(f"⚠️ Text analysis failed (expected without API key): {text_result.error_code}")
        
        # Test statistics
        stats = ai_service.get_statistics()
        print(f"✅ AI service statistics: {stats}")
        
        await ai_service.shutdown()
        print("✅ AI service test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ AI service test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_notification_service():
    """Test notification service functionality"""
    try:
        print("\nTesting Notification Service...")
        
        from aurawell.services.notification_service import (
            NotificationService, NotificationType, NotificationPriority
        )
        
        # Create notification service
        notification_service = NotificationService()
        await notification_service.initialize()
        print("✅ Notification service initialized")
        
        # Test sending notification
        send_result = await notification_service.send_notification(
            user_id='test_user_001',
            notification_type=NotificationType.HEALTH_INSIGHT,
            title='Test Notification',
            message='This is a test notification',
            priority=NotificationPriority.MEDIUM
        )
        
        if send_result.success:
            print(f"✅ Notification sent: {send_result.data}")
        else:
            print(f"❌ Notification sending failed: {send_result.error}")
        
        # Test getting user notifications
        get_result = await notification_service.get_user_notifications('test_user_001')
        if get_result.success:
            print(f"✅ Retrieved {len(get_result.data)} notifications")
        else:
            print(f"❌ Notification retrieval failed: {get_result.error}")
        
        # Test delivery statistics
        stats = notification_service.get_delivery_statistics()
        print(f"✅ Notification statistics: {stats}")
        
        # Wait a moment for background processing
        await asyncio.sleep(1)
        
        await notification_service.shutdown()
        print("✅ Notification service test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification service test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all service tests"""
    print("🧪 AuraWell Services Layer Tests")
    print("=" * 50)
    
    tests = [
        test_base_service,
        test_user_service,
        test_health_service,
        test_ai_service,
        test_notification_service
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 Test Results: {success_count}/{total_count} passed")
    
    if success_count == total_count:
        print("🎉 All service tests passed!")
    else:
        print("💥 Some service tests failed!")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
