#!/usr/bin/env python3
"""
Test script for AuraWell Orchestrator v2
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_orchestrator_v2():
    """Test orchestrator v2"""
    try:
        print("Testing orchestrator v2 import...")
        
        # Set dummy API key to avoid initialization error
        os.environ['DEEPSEEK_API_KEY'] = 'test_key'
        
        from aurawell.core.orchestrator_v2 import AuraWellOrchestrator, HealthInsight, HealthPlan
        print("✅ Orchestrator v2 classes imported successfully")
        
        # Test basic initialization
        orchestrator = AuraWellOrchestrator()
        print("✅ Orchestrator v2 initialized successfully")
        
        # Test system status
        status = orchestrator.get_system_status()
        print(f"✅ System status: {status}")
        
        # Test with sample data
        user_profile = {
            'user_id': 'test_user_001',
            'age': 30,
            'gender': 'male',
            'daily_steps_goal': 10000,
            'sleep_duration_goal_hours': 8.0
        }
        
        activity_data = [
            {'steps': 8500, 'date': '2025-01-01'},
            {'steps': 9200, 'date': '2025-01-02'},
            {'steps': 7800, 'date': '2025-01-03'}
        ]
        
        sleep_data = [
            {'duration_hours': 7.5, 'date': '2025-01-01'},
            {'duration_hours': 6.8, 'date': '2025-01-02'},
            {'duration_hours': 8.2, 'date': '2025-01-03'}
        ]
        
        # Test health data analysis
        insights = orchestrator.analyze_user_health_data(
            user_profile=user_profile,
            activity_data=activity_data,
            sleep_data=sleep_data
        )
        print(f"✅ Generated {len(insights)} insights")
        
        for insight in insights:
            print(f"  - {insight.title} ({insight.priority.value})")
        
        # Test health plan creation
        health_plan = orchestrator.create_personalized_health_plan(
            user_profile=user_profile
        )
        print(f"✅ Created health plan: {health_plan.title}")
        
        # Test daily recommendations
        recommendations = orchestrator.get_daily_recommendations('test_user_001')
        print(f"✅ Generated {len(recommendations)} daily recommendations")
        
        for rec in recommendations:
            print(f"  - {rec['title']} ({rec['time']})")
        
        assert True  # Use assertion instead of return

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed: {e}"

if __name__ == "__main__":
    try:
        test_orchestrator_v2()
        print("\n🎉 All orchestrator v2 tests passed!")
    except AssertionError as e:
        print(f"\n💥 Orchestrator v2 tests failed: {e}")
        sys.exit(1)
