#!/usr/bin/env python3
"""
Test script for AuraWell Orchestrator
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_orchestrator_import():
    """Test orchestrator import"""
    try:
        print("Testing orchestrator import...")
        
        # Set dummy API key to avoid initialization error
        os.environ['DEEPSEEK_API_KEY'] = 'test_key'
        
        from aurawell.core.orchestrator_v2 import AuraWellOrchestrator, HealthInsight, HealthPlan
        print("✅ Orchestrator classes imported successfully")
        
        # Test basic initialization
        orchestrator = AuraWellOrchestrator()
        print("✅ Orchestrator initialized successfully")
        
        # Test system status
        status = orchestrator.get_system_status()
        print(f"✅ System status: {status}")
        
        assert True  # Use assertion instead of return
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Test failed: {e}"

if __name__ == "__main__":
    try:
        test_orchestrator_import()
        print("\n🎉 All orchestrator tests passed!")
    except AssertionError as e:
        print(f"\n💥 Orchestrator tests failed: {e}")
        sys.exit(1)
