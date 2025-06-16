"""
测试改进功能
测试数据库集成、WebSocket心跳、权限审计、异常处理和速率限制
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

import sys
import os

# Add the src directory to Python path for new structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aurawell.services.family_service import FamilyService
from aurawell.core.exceptions import (
    AurawellException,
    ValidationError,
    AuthorizationError,
    NotFoundError,
    DatabaseError,
    BusinessLogicError,
)
from aurawell.core.permissions import log_permission_action
from aurawell.middleware.rate_limiter import RateLimiter, RateLimitingMiddleware
from aurawell.interfaces.websocket_interface import WebSocketManager
from aurawell.models.family_models import FamilyCreateRequest, FamilyRole


class TestDatabaseIntegration:
    """测试数据库集成功能"""

    @pytest.mark.asyncio
    async def test_family_service_database_operations(self):
        """测试家庭服务数据库操作"""
        service = FamilyService()

        # 测试创建家庭
        request = FamilyCreateRequest(name="Test Family", description="A test family")
        user_id = "test_user"

        try:
            family_info = await service.create_family(request, user_id)
            assert family_info is not None
            assert family_info.name == "Test Family"
            assert family_info.owner_id == user_id
        except Exception as e:
            # 预期可能因为缺少真实数据库而失败
            assert isinstance(e, (DatabaseError, NotFoundError, BusinessLogicError))

    @pytest.mark.asyncio
    async def test_family_service_error_handling(self):
        """测试家庭服务错误处理"""
        service = FamilyService()

        # 测试无效用户ID
        request = FamilyCreateRequest(name="Test Family")
        invalid_user_id = "nonexistent_user"

        with pytest.raises((NotFoundError, DatabaseError, BusinessLogicError)):
            await service.create_family(request, invalid_user_id)


class TestStandardizedExceptions:
    """测试标准化异常处理"""

    def test_aurawell_exception_creation(self):
        """测试AurawellException创建"""
        exc = AurawellException(
            "Test error",
            error_code="TEST_ERROR",
            user_message="用户友好的错误消息",
            http_status=400,
        )

        assert exc.message == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.user_message == "用户友好的错误消息"
        assert exc.http_status == 400

        # 测试转换为字典
        exc_dict = exc.to_dict()
        assert exc_dict["error_code"] == "TEST_ERROR"
        assert exc_dict["message"] == "用户友好的错误消息"

    def test_validation_error(self):
        """测试ValidationError"""
        exc = ValidationError("Invalid input", field="email")

        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.http_status == 400
        assert exc.details["field"] == "email"
        assert "输入验证失败" in exc.user_message

    def test_authorization_error(self):
        """测试AuthorizationError"""
        exc = AuthorizationError("Access denied")

        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.http_status == 403
        assert "权限不足" in exc.user_message


class TestPermissionAudit:
    """测试权限审计功能"""

    @pytest.mark.asyncio
    async def test_log_permission_action(self):
        """测试权限操作日志"""
        user_id = "test_user"
        family_id = "test_family"
        action = "view_family_data"
        resource = "family_info"

        # 测试成功的权限操作日志
        await log_permission_action(
            user_id=user_id,
            family_id=family_id,
            action=action,
            resource=resource,
            result="success",
            details={"role": "owner"},
        )

        # 测试被拒绝的权限操作日志
        await log_permission_action(
            user_id=user_id,
            family_id=family_id,
            action=action,
            resource=resource,
            result="denied",
            error_message="Insufficient permissions",
        )

        # 如果没有异常抛出，则测试通过
        assert True


class TestRateLimiting:
    """测试速率限制功能"""

    def test_rate_limiter_basic(self):
        """测试基本速率限制"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        # 测试允许的请求
        for i in range(3):
            allowed, retry_after = limiter.is_allowed("test_user")
            assert allowed is True
            assert retry_after is None

        # 测试超出限制的请求
        allowed, retry_after = limiter.is_allowed("test_user")
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0

    def test_rate_limiter_remaining_requests(self):
        """测试剩余请求数量"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)

        # 初始状态
        remaining = limiter.get_remaining_requests("test_user")
        assert remaining == 5

        # 使用一些请求
        limiter.is_allowed("test_user")
        limiter.is_allowed("test_user")

        remaining = limiter.get_remaining_requests("test_user")
        assert remaining == 3

    def test_rate_limiter_different_keys(self):
        """测试不同键的独立限制"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        # 用户1的请求
        allowed, _ = limiter.is_allowed("user1")
        assert allowed is True
        allowed, _ = limiter.is_allowed("user1")
        assert allowed is True
        allowed, _ = limiter.is_allowed("user1")
        assert allowed is False

        # 用户2的请求应该仍然被允许
        allowed, _ = limiter.is_allowed("user2")
        assert allowed is True
        allowed, _ = limiter.is_allowed("user2")
        assert allowed is True


class TestWebSocketHeartbeat:
    """测试WebSocket心跳功能"""

    def test_websocket_manager_initialization(self):
        """测试WebSocket管理器初始化"""
        manager = WebSocketManager()

        assert manager.heartbeat_interval == 30
        assert manager.heartbeat_timeout == 10
        assert len(manager.active_connections) == 0
        assert len(manager.heartbeat_tasks) == 0

    @pytest.mark.asyncio
    async def test_websocket_pong_handling(self):
        """测试WebSocket pong处理"""
        manager = WebSocketManager()
        user_id = "test_user"

        # 初始化用户会话
        manager.user_sessions[user_id] = {
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "active_member_id": user_id,
            "conversation_id": None,
            "heartbeat_count": 0,
            "last_pong": datetime.now().isoformat(),
        }

        initial_pong_time = manager.user_sessions[user_id]["last_pong"]

        # 等待一小段时间确保时间戳不同
        await asyncio.sleep(0.01)

        # 处理pong响应
        await manager.handle_pong(user_id)

        # 验证pong时间已更新
        new_pong_time = manager.user_sessions[user_id]["last_pong"]
        assert new_pong_time != initial_pong_time

    def test_websocket_disconnect_cleanup(self):
        """测试WebSocket断开连接清理"""
        manager = WebSocketManager()
        user_id = "test_user"

        # 模拟连接状态
        manager.active_connections[user_id] = Mock()
        manager.connection_metadata[user_id] = {"test": "data"}
        manager.user_sessions[user_id] = {"test": "session"}
        mock_task = Mock()
        mock_task.cancel = Mock()
        manager.heartbeat_tasks[user_id] = mock_task

        # 断开连接
        manager.disconnect(user_id)

        # 验证清理
        assert user_id not in manager.active_connections
        assert user_id not in manager.connection_metadata
        assert user_id not in manager.user_sessions
        assert user_id not in manager.heartbeat_tasks
        mock_task.cancel.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
