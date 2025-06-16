"""
Family Management Service - Fixed Implementation

Handles all family-related business logic including:
- Family creation and management
- Member invitation and management
- Role and permission management
- Secure invitation code generation and validation

This implementation uses in-memory storage for testing purposes.
In production, replace with actual database operations.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from ..models.family_models import (
    FamilyRole, InviteStatus,
    FamilyCreateRequest, InviteMemberRequest, AcceptInviteRequest,
    DeclineInviteRequest, UpdateMemberRoleRequest, RemoveMemberRequest,
    TransferOwnershipRequest, LeaveFamilyRequest, DeleteFamilyRequest,
    FamilySettingsRequest, FamilyInfo, FamilyMember, InviteInfo,
    FamilyPermissionInfo, FamilyActivityLog, FamilySettings
)
from ..core.exceptions import (
    ValidationError, AuthorizationError, NotFoundError,
    ConflictError, BusinessLogicError
)


class FamilyService:
    """Service class for family management operations"""
    
    def __init__(self, db_session: Any = None):
        """Initialize family service with database session"""
        self.db = db_session
        
        # Import constants locally to avoid circular imports
        try:
            from ..config.health_constants import get_health_constant
            self.invite_expiry_hours = get_health_constant("family", "INVITATION_EXPIRY_HOURS", 72)
        except ImportError:
            self.invite_expiry_hours = 72  # Fallback
        
        # Mock data storage for testing (in production, use real database)
        self._families = {}  # family_id -> family_data
        self._family_members = {}  # family_id -> [member_data]
        self._invitations = {}  # invite_code -> invite_data
        self._users = {  # Mock user data
            "user1": {"user_id": "user1", "username": "testuser1", "email": "test1@example.com"},
            "user2": {"user_id": "user2", "username": "testuser2", "email": "test2@example.com"},
        }
        
    # =====================
    # Family Operations
    # =====================
    
    async def create_family(self, request: FamilyCreateRequest, user_id: str) -> FamilyInfo:
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
        try:
            # Check if user already has maximum families
            try:
                from ..config.health_constants import get_health_constant
                max_families = get_health_constant("family", "MAX_FAMILIES_PER_USER", 3)
            except ImportError:
                max_families = 3  # Fallback
                
            current_families = await self._get_user_owned_families_count(user_id)
            if current_families >= max_families:
                raise ConflictError(f"Maximum number of families ({max_families}) reached. Please delete an existing family first.")
            
            # Generate unique family ID
            family_id = str(uuid.uuid4())
            
            # Create family record
            family_data = {
                'family_id': family_id,
                'name': request.name.strip(),
                'description': request.description.strip() if request.description else None,
                'owner_id': user_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'member_count': 1,
                'is_active': True
            }
            
            # Insert family into database
            await self._insert_family(family_data)
            
            # Add owner as first member
            await self._add_family_member(family_id, user_id, FamilyRole.OWNER)
            
            # Log family creation
            await self._log_family_activity(
                family_id, user_id, "family_created",
                {"family_name": request.name}
            )
            
            return FamilyInfo(**family_data)
            
        except Exception as e:
            if hasattr(self.db, 'rollback'):
                await self.db.rollback()
            if isinstance(e, (ValidationError, ConflictError)):
                raise
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
        # Check if user is a member of the family
        if not await self._is_family_member(family_id, user_id):
            raise AuthorizationError("You are not a member of this family")
        
        family_data = await self._get_family_by_id(family_id)
        if not family_data:
            raise NotFoundError("Family not found")
            
        return FamilyInfo(**family_data)
    
    async def get_user_families(self, user_id: str) -> List[FamilyInfo]:
        """
        Get all families that a user is a member of
        
        Args:
            user_id: ID of the user
            
        Returns:
            List[FamilyInfo]: List of families
        """
        families_data = await self._get_user_families(user_id)
        return [FamilyInfo(**family) for family in families_data]
    
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
        # Check inviter permissions
        if not await self._can_invite_members(family_id, inviter_id):
            raise AuthorizationError("You don't have permission to invite members")
        
        # Check if family exists and is active
        family = await self._get_family_by_id(family_id)
        if not family or not family['is_active']:
            raise NotFoundError("Family not found or inactive")
        
        # Check if invitee exists in the system
        invitee = await self._get_user_by_email(request.email)
        if not invitee:
            raise ValidationError("User with this email address not found")
        
        invitee_id = invitee['user_id']
        
        # Check if user is already a member
        if await self._is_family_member(family_id, invitee_id):
            raise ConflictError("User is already a member of this family")
        
        # Check if there's already a pending invitation
        existing_invite = await self._get_pending_invite(family_id, request.email)
        if existing_invite:
            raise ConflictError("There is already a pending invitation for this user")
        
        # Generate secure invitation code
        invite_code = await self._generate_invite_code()
        invite_id = str(uuid.uuid4())
        
        # Get inviter info
        inviter = await self._get_user_by_id(inviter_id)
        
        # Create invitation record
        invite_data = {
            'invite_id': invite_id,
            'family_id': family_id,
            'family_name': family['name'],
            'inviter_id': inviter_id,
            'inviter_name': inviter.get('username', 'Unknown'),
            'invitee_email': request.email,
            'role': request.role,
            'status': InviteStatus.PENDING,
            'message': request.message,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=self.invite_expiry_hours),
            'responded_at': None,
            'invite_code': invite_code
        }
        
        # Insert invitation
        await self._insert_invitation(invite_data)
        
        # Log activity
        await self._log_family_activity(
            family_id, inviter_id, "member_invited",
            {"invitee_email": request.email, "role": request.role.value}
        )
        
        return InviteInfo(**invite_data)
    
    async def accept_invitation(self, request: AcceptInviteRequest, user_id: str) -> FamilyInfo:
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
        # Get invitation by code
        invite = await self._get_invitation_by_code(request.invite_code)
        if not invite:
            raise NotFoundError("Invitation not found")
        
        # Check if invitation is still valid
        if invite['status'] != InviteStatus.PENDING:
            raise ValidationError("Invitation is no longer valid")
        
        if datetime.utcnow() > invite['expires_at']:
            raise ValidationError("Invitation has expired")
        
        # Check if user is the intended recipient
        user = await self._get_user_by_id(user_id)
        if not user or user.get('email') != invite['invitee_email']:
            raise AuthorizationError("You are not the intended recipient of this invitation")
        
        family_id = invite['family_id']
        
        # Check if user is already a member
        if await self._is_family_member(family_id, user_id):
            raise ConflictError("You are already a member of this family")
        
        # Add user to family
        await self._add_family_member(family_id, user_id, invite['role'])
        
        # Update invitation status
        await self._update_invitation_status(
            invite['invite_id'], InviteStatus.ACCEPTED, datetime.utcnow()
        )
        
        # Increment family member count
        await self._increment_family_member_count(family_id)
        
        # Log activity
        await self._log_family_activity(
            family_id, user_id, "member_joined",
            {"role": invite['role'].value}
        )
        
        # Return family info
        family_data = await self._get_family_by_id(family_id)
        return FamilyInfo(**family_data)
    
    async def get_family_members(self, family_id: str, user_id: str) -> List[FamilyMember]:
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
        if not await self._is_family_member(family_id, user_id):
            raise AuthorizationError("You are not a member of this family")
        
        members_data = await self._get_family_members(family_id)
        return [FamilyMember(**member) for member in members_data]
    
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
        member = await self._get_family_member(family_id, user_id)
        if not member:
            raise NotFoundError("User is not a member of this family")
        
        role = member['role']
        permissions = await self._get_role_permissions(role)
        
        return FamilyPermissionInfo(
            family_id=family_id,
            user_id=user_id,
            role=role,
            permissions=permissions,
            can_invite_members=role in [FamilyRole.OWNER, FamilyRole.MANAGER],
            can_remove_members=role in [FamilyRole.OWNER, FamilyRole.MANAGER],
            can_view_all_data=role in [FamilyRole.OWNER, FamilyRole.MANAGER, FamilyRole.VIEWER],
            can_modify_family_settings=role == FamilyRole.OWNER,
            can_delete_family=role == FamilyRole.OWNER
        )
    
    # =====================
    # Private Helper Methods (Mock Implementation)
    # =====================
    
    async def _generate_invite_code(self) -> str:
        """Generate a secure invitation code"""
        random_bytes = secrets.token_bytes(32)
        timestamp = str(datetime.utcnow().timestamp())
        combined = random_bytes + timestamp.encode()
        
        hash_obj = hashlib.sha256(combined)
        hash_hex = hash_obj.hexdigest()
        
        return hash_hex[:16].upper()
    
    async def _get_user_owned_families_count(self, user_id: str) -> int:
        """Get count of families owned by user"""
        count = 0
        for family_data in self._families.values():
            if family_data.get('owner_id') == user_id:
                count += 1
        return count
    
    async def _insert_family(self, family_data: dict) -> None:
        """Insert family into database"""
        self._families[family_data['family_id']] = family_data
        self._family_members[family_data['family_id']] = []
    
    async def _add_family_member(self, family_id: str, user_id: str, role: FamilyRole) -> None:
        """Add member to family"""
        if family_id not in self._family_members:
            self._family_members[family_id] = []
        
        user_data = self._users.get(user_id, {})
        member_data = {
            'user_id': user_id,
            'username': user_data.get('username', f'user_{user_id}'),
            'display_name': user_data.get('display_name'),
            'email': user_data.get('email'),
            'role': role,
            'joined_at': datetime.utcnow(),
            'last_active': datetime.utcnow(),
            'is_active': True
        }
        self._family_members[family_id].append(member_data)
    
    async def _log_family_activity(
        self, family_id: str, user_id: str, action: str, details: dict
    ) -> None:
        """Log family activity"""
        # Mock implementation - in production, store in database
        pass
    
    async def _is_family_member(self, family_id: str, user_id: str) -> bool:
        """Check if user is a family member"""
        if family_id not in self._family_members:
            return False
        
        for member in self._family_members[family_id]:
            if member['user_id'] == user_id:
                return True
        return False
    
    async def _get_family_by_id(self, family_id: str) -> Optional[dict]:
        """Get family by ID"""
        return self._families.get(family_id)
    
    async def _get_user_families(self, user_id: str) -> List[dict]:
        """Get families for user"""
        user_families = []
        for family_id, family_data in self._families.items():
            if await self._is_family_member(family_id, user_id):
                user_families.append(family_data)
        return user_families
    
    async def _can_invite_members(self, family_id: str, user_id: str) -> bool:
        """Check if user can invite members"""
        member = await self._get_family_member(family_id, user_id)
        if not member:
            return False
        
        role = member.get('role')
        return role in [FamilyRole.OWNER, FamilyRole.MANAGER]
    
    async def _get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        for user_data in self._users.values():
            if user_data.get('email') == email:
                return user_data
        return None
    
    async def _get_pending_invite(self, family_id: str, email: str) -> Optional[dict]:
        """Get pending invitation"""
        for invite_data in self._invitations.values():
            if (invite_data.get('family_id') == family_id and 
                invite_data.get('invitee_email') == email and
                invite_data.get('status') == InviteStatus.PENDING):
                return invite_data
        return None
    
    async def _get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        return self._users.get(user_id)
    
    async def _insert_invitation(self, invite_data: dict) -> None:
        """Insert invitation into database"""
        invite_code = invite_data['invite_code']
        self._invitations[invite_code] = invite_data
    
    async def _get_invitation_by_code(self, invite_code: str) -> Optional[dict]:
        """Get invitation by code"""
        return self._invitations.get(invite_code)
    
    async def _update_invitation_status(
        self, invite_id: str, status: InviteStatus, responded_at: Optional[datetime] = None
    ) -> None:
        """Update invitation status"""
        for invite_data in self._invitations.values():
            if invite_data.get('invite_id') == invite_id:
                invite_data['status'] = status
                if responded_at:
                    invite_data['responded_at'] = responded_at
                break
    
    async def _increment_family_member_count(self, family_id: str) -> None:
        """Increment family member count"""
        if family_id in self._families:
            self._families[family_id]['member_count'] += 1
    
    async def _get_family_members(self, family_id: str) -> List[dict]:
        """Get family members"""
        return self._family_members.get(family_id, [])
    
    async def _get_family_member(self, family_id: str, user_id: str) -> Optional[dict]:
        """Get specific family member"""
        members = await self._get_family_members(family_id)
        for member in members:
            if member['user_id'] == user_id:
                return member
        return None
    
    async def _get_role_permissions(self, role: FamilyRole) -> List[str]:
        """Get permissions for role"""
        permissions_map = {
            FamilyRole.OWNER: [
                "invite_members", "remove_members", "modify_family_settings",
                "view_all_data", "modify_family_data", "delete_family",
                "change_member_roles", "transfer_ownership"
            ],
            FamilyRole.MANAGER: [
                "invite_members", "remove_members", "view_all_data", 
                "modify_family_data"
            ],
            FamilyRole.VIEWER: [
                "view_all_data"
            ]
        }
        return permissions_map.get(role, []) 