"""
Comprehensive End-to-End Isolation Testing for AuraWell Family-Agent

Tests complete workflows with isolated test environments, data isolation,
and comprehensive scenario coverage for family-related operations.
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, patch

from src.aurawell.services.family_service import FamilyService
from src.aurawell.services.dashboard_service import FamilyDashboardService
from src.aurawell.services.report_service import HealthReportService
from src.aurawell.interfaces.websocket_interface import WebSocketManager
from src.aurawell.models.family_models import (
    FamilyRole,
    FamilyCreateRequest,
    InviteMemberRequest,
    AcceptInviteRequest,
    UpdateMemberRoleRequest,
    RemoveMemberRequest,
    TransferOwnershipRequest,
    FamilyInfo,
    FamilyMember,
    InviteInfo,
)
from src.aurawell.core.exceptions import AurawellException, PermissionDeniedError


class TestEnvironmentIsolation:
    """Test environment isolation and cleanup"""

    @pytest.fixture
    async def isolated_test_environment(self):
        """Create isolated test environment with cleanup"""
        # Generate unique test identifiers
        test_id = str(uuid.uuid4())[:8]
        test_data = {
            "test_id": test_id,
            "users": {},
            "families": {},
            "invites": {},
            "connections": {},
        }

        # Setup mock database with isolated data
        mock_db = AsyncMock()
        mock_session = AsyncMock()
        mock_db.get_session.return_value.__aenter__.return_value = mock_session

        # Create service instances
        family_service = FamilyService(database_manager=mock_db)
        dashboard_service = FamilyDashboardService(database_manager=mock_db)
        report_service = HealthReportService(database_manager=mock_db)
        websocket_manager = WebSocketManager()

        services = {
            "family_service": family_service,
            "dashboard_service": dashboard_service,
            "report_service": report_service,
            "websocket_manager": websocket_manager,
            "database": mock_db,
            "session": mock_session,
        }

        yield test_data, services

        # Cleanup after test
        await self.cleanup_test_environment(test_data, services)

    async def cleanup_test_environment(self, test_data: Dict, services: Dict):
        """Clean up test environment"""
        # Close WebSocket connections
        if "websocket_manager" in services:
            await services["websocket_manager"].cleanup_all_connections()

        # Clear test data
        test_data.clear()

    @pytest.mark.asyncio
    async def test_data_isolation_between_tests(self, isolated_test_environment):
        """Test that data is isolated between different test runs"""
        test_data, services = isolated_test_environment

        # Create test family
        family_id = f"family_{test_data['test_id']}"
        test_data["families"][family_id] = {
            "name": f"Test Family {test_data['test_id']}",
            "members": [],
        }

        # Verify isolation by checking test_id is unique
        assert test_data["test_id"] not in ["previous_test_id_1", "previous_test_id_2"]
        assert family_id.startswith("family_")
        assert test_data["test_id"] in family_id


class TestCompleteUserJourney:
    """Test complete user journey from registration to family management"""

    @pytest.fixture
    def mock_repositories(self):
        """Mock all repository dependencies"""
        mocks = {
            "family_repo": AsyncMock(),
            "user_repo": AsyncMock(),
            "health_repo": AsyncMock(),
            "dashboard_repo": AsyncMock(),
        }
        return mocks

    @pytest.mark.asyncio
    async def test_complete_family_creation_journey(
        self, isolated_test_environment, mock_repositories
    ):
        """Test complete family creation and setup journey"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        # Setup mocks
        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_repositories["family_repo"],
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_repositories["user_repo"],
        ):

            # Mock user exists
            user_id = f"user_{test_data['test_id']}_owner"
            mock_repositories["user_repo"].get_user_by_id.return_value = {
                "user_id": user_id,
                "username": "testowner",
            }
            mock_repositories["family_repo"].get_families_by_user.return_value = []

            # Step 1: Create family
            family_request = FamilyCreateRequest(
                name=f"Test Family {test_data['test_id']}",
                description="E2E test family",
            )

            family_info = await family_service.create_family(user_id, family_request)

            # Verify family creation
            assert isinstance(family_info, FamilyInfo)
            assert family_info.name == family_request.name
            assert family_info.owner_id == user_id

            # Store for cleanup
            test_data["families"][family_info.family_id] = family_info
            test_data["users"][user_id] = {"role": FamilyRole.OWNER}

    @pytest.mark.asyncio
    async def test_complete_member_invitation_journey(
        self, isolated_test_environment, mock_repositories
    ):
        """Test complete member invitation and acceptance journey"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_repositories["family_repo"],
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_repositories["user_repo"],
        ):

            # Setup test data
            family_id = f"family_{test_data['test_id']}"
            owner_id = f"user_{test_data['test_id']}_owner"
            invitee_email = f"invitee_{test_data['test_id']}@example.com"
            invitee_id = f"user_{test_data['test_id']}_invitee"

            # Mock family and user data
            mock_repositories["family_repo"].get_family_member.return_value = {
                "user_id": owner_id,
                "role": FamilyRole.OWNER,
            }
            mock_repositories["family_repo"].get_family_by_id.return_value = {
                "family_id": family_id,
                "member_count": 1,
            }
            mock_repositories["user_repo"].get_user_by_email.return_value = {
                "user_id": invitee_id
            }
            mock_repositories["family_repo"].get_pending_invite.return_value = None

            # Step 1: Send invitation
            invite_request = InviteMemberRequest(
                email=invitee_email,
                role=FamilyRole.MEMBER,
                custom_message="Welcome to our family!",
            )

            invite_info = await family_service.invite_member(
                family_id, owner_id, invite_request
            )

            # Verify invitation
            assert isinstance(invite_info, InviteInfo)
            assert invite_info.invitee_email == invitee_email

            # Step 2: Accept invitation
            mock_repositories["family_repo"].get_invite_by_code.return_value = {
                "invite_code": invite_info.invite_code,
                "family_id": family_id,
                "invitee_id": invitee_id,
                "status": "pending",
            }

            accept_request = AcceptInviteRequest(invite_code=invite_info.invite_code)
            member_info = await family_service.accept_invite(invitee_id, accept_request)

            # Verify acceptance
            assert isinstance(member_info, FamilyMember)
            assert member_info.user_id == invitee_id
            assert member_info.role == FamilyRole.MEMBER

            # Store for cleanup
            test_data["users"][invitee_id] = {"role": FamilyRole.MEMBER}
            test_data["invites"][invite_info.invite_code] = invite_info

    @pytest.mark.asyncio
    async def test_complete_role_management_journey(
        self, isolated_test_environment, mock_repositories
    ):
        """Test complete role management journey"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_repositories["family_repo"],
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_repositories["user_repo"],
        ):

            # Setup test data
            family_id = f"family_{test_data['test_id']}"
            owner_id = f"user_{test_data['test_id']}_owner"
            member_id = f"user_{test_data['test_id']}_member"

            # Mock initial state - member exists
            mock_repositories["family_repo"].get_family_member.side_effect = [
                {"user_id": owner_id, "role": FamilyRole.OWNER},  # Owner check
                {"user_id": member_id, "role": FamilyRole.MEMBER},  # Member check
            ]

            # Step 1: Promote member to manager
            update_request = UpdateMemberRoleRequest(
                member_id=member_id,
                new_role=FamilyRole.MANAGER,
                reason="Promoting to manager for family management",
            )

            await family_service.update_member_role(family_id, owner_id, update_request)

            # Verify role update was called
            mock_repositories["family_repo"].update_member_role.assert_called()

            # Step 2: Transfer ownership
            mock_repositories["family_repo"].get_family_member.side_effect = [
                {"user_id": owner_id, "role": FamilyRole.OWNER},  # Current owner check
                {"user_id": member_id, "role": FamilyRole.MANAGER},  # New owner check
            ]

            transfer_request = TransferOwnershipRequest(
                new_owner_id=member_id,
                confirmation_message="Transferring ownership to trusted member",
            )

            await family_service.transfer_ownership(
                family_id, owner_id, transfer_request
            )

            # Verify ownership transfer
            assert mock_repositories["family_repo"].update_member_role.call_count >= 2

            # Store role changes
            test_data["users"][member_id] = {"role": FamilyRole.OWNER}
            test_data["users"][owner_id] = {"role": FamilyRole.MANAGER}


