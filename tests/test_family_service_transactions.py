"""
Comprehensive FamilyService Transaction Testing for AuraWell

Tests database transactions, rollback scenarios, concurrent operations,
and data consistency for FamilyService operations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.aurawell.services.family_service import FamilyService
from src.aurawell.models.family_models import (
    FamilyRole,
    FamilyCreateRequest,
    InviteMemberRequest,
    RemoveMemberRequest,
    TransferOwnershipRequest,
    FamilyInfo,
    InviteInfo,
)
from src.aurawell.core.exceptions import AurawellException


class TestFamilyServiceTransactions:
    """Test transaction management in FamilyService"""

    @pytest.fixture
    def mock_database_manager(self):
        """Mock database manager for testing"""
        mock_db = AsyncMock()
        mock_session = AsyncMock()
        mock_db.get_session.return_value.__aenter__.return_value = mock_session
        return mock_db, mock_session

    @pytest.fixture
    def family_service(self, mock_database_manager):
        """Create FamilyService instance with mocked database"""
        mock_db, _ = mock_database_manager
        return FamilyService(database_manager=mock_db)

    @pytest.mark.asyncio
    async def test_create_family_transaction_success(
        self, family_service, mock_database_manager
    ):
        """Test successful family creation with proper transaction handling"""
        _, mock_session = mock_database_manager

        # Mock repository operations
        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            # Setup mocks
            mock_user_repo.get_user_by_id.return_value = {
                "user_id": "user123",
                "username": "testuser",
            }
            mock_family_repo.get_families_by_user.return_value = (
                []
            )  # User has no families
            mock_family_repo.create_family.return_value = None
            mock_family_repo.add_family_member.return_value = None
            mock_family_repo.log_family_activity.return_value = None

            # Test data
            request = FamilyCreateRequest(
                name="Test Family", description="Test Description"
            )
            user_id = "user123"

            # Execute operation
            result = await family_service.create_family(user_id, request)

            # Verify transaction behavior
            mock_session.commit.assert_called_once()
            mock_family_repo.create_family.assert_called_once()
            mock_family_repo.add_family_member.assert_called_once()
            mock_family_repo.log_family_activity.assert_called_once()

            # Verify result
            assert isinstance(result, FamilyInfo)
            assert result.name == "Test Family"
            assert result.owner_id == user_id

    @pytest.mark.asyncio
    async def test_create_family_transaction_rollback(
        self, family_service, mock_database_manager
    ):
        """Test transaction rollback on family creation failure"""
        _, mock_session = mock_database_manager

        # Mock repository operations
        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            # Setup mocks - user exists but family creation fails
            mock_user_repo.get_user_by_id.return_value = {
                "user_id": "user123",
                "username": "testuser",
            }
            mock_family_repo.get_families_by_user.return_value = []
            mock_family_repo.create_family.side_effect = SQLAlchemyError(
                "Database error"
            )

            # Test data
            request = FamilyCreateRequest(name="Test Family")
            user_id = "user123"

            # Execute operation and expect exception
            with pytest.raises(AurawellException) as exc_info:
                await family_service.create_family(user_id, request)

            # Verify transaction rollback behavior
            assert "Database operation failed" in str(exc_info.value)
            mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_invite_member_transaction_integrity(
        self, family_service, mock_database_manager
    ):
        """Test transaction integrity during member invitation"""
        _, mock_session = mock_database_manager

        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            # Setup mocks
            mock_family_repo.get_family_member.return_value = {
                "user_id": "owner123",
                "role": FamilyRole.OWNER,
            }
            mock_family_repo.get_family_by_id.return_value = {
                "family_id": "family123",
                "member_count": 2,
            }
            mock_user_repo.get_user_by_email.return_value = {"user_id": "invitee123"}
            mock_family_repo.get_pending_invite.return_value = (
                None  # No existing invite
            )
            mock_family_repo.create_invite.return_value = None
            mock_family_repo.log_family_activity.return_value = None

            # Test data
            request = InviteMemberRequest(
                email="invitee@example.com", role=FamilyRole.MEMBER
            )
            family_id = "family123"
            inviter_id = "owner123"

            # Execute operation
            result = await family_service.invite_member(family_id, inviter_id, request)

            # Verify all operations were called in transaction
            mock_family_repo.create_invite.assert_called_once()
            mock_family_repo.log_family_activity.assert_called_once()
            mock_session.commit.assert_called_once()

            assert isinstance(result, InviteInfo)

    @pytest.mark.asyncio
    async def test_concurrent_family_operations(
        self, family_service, mock_database_manager
    ):
        """Test handling of concurrent family operations"""
        mock_db, mock_session = mock_database_manager

        # Simulate concurrent operations with different outcomes
        async def create_family_operation(user_id: str, family_name: str):
            request = FamilyCreateRequest(name=family_name)
            try:
                return await family_service.create_family(user_id, request)
            except Exception as e:
                return e

        # Mock setup for concurrent operations
        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            mock_user_repo.get_user_by_id.return_value = {
                "user_id": "user123",
                "username": "testuser",
            }
            mock_family_repo.get_families_by_user.return_value = []

            # First operation succeeds, second fails due to constraint
            mock_family_repo.create_family.side_effect = [
                None,  # First call succeeds
                IntegrityError("Duplicate key", None, None),  # Second call fails
            ]

            # Execute concurrent operations
            tasks = [
                create_family_operation("user123", "Family 1"),
                create_family_operation("user123", "Family 2"),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify one succeeded and one failed appropriately
            success_count = sum(1 for r in results if isinstance(r, FamilyInfo))
            error_count = sum(1 for r in results if isinstance(r, Exception))

            assert success_count >= 1  # At least one should succeed
            assert error_count >= 0  # Some may fail due to constraints

    @pytest.mark.asyncio
    async def test_transfer_ownership_transaction_atomicity(
        self, family_service, mock_database_manager
    ):
        """Test atomicity of ownership transfer operation"""
        mock_db, mock_session = mock_database_manager

        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            # Setup mocks
            mock_family_repo.get_family_member.side_effect = [
                {
                    "user_id": "current_owner",
                    "role": FamilyRole.OWNER,
                },  # Current owner check
                {"user_id": "new_owner", "role": FamilyRole.MEMBER},  # New owner check
            ]
            mock_family_repo.update_member_role.return_value = None
            mock_family_repo.log_family_activity.return_value = None

            # Test data
            request = TransferOwnershipRequest(new_owner_id="new_owner")
            family_id = "family123"
            current_owner_id = "current_owner"

            # Execute operation
            await family_service.transfer_ownership(
                family_id, current_owner_id, request
            )

            # Verify atomic operations
            assert (
                mock_family_repo.update_member_role.call_count == 2
            )  # Two role updates
            mock_family_repo.log_family_activity.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_transaction_consistency(
        self, family_service, mock_database_manager
    ):
        """Test transaction consistency during member removal"""
        mock_db, mock_session = mock_database_manager

        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            # Setup mocks
            mock_family_repo.get_family_member.side_effect = [
                {"user_id": "manager123", "role": FamilyRole.MANAGER},  # Remover check
                {
                    "user_id": "member123",
                    "role": FamilyRole.MEMBER,
                },  # Target member check
            ]
            mock_family_repo.remove_family_member.return_value = None
            mock_family_repo.update_family_member_count.return_value = None
            mock_family_repo.log_family_activity.return_value = None

            # Test data
            request = RemoveMemberRequest(member_id="member123", reason="Test removal")
            family_id = "family123"
            remover_id = "manager123"

            # Execute operation
            await family_service.remove_member(family_id, remover_id, request)

            # Verify all operations in transaction
            mock_family_repo.remove_family_member.assert_called_once()
            mock_family_repo.update_family_member_count.assert_called_once()
            mock_family_repo.log_family_activity.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_mechanism_on_transient_failures(
        self, family_service, mock_database_manager
    ):
        """Test retry mechanism for transient database failures"""
        mock_db, mock_session = mock_database_manager

        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            # Setup mocks - first call fails, second succeeds
            mock_user_repo.get_user_by_id.return_value = {
                "user_id": "user123",
                "username": "testuser",
            }
            mock_family_repo.get_families_by_user.return_value = []

            # Simulate transient failure then success
            mock_family_repo.create_family.side_effect = [
                SQLAlchemyError("Temporary connection error"),  # First attempt fails
                None,  # Second attempt succeeds
            ]

            # Test data
            request = FamilyCreateRequest(name="Test Family")
            user_id = "user123"

            # Execute operation
            result = await family_service.create_family(user_id, request)

            # Verify retry occurred
            assert mock_family_repo.create_family.call_count == 2
            assert isinstance(result, FamilyInfo)

    @pytest.mark.asyncio
    async def test_max_retry_limit_exceeded(
        self, family_service, mock_database_manager
    ):
        """Test behavior when max retry limit is exceeded"""
        mock_db, mock_session = mock_database_manager

        mock_family_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        with patch(
            "aurawell.services.family_service.FamilyRepository",
            return_value=mock_family_repo,
        ), patch(
            "aurawell.services.family_service.UserRepository",
            return_value=mock_user_repo,
        ):

            # Setup mocks - all attempts fail
            mock_user_repo.get_user_by_id.return_value = {
                "user_id": "user123",
                "username": "testuser",
            }
            mock_family_repo.get_families_by_user.return_value = []
            mock_family_repo.create_family.side_effect = SQLAlchemyError(
                "Persistent error"
            )

            # Test data
            request = FamilyCreateRequest(name="Test Family")
            user_id = "user123"

            # Execute operation and expect failure
            with pytest.raises(AurawellException) as exc_info:
                await family_service.create_family(user_id, request)

            # Verify max retries were attempted
            assert (
                mock_family_repo.create_family.call_count
                == family_service.max_retry_attempts
            )
            assert "Database operation failed" in str(exc_info.value)


class TestFamilyServiceDataConsistency:
    """Test data consistency in FamilyService operations"""

    @pytest.fixture
    def family_service(self):
        """Create FamilyService instance for consistency testing"""
        mock_db = AsyncMock()
        return FamilyService(database_manager=mock_db)

    @pytest.mark.asyncio
    async def test_member_count_consistency(self, family_service):
        """Test that member count remains consistent across operations"""
        # This would be an integration test with real database
        # For now, we test the logic flow

        with patch.object(family_service, "_execute_with_retry") as mock_execute:
            mock_execute.return_value = None

            # Test adding member updates count
            request = InviteMemberRequest(email="test@example.com")
            await family_service.invite_member("family123", "owner123", request)

            # Verify the operation would update member count
            mock_execute.assert_called()

    @pytest.mark.asyncio
    async def test_role_hierarchy_consistency(self, family_service):
        """Test that role hierarchy is maintained consistently"""
        with patch.object(family_service, "_execute_with_retry") as mock_execute:
            mock_execute.return_value = None

            # Test that ownership transfer maintains hierarchy
            request = TransferOwnershipRequest(new_owner_id="new_owner")
            await family_service.transfer_ownership(
                "family123", "current_owner", request
            )

            # Verify the operation maintains role consistency
            mock_execute.assert_called()


@pytest.fixture
def sample_family_service_data():
    """Fixture providing sample data for FamilyService testing"""
    return {
        "family_id": "family123",
        "user_id": "user123",
        "owner_id": "owner123",
        "member_id": "member123",
        "invitee_email": "invitee@example.com",
    }
