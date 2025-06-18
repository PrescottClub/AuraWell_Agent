"""
家庭API接口单元测试

测试家庭创建、管理等API接口
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from aurawell.interfaces.api_interface import app
from aurawell.models.family_models import FamilyRole
from aurawell.core.exceptions import ValidationError, ConflictError, DatabaseError


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_family_service():
    """模拟家庭服务"""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_get_current_user_id():
    """模拟当前用户ID获取"""
    return str(uuid.uuid4())


@pytest.fixture
def sample_family_request():
    """示例家庭创建请求"""
    return {
        "name": "测试家庭",
        "description": "这是一个测试家庭"
    }


class TestFamilyAPI:
    """家庭API测试"""

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_create_family_success(self, mock_get_user_id, mock_get_service, client, sample_family_request):
        """测试成功创建家庭"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        family_id = str(uuid.uuid4())
        
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.create_family.return_value = {
            "family_id": family_id,
            "name": sample_family_request["name"],
            "description": sample_family_request["description"],
            "owner_id": user_id,
            "member_count": 1,
            "is_active": True
        }
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.post(
            "/api/v1/family",
            json=sample_family_request,
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["family_id"] == family_id
        assert data["data"]["name"] == sample_family_request["name"]

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_create_family_validation_error(self, mock_get_user_id, mock_get_service, client):
        """测试创建家庭时验证错误"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.create_family.side_effect = ValidationError("Family name is required")
        mock_get_service.return_value = mock_service
        
        # 发送无效请求
        response = client.post(
            "/api/v1/family",
            json={"description": "没有名称的家庭"},
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_create_family_conflict_error(self, mock_get_user_id, mock_get_service, client, sample_family_request):
        """测试创建家庭时冲突错误"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.create_family.side_effect = ConflictError("User already owns a family")
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.post(
            "/api/v1/family",
            json=sample_family_request,
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_409_CONFLICT

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_create_family_database_error(self, mock_get_user_id, mock_get_service, client, sample_family_request):
        """测试创建家庭时数据库错误"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.create_family.side_effect = DatabaseError("Database connection failed")
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.post(
            "/api/v1/family",
            json=sample_family_request,
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_create_family_unauthorized(self, client, sample_family_request):
        """测试未授权创建家庭"""
        # 发送无授权头的请求
        response = client.post(
            "/api/v1/family",
            json=sample_family_request
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_get_family_success(self, mock_get_user_id, mock_get_service, client):
        """测试成功获取家庭信息"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        family_id = str(uuid.uuid4())
        
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.get_family_details.return_value = {
            "family_id": family_id,
            "name": "测试家庭",
            "description": "测试描述",
            "owner_id": user_id,
            "member_count": 2,
            "members": [
                {
                    "user_id": user_id,
                    "username": "owner",
                    "role": FamilyRole.OWNER
                }
            ]
        }
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get(
            f"/api/v1/family/{family_id}",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["family_id"] == family_id
        assert data["data"]["name"] == "测试家庭"

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_get_family_not_found(self, mock_get_user_id, mock_get_service, client):
        """测试获取不存在的家庭"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        family_id = str(uuid.uuid4())
        
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.get_family_details.return_value = None
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get(
            f"/api/v1/family/{family_id}",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_invite_family_member_success(self, mock_get_user_id, mock_get_service, client):
        """测试成功邀请家庭成员"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        family_id = str(uuid.uuid4())
        
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.invite_member.return_value = {
            "invite_id": str(uuid.uuid4()),
            "invite_code": "ABC123",
            "expires_at": "2025-01-24T12:00:00Z"
        }
        mock_get_service.return_value = mock_service
        
        invite_request = {
            "email": "newmember@example.com",
            "role": "MEMBER",
            "message": "欢迎加入我们的家庭"
        }
        
        # 发送请求
        response = client.post(
            f"/api/v1/family/{family_id}/invite",
            json=invite_request,
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "invite_code" in data["data"]

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_join_family_success(self, mock_get_user_id, mock_get_service, client):
        """测试成功加入家庭"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.join_family.return_value = {
            "family_id": str(uuid.uuid4()),
            "member_id": str(uuid.uuid4()),
            "role": FamilyRole.MEMBER
        }
        mock_get_service.return_value = mock_service
        
        join_request = {
            "invite_code": "ABC123"
        }
        
        # 发送请求
        response = client.post(
            "/api/v1/family/join",
            json=join_request,
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "family_id" in data["data"]

    @patch('aurawell.interfaces.api_interface.get_family_service')
    @patch('aurawell.interfaces.api_interface.get_current_user_id')
    def test_get_user_families(self, mock_get_user_id, mock_get_service, client):
        """测试获取用户家庭列表"""
        # 设置模拟
        user_id = str(uuid.uuid4())
        
        mock_get_user_id.return_value = user_id
        
        mock_service = AsyncMock()
        mock_service.get_user_families.return_value = [
            {
                "family_id": str(uuid.uuid4()),
                "name": "家庭1",
                "role": FamilyRole.OWNER,
                "member_count": 3
            },
            {
                "family_id": str(uuid.uuid4()),
                "name": "家庭2",
                "role": FamilyRole.MEMBER,
                "member_count": 2
            }
        ]
        mock_get_service.return_value = mock_service
        
        # 发送请求
        response = client.get(
            "/api/v1/family/user/families",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "家庭1"
        assert data["data"][1]["name"] == "家庭2"


class TestFamilyAPIIntegration:
    """家庭API集成测试"""

    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
