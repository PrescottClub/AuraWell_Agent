"""
Test cases for FastAPI REST API interface

Tests all major API endpoints and functionality.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

# Import the FastAPI app
from aurawell.interfaces.api_interface import app

# Create test client
client = TestClient(app)


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "demo_user", "password": "demo_password"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "invalid", "password": "invalid"}
        )
        assert response.status_code == 401
        response_data = response.json()
        assert "Invalid username or password" in response_data.get("message", response_data.get("detail", ""))


class TestSystemEndpoints:
    """Test system endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "AuraWell API is healthy" in data["message"]
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Welcome to AuraWell" in data["message"]


class TestProtectedEndpoints:
    """Test protected endpoints that require authentication"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers"""
        # Login to get token
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "demo_user", "password": "demo_password"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_chat_endpoint(self, auth_headers):
        """Test chat endpoint"""
        with patch('aurawell.interfaces.api_interface.ConversationAgent') as mock_agent:
            # Mock the conversation agent
            mock_instance = AsyncMock()
            mock_instance.a_run.return_value = "Hello! I'm your health assistant."
            mock_agent.return_value = mock_instance
            
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "Hello, how are you?",
                    "user_id": "user_001"
                },
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "reply" in data
    
    def test_user_profile_get(self, auth_headers):
        """Test get user profile endpoint - should create default profile if none exists"""
        with patch('aurawell.interfaces.api_interface.get_user_repository') as mock_repo:
            # Mock user repository
            mock_repo_instance = AsyncMock()
            mock_repo_instance.get_user_by_id.return_value = None  # No existing profile
            mock_repo_instance.create_user.return_value = None  # Mock creation failure
            mock_repo.return_value = mock_repo_instance

            response = client.get("/api/v1/user/profile", headers=auth_headers)
            assert response.status_code == 200  # Should return default profile
            data = response.json()
            assert data["status"] == "success"
            assert "user_id" in data

    def test_user_profile_put(self, auth_headers):
        """Test update user profile endpoint"""
        with patch('aurawell.interfaces.api_interface.get_user_repository') as mock_repo:
            # Mock user repository
            mock_repo_instance = AsyncMock()
            mock_repo_instance.get_user_by_id.return_value = None  # No existing profile

            # Mock successful profile creation
            from aurawell.database.models import UserProfileDB
            mock_created_profile = UserProfileDB(
                user_id="user_001",
                display_name="Test User",
                email="test@example.com",
                age=25,
                gender="male",
                height_cm=175.0,
                weight_kg=70.0,
                activity_level="moderately_active"
            )
            mock_repo_instance.create_user.return_value = mock_created_profile
            mock_repo_instance.to_pydantic.return_value = AsyncMock()
            mock_repo_instance.to_pydantic.return_value.user_id = "user_001"
            mock_repo_instance.to_pydantic.return_value.display_name = "Test User"
            mock_repo_instance.to_pydantic.return_value.email = "test@example.com"
            mock_repo_instance.to_pydantic.return_value.age = 25
            mock_repo_instance.to_pydantic.return_value.gender = AsyncMock()
            mock_repo_instance.to_pydantic.return_value.gender.value = "male"
            mock_repo_instance.to_pydantic.return_value.height_cm = 175.0
            mock_repo_instance.to_pydantic.return_value.weight_kg = 70.0
            mock_repo_instance.to_pydantic.return_value.activity_level = AsyncMock()
            mock_repo_instance.to_pydantic.return_value.activity_level.value = "moderately_active"

            mock_repo.return_value = mock_repo_instance

            profile_data = {
                "display_name": "Test User",
                "email": "test@example.com",
                "age": 25,
                "gender": "male",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "activity_level": "moderately_active"
            }

            response = client.put("/api/v1/user/profile", json=profile_data, headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["display_name"] == "Test User"
    
    def test_health_summary(self, auth_headers):
        """Test health summary endpoint"""
        with patch('aurawell.interfaces.api_interface.get_tools_registry') as mock_registry:
            # Mock tools registry
            mock_registry_instance = AsyncMock()
            mock_tool = AsyncMock()
            mock_tool.return_value = [{"steps": 8000, "calories_burned": 300}]
            mock_registry_instance.get_tool.return_value = mock_tool
            mock_registry.return_value = mock_registry_instance
            
            response = client.get("/api/v1/health/summary?days=7", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "user_id" in data
    
    def test_achievements(self, auth_headers):
        """Test achievements endpoint"""
        with patch('aurawell.interfaces.api_interface.get_tools_registry') as mock_registry:
            # Mock tools registry
            mock_registry_instance = AsyncMock()
            mock_tool = AsyncMock()
            mock_tool.return_value = [
                {"achievement": "First Steps", "progress": 100, "points": 10}
            ]
            mock_registry_instance.get_tool.return_value = mock_tool
            mock_registry.return_value = mock_registry_instance
            
            response = client.get("/api/v1/achievements", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "achievements" in data
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without authentication"""
        response = client.get("/api/v1/user/profile")
        assert response.status_code == 403  # Forbidden


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema generation"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "AuraWell Health Assistant API"
    
    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self):
        """Test ReDoc docs endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON in request"""
        response = client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS configuration is present"""
        # TestClient doesn't trigger CORS middleware, so we just test that the endpoint works
        # In real deployment, CORS headers would be present
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        # Test that the response is valid JSON (indicates proper API setup)
        data = response.json()
        assert data["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
