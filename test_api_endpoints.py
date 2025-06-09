#!/usr/bin/env python3
"""
Simple API Endpoints Test Script

Tests all AuraWell API endpoints to verify they are working correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing AuraWell API Endpoints")
    print("=" * 50)
    
    try:
        # Import FastAPI app and test client
        from aurawell.interfaces.api_interface import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        print("✅ FastAPI app and test client created successfully")
        
        # Test results
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "endpoints": []
        }
        
        # 1. Test System Endpoints (Public)
        print("\n📋 Testing System Endpoints...")
        
        # Health check
        try:
            response = client.get("/api/v1/health")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            results["endpoints"].append({"endpoint": "GET /api/v1/health", "status": status})
            results["total_tests"] += 1
            if response.status_code == 200:
                results["passed"] += 1
            else:
                results["failed"] += 1
            print(f"  Health Check: {status}")
        except Exception as e:
            print(f"  Health Check: ❌ ERROR - {e}")
            results["failed"] += 1
            results["total_tests"] += 1
        
        # Root endpoint
        try:
            response = client.get("/")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            results["endpoints"].append({"endpoint": "GET /", "status": status})
            results["total_tests"] += 1
            if response.status_code == 200:
                results["passed"] += 1
            else:
                results["failed"] += 1
            print(f"  Root Endpoint: {status}")
        except Exception as e:
            print(f"  Root Endpoint: ❌ ERROR - {e}")
            results["failed"] += 1
            results["total_tests"] += 1
        
        # 2. Test Authentication Endpoint
        print("\n🔐 Testing Authentication...")
        
        token = None
        try:
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "demo_user", "password": "demo_password"}
            )
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            results["endpoints"].append({"endpoint": "POST /api/v1/auth/login", "status": status})
            results["total_tests"] += 1
            if response.status_code == 200:
                results["passed"] += 1
                data = response.json()
                token = data["data"]["access_token"]
                print(f"  Login: {status} (Token obtained)")
            else:
                results["failed"] += 1
                print(f"  Login: {status}")
        except Exception as e:
            print(f"  Login: ❌ ERROR - {e}")
            results["failed"] += 1
            results["total_tests"] += 1
        
        # Test invalid login
        try:
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "invalid", "password": "invalid"}
            )
            status = "✅ PASS" if response.status_code == 401 else f"❌ FAIL ({response.status_code})"
            results["endpoints"].append({"endpoint": "POST /api/v1/auth/login (invalid)", "status": status})
            results["total_tests"] += 1
            if response.status_code == 401:
                results["passed"] += 1
            else:
                results["failed"] += 1
            print(f"  Invalid Login: {status}")
        except Exception as e:
            print(f"  Invalid Login: ❌ ERROR - {e}")
            results["failed"] += 1
            results["total_tests"] += 1
        
        # 3. Test Protected Endpoints (if token available)
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            print("\n🔒 Testing Protected Endpoints...")
            
            # Test endpoints that require authentication
            protected_endpoints = [
                ("GET", "/api/v1/user/profile", "User Profile Get"),
                ("GET", "/api/v1/health/summary", "Health Summary"),
                ("GET", "/api/v1/health/goals", "Health Goals"),
                ("GET", "/api/v1/achievements", "Achievements"),
                ("GET", "/api/v1/health/activity", "Activity Data"),
                ("GET", "/api/v1/health/sleep", "Sleep Data"),
            ]
            
            for method, endpoint, name in protected_endpoints:
                try:
                    if method == "GET":
                        response = client.get(endpoint, headers=headers)
                    elif method == "POST":
                        response = client.post(endpoint, headers=headers, json={})
                    
                    status = "✅ PASS" if response.status_code in [200, 201] else f"❌ FAIL ({response.status_code})"
                    results["endpoints"].append({"endpoint": f"{method} {endpoint}", "status": status})
                    results["total_tests"] += 1
                    if response.status_code in [200, 201]:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                    print(f"  {name}: {status}")
                except Exception as e:
                    print(f"  {name}: ❌ ERROR - {e}")
                    results["failed"] += 1
                    results["total_tests"] += 1
        
        # 4. Test API Documentation
        print("\n📚 Testing API Documentation...")
        
        # OpenAPI schema
        try:
            response = client.get("/openapi.json")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            results["endpoints"].append({"endpoint": "GET /openapi.json", "status": status})
            results["total_tests"] += 1
            if response.status_code == 200:
                results["passed"] += 1
                schema = response.json()
                print(f"  OpenAPI Schema: {status} (Title: {schema.get('info', {}).get('title', 'N/A')})")
            else:
                results["failed"] += 1
                print(f"  OpenAPI Schema: {status}")
        except Exception as e:
            print(f"  OpenAPI Schema: ❌ ERROR - {e}")
            results["failed"] += 1
            results["total_tests"] += 1
        
        # Swagger UI
        try:
            response = client.get("/docs")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            results["endpoints"].append({"endpoint": "GET /docs", "status": status})
            results["total_tests"] += 1
            if response.status_code == 200:
                results["passed"] += 1
            else:
                results["failed"] += 1
            print(f"  Swagger UI: {status}")
        except Exception as e:
            print(f"  Swagger UI: ❌ ERROR - {e}")
            results["failed"] += 1
            results["total_tests"] += 1
        
        # ReDoc
        try:
            response = client.get("/redoc")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            results["endpoints"].append({"endpoint": "GET /redoc", "status": status})
            results["total_tests"] += 1
            if response.status_code == 200:
                results["passed"] += 1
            else:
                results["failed"] += 1
            print(f"  ReDoc: {status}")
        except Exception as e:
            print(f"  ReDoc: ❌ ERROR - {e}")
            results["failed"] += 1
            results["total_tests"] += 1
        
        return results
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install fastapi uvicorn pydantic")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = test_api_endpoints()
    if results:
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']} ✅")
        print(f"Failed: {results['failed']} ❌")
        print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
        
        if results['failed'] > 0:
            print("\n❌ Failed Endpoints:")
            for endpoint in results['endpoints']:
                if "FAIL" in endpoint['status'] or "ERROR" in endpoint['status']:
                    print(f"  - {endpoint['endpoint']}: {endpoint['status']}")
        
        sys.exit(0 if results['failed'] == 0 else 1)
    else:
        sys.exit(1)