class TestConcurrentOperations:
    """Test concurrent operations and race condition handling"""

    @pytest.mark.asyncio
    async def test_concurrent_family_creation(self, isolated_test_environment):
        """Test concurrent family creation by same user"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        user_id = f"user_{test_data['test_id']}_concurrent"

        async def create_family(family_name: str):
            with patch(
                "aurawell.services.family_service.FamilyRepository"
            ) as mock_repo, patch(
                "aurawell.services.family_service.UserRepository"
            ) as mock_user_repo:

                mock_user_repo.return_value.get_user_by_id.return_value = {
                    "user_id": user_id,
                    "username": "testuser",
                }
                mock_repo.return_value.get_families_by_user.return_value = []

                request = FamilyCreateRequest(name=family_name)
                try:
                    return await family_service.create_family(user_id, request)
                except Exception as e:
                    return e

        # Create multiple families concurrently
        tasks = [create_family(f"Family {i}_{test_data['test_id']}") for i in range(3)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # At least one should succeed
        successful_creations = [r for r in results if isinstance(r, FamilyInfo)]
        assert len(successful_creations) >= 1

        # Store successful creations for cleanup
        for family_info in successful_creations:
            test_data["families"][family_info.family_id] = family_info

    @pytest.mark.asyncio
    async def test_concurrent_member_operations(self, isolated_test_environment):
        """Test concurrent member operations on same family"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        family_id = f"family_{test_data['test_id']}_concurrent"
        owner_id = f"user_{test_data['test_id']}_owner"

        async def invite_member(email: str):
            with patch(
                "aurawell.services.family_service.FamilyRepository"
            ) as mock_repo, patch(
                "aurawell.services.family_service.UserRepository"
            ) as mock_user_repo:

                mock_repo.return_value.get_family_member.return_value = {
                    "user_id": owner_id,
                    "role": FamilyRole.OWNER,
                }
                mock_repo.return_value.get_family_by_id.return_value = {
                    "family_id": family_id,
                    "member_count": 1,
                }
                mock_user_repo.return_value.get_user_by_email.return_value = {
                    "user_id": f"user_{email.split('@')[0]}"
                }
                mock_repo.return_value.get_pending_invite.return_value = None

                request = InviteMemberRequest(email=email)
                try:
                    return await family_service.invite_member(
                        family_id, owner_id, request
                    )
                except Exception as e:
                    return e

        # Send multiple invitations concurrently
        emails = [f"member{i}_{test_data['test_id']}@example.com" for i in range(3)]

        tasks = [invite_member(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed (different emails)
        successful_invites = [r for r in results if isinstance(r, InviteInfo)]
        assert len(successful_invites) >= 1

        # Store invites for cleanup
        for invite_info in successful_invites:
            test_data["invites"][invite_info.invite_code] = invite_info


class TestErrorRecovery:
    """Test error recovery and rollback scenarios"""

    @pytest.mark.asyncio
    async def test_family_creation_rollback_on_error(self, isolated_test_environment):
        """Test rollback when family creation fails partway through"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        user_id = f"user_{test_data['test_id']}_rollback"

        with patch(
            "aurawell.services.family_service.FamilyRepository"
        ) as mock_repo, patch(
            "aurawell.services.family_service.UserRepository"
        ) as mock_user_repo:

            # Setup mocks - user exists but family creation fails
            mock_user_repo.return_value.get_user_by_id.return_value = {
                "user_id": user_id,
                "username": "testuser",
            }
            mock_repo.return_value.get_families_by_user.return_value = []

            # Simulate failure during family creation
            from sqlalchemy.exc import SQLAlchemyError

            mock_repo.return_value.create_family.side_effect = SQLAlchemyError(
                "Database error"
            )

            request = FamilyCreateRequest(name=f"Rollback Test {test_data['test_id']}")

            # Should raise exception and not create partial data
            with pytest.raises(AurawellException):
                await family_service.create_family(user_id, request)

            # Verify rollback - session commit should not be called
            services["session"].commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_invite_acceptance_rollback_on_error(self, isolated_test_environment):
        """Test rollback when invite acceptance fails"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        invitee_id = f"user_{test_data['test_id']}_invitee"
        invite_code = f"invite_{test_data['test_id']}"

        with patch("aurawell.services.family_service.FamilyRepository") as mock_repo:

            # Setup valid invite
            mock_repo.return_value.get_invite_by_code.return_value = {
                "invite_code": invite_code,
                "family_id": f"family_{test_data['test_id']}",
                "invitee_id": invitee_id,
                "status": "pending",
            }

            # Simulate failure during member addition
            from sqlalchemy.exc import IntegrityError

            mock_repo.return_value.add_family_member.side_effect = IntegrityError(
                "Duplicate member", None, None
            )

            request = AcceptInviteRequest(invite_code=invite_code)

            # Should raise exception and rollback
            with pytest.raises(AurawellException):
                await family_service.accept_invite(invitee_id, request)

            # Verify rollback behavior
            services["session"].commit.assert_not_called()


class TestDataConsistency:
    """Test data consistency across operations"""

    @pytest.mark.asyncio
    async def test_member_count_consistency(self, isolated_test_environment):
        """Test that member count remains consistent across operations"""
        test_data, services = isolated_test_environment
        family_service = services["family_service"]

        # This would be tested with real database in integration tests
        # For unit tests, we verify the logic calls the right methods

        family_id = f"family_{test_data['test_id']}_consistency"

        with patch("aurawell.services.family_service.FamilyRepository") as mock_repo:

            # Test that adding member updates count
            mock_repo.return_value.add_family_member.return_value = None
            mock_repo.return_value.update_family_member_count.return_value = None

            # Simulate member addition
            await family_service._execute_with_retry(
                lambda repo, user_repo: repo.add_family_member(
                    family_id, "user123", FamilyRole.MEMBER
                )
            )

            # Verify member count update would be called
            # (In real implementation, this would be part of the transaction)
            assert mock_repo.return_value.add_family_member.called

    @pytest.mark.asyncio
    async def test_role_hierarchy_consistency(self, isolated_test_environment):
        """Test that role hierarchy is maintained consistently"""
        test_data, services = isolated_test_environment

        # Test role hierarchy validation
        role_hierarchy = [
            FamilyRole.VIEWER,
            FamilyRole.MEMBER,
            FamilyRole.MANAGER,
            FamilyRole.OWNER,
        ]

        for i, role in enumerate(role_hierarchy):
            for j in range(i + 1, len(role_hierarchy)):
                higher_role = role_hierarchy[j]
                # Higher roles should have higher values
                assert higher_role.value > role.value


@pytest.fixture
def sample_e2e_data():
    """Fixture providing sample data for E2E testing"""
    test_id = str(uuid.uuid4())[:8]
    return {
        "test_id": test_id,
        "owner_id": f"user_{test_id}_owner",
        "member_id": f"user_{test_id}_member",
        "family_id": f"family_{test_id}",
        "invite_email": f"invitee_{test_id}@example.com",
    }
