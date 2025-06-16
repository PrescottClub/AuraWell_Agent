"""
Comprehensive Permissions and Security Testing for AuraWell Family-Agent

Tests permission decorators, role-based access control, security validations,
and authorization mechanisms for family-related operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any, List

from src.aurawell.core.permissions import (
    require_family_permission,
    require_family_membership,
    require_owner,
    require_manager_or_owner,
    require_member,
    require_manager_or_self,
    FamilyPermissionChecker,
    check_family_permission,
    get_user_family_role,
    validate_family_access,
    audit_family_operation,
)
from src.aurawell.models.family_models import FamilyRole
from src.aurawell.core.exceptions import AurawellException, PermissionDeniedError


class TestPermissionDecorators:
    """Test permission decorator functionality"""

    @pytest.fixture
    def mock_permission_checker(self):
        """Mock permission checker for testing"""
        checker = AsyncMock(spec=FamilyPermissionChecker)
        return checker

    @pytest.fixture
    def mock_request_context(self):
        """Mock request context with user and family information"""
        return {
            "user_id": "user123",
            "family_id": "family123",
            "current_user": {"user_id": "user123", "username": "testuser"},
        }

    @pytest.mark.asyncio
    async def test_require_owner_decorator_success(self, mock_permission_checker):
        """Test require_owner decorator with valid owner"""

        @require_owner
        async def protected_function(family_id: str, user_id: str):
            return "success"

        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.OWNER

            result = await protected_function("family123", "user123")
            assert result == "success"
            mock_get_role.assert_called_once_with("user123", "family123")

    @pytest.mark.asyncio
    async def test_require_owner_decorator_failure(self, mock_permission_checker):
        """Test require_owner decorator with non-owner user"""

        @require_owner
        async def protected_function(family_id: str, user_id: str):
            return "success"

        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MEMBER

            with pytest.raises(PermissionDeniedError) as exc_info:
                await protected_function("family123", "user123")

            assert "Insufficient permissions" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_require_manager_or_owner_decorator(self, mock_permission_checker):
        """Test require_manager_or_owner decorator with different roles"""

        @require_manager_or_owner
        async def protected_function(family_id: str, user_id: str):
            return "success"

        # Test with OWNER role
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.OWNER
            result = await protected_function("family123", "user123")
            assert result == "success"

        # Test with MANAGER role
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MANAGER
            result = await protected_function("family123", "user123")
            assert result == "success"

        # Test with MEMBER role (should fail)
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MEMBER

            with pytest.raises(PermissionDeniedError):
                await protected_function("family123", "user123")

    @pytest.mark.asyncio
    async def test_require_member_decorator(self, mock_permission_checker):
        """Test require_member decorator for basic membership"""

        @require_member
        async def protected_function(family_id: str, user_id: str):
            return "success"

        # Test with any valid family role
        for role in [
            FamilyRole.OWNER,
            FamilyRole.MANAGER,
            FamilyRole.MEMBER,
            FamilyRole.VIEWER,
        ]:
            with patch(
                "aurawell.core.permissions.get_user_family_role"
            ) as mock_get_role:
                mock_get_role.return_value = role
                result = await protected_function("family123", "user123")
                assert result == "success"

        # Test with no role (not a member)
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = None

            with pytest.raises(PermissionDeniedError):
                await protected_function("family123", "user123")

    @pytest.mark.asyncio
    async def test_require_manager_or_self_decorator(self, mock_permission_checker):
        """Test require_manager_or_self decorator with self-access allowance"""

        @require_manager_or_self
        async def protected_function(
            family_id: str, user_id: str, target_user_id: str = None
        ):
            return "success"

        # Test manager accessing other user's data
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MANAGER
            result = await protected_function("family123", "user123", "other_user")
            assert result == "success"

        # Test user accessing their own data
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MEMBER
            result = await protected_function("family123", "user123", "user123")
            assert result == "success"

        # Test member accessing other user's data (should fail)
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MEMBER

            with pytest.raises(PermissionDeniedError):
                await protected_function("family123", "user123", "other_user")


class TestFamilyPermissionChecker:
    """Test FamilyPermissionChecker class functionality"""

    @pytest.fixture
    def permission_checker(self):
        """Create FamilyPermissionChecker instance"""
        mock_db = AsyncMock()
        return FamilyPermissionChecker(database_manager=mock_db)

    @pytest.mark.asyncio
    async def test_check_family_permission_valid_owner(self, permission_checker):
        """Test permission checking for valid owner"""
        with patch.object(permission_checker, "get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.OWNER

            result = await permission_checker.check_family_permission(
                "user123", "family123", [FamilyRole.OWNER]
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_check_family_permission_insufficient_role(self, permission_checker):
        """Test permission checking with insufficient role"""
        with patch.object(permission_checker, "get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MEMBER

            result = await permission_checker.check_family_permission(
                "user123", "family123", [FamilyRole.OWNER, FamilyRole.MANAGER]
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_family_access_success(self, permission_checker):
        """Test successful family access validation"""
        with patch.object(permission_checker, "get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MEMBER

            # Should not raise exception
            await permission_checker.validate_family_access("user123", "family123")

    @pytest.mark.asyncio
    async def test_validate_family_access_failure(self, permission_checker):
        """Test failed family access validation"""
        with patch.object(permission_checker, "get_user_family_role") as mock_get_role:
            mock_get_role.return_value = None  # Not a member

            with pytest.raises(PermissionDeniedError):
                await permission_checker.validate_family_access("user123", "family123")

    @pytest.mark.asyncio
    async def test_get_user_family_role_caching(self, permission_checker):
        """Test role caching mechanism"""
        mock_repo = AsyncMock()
        mock_repo.get_family_member.return_value = {"role": FamilyRole.MANAGER}

        with patch.object(
            permission_checker, "_get_family_repository", return_value=mock_repo
        ):
            # First call
            role1 = await permission_checker.get_user_family_role(
                "user123", "family123"
            )
            # Second call (should use cache)
            role2 = await permission_checker.get_user_family_role(
                "user123", "family123"
            )

            assert role1 == FamilyRole.MANAGER
            assert role2 == FamilyRole.MANAGER
            # Repository should only be called once due to caching
            mock_repo.get_family_member.assert_called_once()


class TestSecurityValidations:
    """Test security validation functions"""

    @pytest.mark.asyncio
    async def test_audit_family_operation_logging(self):
        """Test audit logging for family operations"""
        mock_audit_logger = AsyncMock()

        with patch("aurawell.core.permissions.audit_logger", mock_audit_logger):
            await audit_family_operation(
                user_id="user123",
                family_id="family123",
                operation="delete_member",
                details={"target_user": "member456"},
                success=True,
            )

            mock_audit_logger.info.assert_called_once()
            call_args = mock_audit_logger.info.call_args[0][0]
            assert "user123" in call_args
            assert "family123" in call_args
            assert "delete_member" in call_args

    @pytest.mark.asyncio
    async def test_audit_family_operation_failure_logging(self):
        """Test audit logging for failed family operations"""
        mock_audit_logger = AsyncMock()

        with patch("aurawell.core.permissions.audit_logger", mock_audit_logger):
            await audit_family_operation(
                user_id="user123",
                family_id="family123",
                operation="transfer_ownership",
                details={"error": "Insufficient permissions"},
                success=False,
            )

            mock_audit_logger.warning.assert_called_once()
            call_args = mock_audit_logger.warning.call_args[0][0]
            assert "FAILED" in call_args
            assert "transfer_ownership" in call_args

    def test_role_hierarchy_validation(self):
        """Test role hierarchy validation logic"""
        # Test role hierarchy order
        roles_by_power = [
            FamilyRole.VIEWER,
            FamilyRole.MEMBER,
            FamilyRole.MANAGER,
            FamilyRole.OWNER,
        ]

        for i, role in enumerate(roles_by_power):
            # Each role should have power >= all previous roles
            for j in range(i):
                lower_role = roles_by_power[j]
                assert (
                    role.value >= lower_role.value
                ), f"{role} should have >= power than {lower_role}"

    @pytest.mark.asyncio
    async def test_permission_injection_prevention(self):
        """Test prevention of permission injection attacks"""
        # Test that malicious role values are rejected
        malicious_inputs = [
            "'; DROP TABLE families; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "OWNER'; UPDATE families SET owner_id='attacker'--",
        ]

        for malicious_input in malicious_inputs:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                # This should fail when trying to convert to FamilyRole enum
                FamilyRole(malicious_input)

    @pytest.mark.asyncio
    async def test_concurrent_permission_checks(self):
        """Test concurrent permission checks for race conditions"""
        permission_checker = FamilyPermissionChecker(AsyncMock())

        async def check_permission():
            with patch.object(
                permission_checker, "get_user_family_role"
            ) as mock_get_role:
                mock_get_role.return_value = FamilyRole.MEMBER
                return await permission_checker.check_family_permission(
                    "user123", "family123", [FamilyRole.MEMBER]
                )

        # Run multiple concurrent permission checks
        import asyncio

        tasks = [check_permission() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(results)

    @pytest.mark.asyncio
    async def test_permission_cache_invalidation(self):
        """Test permission cache invalidation on role changes"""
        permission_checker = FamilyPermissionChecker(AsyncMock())

        mock_repo = AsyncMock()

        with patch.object(
            permission_checker, "_get_family_repository", return_value=mock_repo
        ):
            # First call returns MEMBER
            mock_repo.get_family_member.return_value = {"role": FamilyRole.MEMBER}
            role1 = await permission_checker.get_user_family_role(
                "user123", "family123"
            )

            # Simulate role change and cache invalidation
            permission_checker.invalidate_role_cache("user123", "family123")

            # Second call returns MANAGER
            mock_repo.get_family_member.return_value = {"role": FamilyRole.MANAGER}
            role2 = await permission_checker.get_user_family_role(
                "user123", "family123"
            )

            assert role1 == FamilyRole.MEMBER
            assert role2 == FamilyRole.MANAGER
            assert mock_repo.get_family_member.call_count == 2


class TestSecurityEdgeCases:
    """Test security edge cases and attack scenarios"""

    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation attacks"""

        @require_family_permission([FamilyRole.OWNER])
        async def sensitive_operation(family_id: str, user_id: str):
            return "sensitive_data"

        # Test that a MEMBER cannot escalate to OWNER
        with patch("aurawell.core.permissions.get_user_family_role") as mock_get_role:
            mock_get_role.return_value = FamilyRole.MEMBER

            with pytest.raises(PermissionDeniedError):
                await sensitive_operation("family123", "user123")

    @pytest.mark.asyncio
    async def test_family_id_spoofing_prevention(self):
        """Test prevention of family ID spoofing attacks"""
        permission_checker = FamilyPermissionChecker(AsyncMock())

        # Test that user cannot access family they're not a member of
        mock_repo = AsyncMock()
        mock_repo.get_family_member.return_value = None  # Not a member

        with patch.object(
            permission_checker, "_get_family_repository", return_value=mock_repo
        ):
            with pytest.raises(PermissionDeniedError):
                await permission_checker.validate_family_access(
                    "user123", "other_family"
                )

    @pytest.mark.asyncio
    async def test_session_hijacking_protection(self):
        """Test protection against session hijacking"""
        # This would typically involve JWT token validation
        # For now, test that user_id validation is strict

        invalid_user_ids = [None, "", "   ", "null", "undefined"]

        for invalid_id in invalid_user_ids:
            with pytest.raises((ValueError, PermissionDeniedError, TypeError)):
                await check_family_permission(
                    invalid_id, "family123", [FamilyRole.MEMBER]
                )


@pytest.fixture
def sample_permission_data():
    """Fixture providing sample permission data for testing"""
    return {
        "user_id": "user123",
        "family_id": "family123",
        "owner_id": "owner123",
        "manager_id": "manager123",
        "member_id": "member123",
        "viewer_id": "viewer123",
    }
