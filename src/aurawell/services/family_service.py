"""
Family Management Service - Database Integration Implementation

Handles all family-related business logic including:
- Family creation and management
- Member invitation and management
- Role and permission management
- Secure invitation code generation and validation

This implementation uses real database operations with transaction management.
"""

import hashlib
import secrets
import uuid
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.family_models import (
    FamilyRole,
    InviteStatus,
    FamilyCreateRequest,
    InviteMemberRequest,
    AcceptInviteRequest,
    FamilyInfo,
    FamilyMember,
    InviteInfo,
    FamilyPermissionInfo,
)
from ..core.exceptions import (
    ValidationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
    AurawellException,
    DatabaseError,
)
from ..database import get_database_manager
from ..repositories.family_repository import FamilyRepository
from ..repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class FamilyService:
    """Service class for family management operations with database integration"""

    def __init__(self, db_session: Optional[Session] = None):
        """Initialize family service with database session"""
        self.db_session = db_session
        self.db_manager = get_database_manager()

        # Import constants locally to avoid circular imports
        try:
            from ..config.health_constants import get_health_constant

            self.invite_expiry_hours = get_health_constant(
                "family", "INVITATION_EXPIRY_HOURS", 72
            )
            self.max_families = get_health_constant(
                "family", "MAX_FAMILIES_PER_USER", 3
            )
            self.max_retry_attempts = 3
        except ImportError:
            self.invite_expiry_hours = 72  # Fallback
            self.max_families = 3
            self.max_retry_attempts = 3

    async def _get_session(self):
        """Get database session with fallback to manager"""
        if self.db_session:
            return self.db_session
        return self.db_manager.get_session()

    async def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute database operation with retry logic"""
        last_exception = None

        for attempt in range(self.max_retry_attempts):
            try:
                async with await self._get_session() as session:
                    family_repo = FamilyRepository(session)
                    user_repo = UserRepository(session)

                    result = await operation(family_repo, user_repo, *args, **kwargs)
                    await session.commit()
                    return result

            except SQLAlchemyError as e:
                last_exception = e
                logger.warning(
                    f"Database operation failed (attempt {attempt + 1}/{self.max_retry_attempts}): {e}"
                )
                if attempt == self.max_retry_attempts - 1:
                    break
                await asyncio.sleep(0.1 * (2**attempt))  # Exponential backoff
            except Exception as e:
                # Non-retryable exceptions
                logger.error(f"Non-retryable error in database operation: {e}")
                raise AurawellException(
                    f"Database operation failed: {str(e)}",
                    details={"operation": "family_service"},
                )

        # If we get here, all retries failed
        raise DatabaseError(
            f"Database operation failed after {self.max_retry_attempts} attempts: {str(last_exception)}"
        )

    # =====================
    # Family Operations
    # =====================

    async def create_family(
        self, request: FamilyCreateRequest, user_id: str
    ) -> FamilyInfo:
        """
        Create a new family with the current user as owner

        Args:
            request: Family creation request
            user_id: ID of the user creating the family

        Returns:
            FamilyInfo: Created family information

        Raises:
            ValidationError: If validation fails
            ConflictError: If user already owns maximum families
        """

        async def _create_family_operation(
            family_repo: FamilyRepository, user_repo: UserRepository
        ):
            # Check if user exists
            user = await user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFoundError(f"User {user_id} not found", resource_type="user")

            # Check if user already has maximum families
            current_families = await family_repo.get_user_owned_families_count(user_id)
            if current_families >= self.max_families:
                raise ConflictError(
                    f"Maximum number of families ({self.max_families}) reached. Please delete an existing family first."
                )

            # Generate unique family ID
            family_id = str(uuid.uuid4())

            # Create family record with timezone-aware datetime
            now = datetime.now(timezone.utc)
            family_data = {
                "family_id": family_id,
                "name": request.name.strip(),
                "description": (
                    request.description.strip() if request.description else None
                ),
                "owner_id": user_id,
                "created_at": now,
                "updated_at": now,
                "member_count": 1,
                "is_active": True,
            }

            # Create family in database
            await family_repo.create_family(family_data)

            # Add owner as first member
            await family_repo.add_family_member(family_id, user_id, FamilyRole.OWNER)

            # Log family creation
            await family_repo.log_family_activity(
                family_id, user_id, "family_created", {"family_name": request.name}
            )

            return FamilyInfo(**family_data)

        try:
            return await self._execute_with_retry(_create_family_operation)
        except (ValidationError, ConflictError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to create family: {e}")
            raise BusinessLogicError(f"Failed to create family: {str(e)}")

    async def get_family_info(self, family_id: str, user_id: str) -> FamilyInfo:
        """
        Get family information for a specific family

        Args:
            family_id: ID of the family
            user_id: ID of the requesting user

        Returns:
            FamilyInfo: Family information

        Raises:
            NotFoundError: If family not found
            AuthorizationError: If user is not a member
        """

        async def _get_family_info_operation(
            family_repo: FamilyRepository, _user_repo: UserRepository
        ):
            # Check if user is a member of the family
            is_member = await family_repo.is_family_member(family_id, user_id)
            if not is_member:
                raise AuthorizationError("You are not a member of this family")

            family_data = await family_repo.get_family_by_id(family_id)
            if not family_data:
                raise NotFoundError("Family not found", resource_type="family")

            return FamilyInfo(**family_data)

        try:
            return await self._execute_with_retry(_get_family_info_operation)
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Failed to get family info: {e}")
            raise BusinessLogicError(f"Failed to get family info: {str(e)}")

    async def get_user_families(self, user_id: str) -> List[FamilyInfo]:
        """
        Get all families that a user is a member of

        Args:
            user_id: ID of the user

        Returns:
            List[FamilyInfo]: List of families
        """

        async def _get_user_families_operation(
            family_repo: FamilyRepository, _user_repo: UserRepository
        ):
            families_data = await family_repo.get_user_families(user_id)
            return [FamilyInfo(**family) for family in families_data]

        try:
            return await self._execute_with_retry(_get_user_families_operation)
        except Exception as e:
            logger.error(f"Failed to get user families: {e}")
            raise BusinessLogicError(f"Failed to get user families: {str(e)}")

    # =====================
    # Member Management
    # =====================

    async def invite_member(
        self, family_id: str, request: InviteMemberRequest, inviter_id: str
    ) -> InviteInfo:
        """
        Invite a new member to the family

        Args:
            family_id: ID of the family
            request: Invitation request
            inviter_id: ID of the user sending the invitation

        Returns:
            InviteInfo: Invitation information

        Raises:
            AuthorizationError: If inviter doesn't have permission
            ConflictError: If user is already a member or has pending invite
            ValidationError: If email is invalid or user not found
        """

        async def _invite_member_operation(
            family_repo: FamilyRepository, user_repo: UserRepository
        ):
            # Check inviter permissions
            can_invite = await family_repo.can_invite_members(family_id, inviter_id)
            if not can_invite:
                raise AuthorizationError("You don't have permission to invite members")

            # Check if family exists and is active
            family = await family_repo.get_family_by_id(family_id)
            if not family or not family.get("is_active"):
                raise NotFoundError(
                    "Family not found or inactive", resource_type="family"
                )

            # Check if invitee exists in the system
            invitee = await user_repo.get_user_by_email(request.email)
            if not invitee:
                raise ValidationError(
                    "User with this email address not found", field="email"
                )

            invitee_id = invitee.user_id

            # Check if user is already a member
            is_member = await family_repo.is_family_member(family_id, invitee_id)
            if is_member:
                raise ConflictError("User is already a member of this family")

            # Check if there's already a pending invitation
            existing_invite = await family_repo.get_pending_invite(
                family_id, request.email
            )
            if existing_invite:
                raise ConflictError(
                    "There is already a pending invitation for this user"
                )

            # Generate secure invitation code
            invite_code = await self._generate_invite_code()
            invite_id = str(uuid.uuid4())

            # Get inviter info
            inviter = await user_repo.get_user_by_id(inviter_id)

            # Create invitation record with timezone-aware datetime
            now = datetime.now(timezone.utc)
            invite_data = {
                "invite_id": invite_id,
                "family_id": family_id,
                "family_name": family["name"],
                "inviter_id": inviter_id,
                "inviter_name": inviter.username if inviter else "Unknown",
                "invitee_email": request.email,
                "role": request.role,
                "status": InviteStatus.PENDING,
                "message": request.message,
                "created_at": now,
                "expires_at": now + timedelta(hours=self.invite_expiry_hours),
                "responded_at": None,
                "invite_code": invite_code,
            }

            # Insert invitation
            await family_repo.create_invitation(invite_data)

            # Log activity
            await family_repo.log_family_activity(
                family_id,
                inviter_id,
                "member_invited",
                {"invitee_email": request.email, "role": request.role.value},
            )

            return InviteInfo(**invite_data)

        try:
            return await self._execute_with_retry(_invite_member_operation)
        except (AuthorizationError, ConflictError, ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to invite member: {e}")
            raise BusinessLogicError(f"Failed to invite member: {str(e)}")

    async def accept_invitation(
        self, request: AcceptInviteRequest, user_id: str
    ) -> FamilyInfo:
        """
        Accept a family invitation

        Args:
            request: Accept invitation request
            user_id: ID of the user accepting

        Returns:
            FamilyInfo: Family information after joining

        Raises:
            NotFoundError: If invitation not found
            ValidationError: If invitation is invalid or expired
            AuthorizationError: If user is not the intended recipient
        """

        async def _accept_invitation_operation(
            family_repo: FamilyRepository, user_repo: UserRepository
        ):
            # Get invitation by code
            invite = await family_repo.get_invitation_by_code(request.invite_code)
            if not invite:
                raise NotFoundError("Invitation not found", resource_type="invitation")

            # Check if invitation is still valid
            if invite["status"] != InviteStatus.PENDING:
                raise ValidationError("Invitation is no longer valid")

            now = datetime.now(timezone.utc)
            if now > invite["expires_at"]:
                raise ValidationError("Invitation has expired")

            # Check if user is the intended recipient
            user = await user_repo.get_user_by_id(user_id)
            if not user or user.email != invite["invitee_email"]:
                raise AuthorizationError(
                    "You are not the intended recipient of this invitation"
                )

            family_id = invite["family_id"]

            # Check if user is already a member
            is_member = await family_repo.is_family_member(family_id, user_id)
            if is_member:
                raise ConflictError("You are already a member of this family")

            # Add user to family
            await family_repo.add_family_member(family_id, user_id, invite["role"])

            # Update invitation status
            await family_repo.update_invitation_status(
                invite["invite_id"], InviteStatus.ACCEPTED, now
            )

            # Increment family member count
            await family_repo.increment_family_member_count(family_id)

            # Log activity
            await family_repo.log_family_activity(
                family_id, user_id, "member_joined", {"role": invite["role"].value}
            )

            # Return family info
            family_data = await family_repo.get_family_by_id(family_id)
            return FamilyInfo(**family_data)

        try:
            return await self._execute_with_retry(_accept_invitation_operation)
        except (NotFoundError, ValidationError, AuthorizationError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Failed to accept invitation: {e}")
            raise BusinessLogicError(f"Failed to accept invitation: {str(e)}")

    async def get_family_members(
        self, family_id: str, user_id: str
    ) -> List[FamilyMember]:
        """
        Get all members of a family

        Args:
            family_id: ID of the family
            user_id: ID of the requesting user

        Returns:
            List[FamilyMember]: List of family members

        Raises:
            AuthorizationError: If user is not a member
        """

        async def _get_family_members_operation(
            family_repo: FamilyRepository, _user_repo: UserRepository
        ):
            is_member = await family_repo.is_family_member(family_id, user_id)
            if not is_member:
                raise AuthorizationError("You are not a member of this family")

            members_data = await family_repo.get_family_members(family_id)
            return [FamilyMember(**member) for member in members_data]

        try:
            return await self._execute_with_retry(_get_family_members_operation)
        except AuthorizationError:
            raise
        except Exception as e:
            logger.error(f"Failed to get family members: {e}")
            raise BusinessLogicError(f"Failed to get family members: {str(e)}")

    # =====================
    # Permission Management
    # =====================

    async def get_user_family_permissions(
        self, family_id: str, user_id: str
    ) -> FamilyPermissionInfo:
        """
        Get a user's permissions within a family

        Args:
            family_id: ID of the family
            user_id: ID of the user

        Returns:
            FamilyPermissionInfo: User's permissions

        Raises:
            NotFoundError: If user is not a member
        """

        async def _get_permissions_operation(
            family_repo: FamilyRepository, _user_repo: UserRepository
        ):
            member = await family_repo.get_family_member(family_id, user_id)
            if not member:
                raise NotFoundError(
                    "User is not a member of this family", resource_type="family_member"
                )

            role = member["role"]
            permissions = self._get_role_permissions(role)

            return FamilyPermissionInfo(
                family_id=family_id,
                user_id=user_id,
                role=role,
                permissions=permissions,
                can_invite_members=role in [FamilyRole.OWNER, FamilyRole.MANAGER],
                can_remove_members=role in [FamilyRole.OWNER, FamilyRole.MANAGER],
                can_view_all_data=role
                in [FamilyRole.OWNER, FamilyRole.MANAGER, FamilyRole.VIEWER],
                can_modify_family_settings=role == FamilyRole.OWNER,
                can_delete_family=role == FamilyRole.OWNER,
            )

        try:
            return await self._execute_with_retry(_get_permissions_operation)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get user family permissions: {e}")
            raise BusinessLogicError(f"Failed to get user family permissions: {str(e)}")

    def _get_role_permissions(self, role: FamilyRole) -> List[str]:
        """Get permissions for role"""
        permissions_map = {
            FamilyRole.OWNER: [
                "invite_members",
                "remove_members",
                "modify_family_settings",
                "view_all_data",
                "modify_family_data",
                "delete_family",
                "change_member_roles",
                "transfer_ownership",
            ],
            FamilyRole.MANAGER: [
                "invite_members",
                "remove_members",
                "view_all_data",
                "modify_family_data",
            ],
            FamilyRole.VIEWER: ["view_all_data"],
        }
        return permissions_map.get(role, [])

    # =====================
    # Helper Methods
    # =====================

    async def _generate_invite_code(self) -> str:
        """Generate a secure invitation code"""
        random_bytes = secrets.token_bytes(32)
        timestamp = str(datetime.now(timezone.utc).timestamp())
        combined = random_bytes + timestamp.encode()

        hash_obj = hashlib.sha256(combined)
        hash_hex = hash_obj.hexdigest()

        return hash_hex[:16].upper()
