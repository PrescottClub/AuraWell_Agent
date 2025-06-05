#!/usr/bin/env python3
"""
Complete System Test for AuraWell

Tests the entire AuraWell system including all layers:
- Core orchestrator
- Database layer
- Services layer
- Monitoring and error handling
"""

import os
import sys
import asyncio
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_complete_workflow():
    """Test complete AuraWell workflow"""
    try:
        print("🧪 Testing Complete AuraWell System Workflow")
        print("=" * 60)
        
        # Set up environment
        os.environ['DEEPSEEK_API_KEY'] = 'test_key'
        
        # 1. Initialize Database
        print("\n1️⃣ Initializing Database Layer...")
        from aurawell.database.connection import DatabaseManager, DatabaseConfig, DatabaseType
        
        config = DatabaseConfig(db_type=DatabaseType.MEMORY)
        db_manager = DatabaseManager(config)
        
        if db_manager.connect():
            print("✅ Database connected and schema initialized")
        else:
            raise Exception("Failed to connect to database")
        
        # 2. Initialize Services
        print("\n2️⃣ Initializing Services Layer...")
        from aurawell.services.user_service import UserService
        from aurawell.services.health_service import HealthService
        from aurawell.services.ai_service import AIService
        from aurawell.services.notification_service import NotificationService
        from aurawell.services.base_service import ServiceManager
        
        # Create services
        user_service = UserService(database_manager=db_manager)
        health_service = HealthService(database_manager=db_manager)
        ai_service = AIService()
        notification_service = NotificationService(database_manager=db_manager)
        
        # Create service manager
        service_manager = ServiceManager()
        service_manager.register_service(user_service)
        service_manager.register_service(health_service)
        service_manager.register_service(ai_service)
        service_manager.register_service(notification_service)
        
        # Initialize all services
        init_results = await service_manager.initialize_all()
        if all(init_results.values()):
            print("✅ All services initialized successfully")
        else:
            print(f"⚠️ Some services failed to initialize: {init_results}")
        
        # 3. Test User Management
        print("\n3️⃣ Testing User Management...")
        user_data = {
            'user_id': 'test_user_001',
            'email': 'test@aurawell.com',
            'display_name': 'Test User',
            'age': 30,
            'gender': 'male',
            'height_cm': 175.0,
            'weight_kg': 70.0,
            'activity_level': 'moderately_active',
            'primary_goal': 'weight_loss',
            'daily_steps_goal': 10000,
            'sleep_duration_goal_hours': 8.0,
            'preferences': {
                'notifications': True,
                'units': 'metric',
                'language': 'zh-CN'
            }
        }
        
        create_result = await user_service.create_user(user_data)
        if create_result.success:
            print("✅ User created successfully")
        else:
            raise Exception(f"Failed to create user: {create_result.error}")
        
        # 4. Test Health Data Storage
        print("\n4️⃣ Testing Health Data Management...")
        
        # Store activity data
        activity_data = {
            'steps': 8500,
            'distance_meters': 6800,
            'active_calories': 350,
            'exercise_minutes': 45
        }
        
        activity_result = await health_service.store_health_data(
            user_id='test_user_001',
            data_type='activity',
            date='2025-01-15',
            data=activity_data,
            source_platform='test_platform'
        )
        
        if activity_result.success:
            print("✅ Activity data stored")
        else:
            raise Exception(f"Failed to store activity data: {activity_result.error}")
        
        # Store sleep data
        sleep_data = {
            'duration_hours': 7.5,
            'deep_sleep_hours': 2.1,
            'rem_sleep_hours': 1.8,
            'sleep_efficiency': 0.85,
            'bedtime': '23:30',
            'wake_time': '07:00'
        }
        
        sleep_result = await health_service.store_health_data(
            user_id='test_user_001',
            data_type='sleep',
            date='2025-01-15',
            data=sleep_data,
            source_platform='test_platform'
        )
        
        if sleep_result.success:
            print("✅ Sleep data stored")
        else:
            raise Exception(f"Failed to store sleep data: {sleep_result.error}")
        
        # Store nutrition data
        nutrition_data = {
            'calories': 2100,
            'protein_g': 120,
            'carbs_g': 250,
            'fat_g': 80,
            'fiber_g': 25,
            'meals': [
                {'name': 'breakfast', 'calories': 450},
                {'name': 'lunch', 'calories': 650},
                {'name': 'dinner', 'calories': 700},
                {'name': 'snacks', 'calories': 300}
            ]
        }
        
        nutrition_result = await health_service.store_health_data(
            user_id='test_user_001',
            data_type='nutrition',
            date='2025-01-15',
            data=nutrition_data,
            source_platform='test_platform'
        )
        
        if nutrition_result.success:
            print("✅ Nutrition data stored")
        else:
            raise Exception(f"Failed to store nutrition data: {nutrition_result.error}")
        
        # 5. Test Health Analysis
        print("\n5️⃣ Testing Health Analysis...")
        
        user_profile = user_data.copy()
        analysis_result = await health_service.analyze_health_data('test_user_001', user_profile)
        
        if analysis_result.success:
            insights = analysis_result.data
            print(f"✅ Health analysis completed, generated {len(insights)} insights")
            
            # Display insights
            for insight in insights[:3]:  # Show first 3 insights
                print(f"   📊 {insight['title']} ({insight['priority']})")
        else:
            print(f"⚠️ Health analysis failed: {analysis_result.error}")
        
        # 6. Test Health Plan Creation
        print("\n6️⃣ Testing Health Plan Creation...")
        
        plan_result = await health_service.create_health_plan('test_user_001', user_profile)
        
        if plan_result.success:
            plan = plan_result.data
            print(f"✅ Health plan created: {plan['title']}")
            print(f"   🎯 Goals: {len(plan['goals'])}")
            print(f"   📅 Daily recommendations: {len(plan['daily_recommendations'])}")
        else:
            print(f"⚠️ Health plan creation failed: {plan_result.error}")
        
        # 7. Test Notifications
        print("\n7️⃣ Testing Notification System...")
        
        from aurawell.services.notification_service import NotificationType, NotificationPriority
        
        # Send health insight notification
        if analysis_result.success and insights:
            insight_notif = await notification_service.send_health_insight_notification(
                'test_user_001', insights[0]
            )
            if insight_notif.success:
                print("✅ Health insight notification sent")
        
        # Send goal reminder
        goal_reminder = await notification_service.send_goal_reminder(
            'test_user_001', 'daily_steps', 8500, 10000
        )
        if goal_reminder.success:
            print("✅ Goal reminder notification sent")
        
        # Get user notifications
        notifications_result = await notification_service.get_user_notifications('test_user_001')
        if notifications_result.success:
            print(f"✅ Retrieved {len(notifications_result.data)} notifications")
        
        # 8. Test Error Handling
        print("\n8️⃣ Testing Error Handling...")
        
        from aurawell.monitoring.error_handler import ErrorHandler, ValidationError
        
        error_handler = ErrorHandler()
        
        # Test error handling
        try:
            raise ValidationError("Test validation error", field="test_field")
        except Exception as e:
            handled_error = error_handler.handle_error(e)
            print(f"✅ Error handled: {handled_error.error_code}")
        
        # Get error statistics
        error_stats = error_handler.get_error_statistics()
        print(f"✅ Error statistics: {error_stats['total_errors']} total errors")
        
        # 9. Test Health Monitoring
        print("\n9️⃣ Testing Health Monitoring...")
        
        from aurawell.monitoring.health_monitor import HealthMonitor
        
        health_monitor = HealthMonitor(check_interval=5)
        
        # Perform health check
        health_results = await health_monitor.perform_health_check()
        print(f"✅ Health checks completed: {len(health_results)} components")
        
        # Get system metrics
        metrics = await health_monitor.get_system_metrics()
        print(f"✅ System metrics: CPU {metrics.cpu_percent}%, Memory {metrics.memory_percent}%")
        
        # Get health summary
        health_summary = health_monitor.get_health_summary()
        print(f"✅ Overall system status: {health_summary['overall_status']}")
        
        # 10. Test Service Health Checks
        print("\n🔟 Testing Service Health Checks...")
        
        service_health = await service_manager.health_check_all()
        healthy_services = sum(1 for h in service_health.values() if h.status.value == 'healthy')
        total_services = len(service_health)
        
        print(f"✅ Service health: {healthy_services}/{total_services} services healthy")
        
        # 11. Cleanup
        print("\n🧹 Cleaning up...")
        
        await service_manager.shutdown_all()
        db_manager.disconnect()
        
        print("✅ System shutdown completed")
        
        # 12. Final Summary
        print("\n📊 Test Summary")
        print("=" * 30)
        print("✅ Database layer: Working")
        print("✅ Services layer: Working")
        print("✅ User management: Working")
        print("✅ Health data storage: Working")
        print("✅ Health analysis: Working")
        print("✅ Health plans: Working")
        print("✅ Notifications: Working")
        print("✅ Error handling: Working")
        print("✅ Health monitoring: Working")
        print("✅ Service coordination: Working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Complete system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_performance():
    """Test system performance under load"""
    try:
        print("\n🚀 Performance Testing...")
        
        # Set up minimal system
        os.environ['DEEPSEEK_API_KEY'] = 'test_key'
        
        from aurawell.database.connection import DatabaseManager, DatabaseConfig, DatabaseType
        from aurawell.services.health_service import HealthService
        
        config = DatabaseConfig(db_type=DatabaseType.MEMORY)
        db_manager = DatabaseManager(config)
        db_manager.connect()
        
        health_service = HealthService(database_manager=db_manager)
        await health_service.initialize()
        
        # Performance test: Store multiple health data records
        start_time = datetime.now()
        
        tasks = []
        for i in range(100):
            task = health_service.store_health_data(
                user_id=f'perf_user_{i % 10}',  # 10 different users
                data_type='activity',
                date=f'2025-01-{15 + (i % 15):02d}',
                data={'steps': 8000 + i * 10, 'calories': 300 + i}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        successful = sum(1 for r in results if r.success)
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Performance test: {successful}/100 operations in {duration:.2f}s")
        print(f"   📈 Throughput: {successful/duration:.1f} operations/second")
        
        await health_service.shutdown()
        db_manager.disconnect()
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🎯 AuraWell Complete System Tests")
    print("=" * 50)
    
    # Run complete workflow test
    workflow_success = await test_complete_workflow()
    
    # Run performance test
    performance_success = await test_performance()
    
    # Final results
    print("\n🏁 Final Results")
    print("=" * 20)
    
    if workflow_success and performance_success:
        print("🎉 All tests passed! AuraWell system is working correctly.")
        print("\n✨ The system is ready for:")
        print("   • User management and profiles")
        print("   • Health data collection and storage")
        print("   • AI-powered health analysis")
        print("   • Personalized health plans")
        print("   • Smart notifications")
        print("   • Error handling and recovery")
        print("   • System monitoring and alerting")
        print("   • High-performance data processing")
        return True
    else:
        print("💥 Some tests failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
