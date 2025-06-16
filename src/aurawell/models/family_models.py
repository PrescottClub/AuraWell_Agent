"""
Family-related data models for AuraWell

This module contains all Pydantic models related to family functionality,
including family management, member roles, invitations, and permissions.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, Generic, TypeVar
from datetime import datetime, date
from enum import Enum
import uuid
# Import base response models from the same package
from typing import Union, Any

# Define base response classes for now to avoid circular imports
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    status: str = "success"
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)

class SuccessResponse(BaseResponse):
    """Success response model"""
    data: Any = None

T = TypeVar('T')


# ================================
# Family Core Models
# ================================

class FamilyRole(str, Enum):
    """Family member role enumeration"""
    OWNER = "owner"          # Full control, can delete family
    MANAGER = "manager"      # Can invite/remove members, view all data
    VIEWER = "viewer"        # Can only view shared data


class InviteStatus(str, Enum):
    """Invitation status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class DataAccessLevel(str, Enum):
    """Data access level enumeration"""
    FULL = "full"        # Full access to all data
    LIMITED = "limited"  # Limited access with some restrictions
    BASIC = "basic"      # Basic access with heavy restrictions


# ================================
# Family Management Models
# ================================

class FamilyCreateRequest(BaseModel):
    """Request to create a new family"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Family name (1-100 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Family description (optional, max 500 characters)"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate family name"""
        if not v.strip():
            raise ValueError('Family name cannot be empty or whitespace only')
        return v.strip()


class FamilyMember(BaseModel):
    """Family member information"""
    user_id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    role: FamilyRole
    joined_at: datetime
    last_active: Optional[datetime] = None
    is_active: bool = True


class FamilyInfo(BaseModel):
    """Family information"""
    family_id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    created_at: datetime
    updated_at: datetime
    member_count: int
    is_active: bool = True


class FamilySettings(BaseModel):
    """Family settings information"""
    family_id: str
    name: str
    description: Optional[str] = None
    privacy_settings: Dict[str, Any]
    member_permissions: Dict[str, List[str]]
    data_sharing_settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ================================
# Invitation Models
# ================================

class InviteMemberRequest(BaseModel):
    """Request to invite a member to family"""
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Valid email address of the user to invite"
    )
    role: FamilyRole = Field(
        default=FamilyRole.VIEWER,
        description="Role to assign to the invited member"
    )
    message: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional invitation message (max 500 characters)"
    )


class InviteInfo(BaseModel):
    """Invitation information"""
    invite_id: str
    family_id: str
    family_name: str
    inviter_id: str
    inviter_name: str
    invitee_email: str
    role: FamilyRole
    status: InviteStatus
    message: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    responded_at: Optional[datetime] = None


class AcceptInviteRequest(BaseModel):
    """Request to accept a family invitation"""
    invite_code: str = Field(
        ...,
        min_length=1,
        description="Invitation code received via email"
    )


class DeclineInviteRequest(BaseModel):
    """Request to decline a family invitation"""
    invite_code: str = Field(
        ...,
        min_length=1,
        description="Invitation code received via email"
    )
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional reason for declining (max 200 characters)"
    )


# ================================
# Member Management Models
# ================================

class UpdateMemberRoleRequest(BaseModel):
    """Request to update a family member's role"""
    user_id: str = Field(..., description="User ID of the member to update")
    new_role: FamilyRole = Field(..., description="New role to assign")
    
    @field_validator('new_role')
    @classmethod
    def validate_role_change(cls, v):
        """Validate role change"""
        if v == FamilyRole.OWNER:
            raise ValueError('Cannot assign owner role through role update. Use transfer ownership instead.')
        return v


class RemoveMemberRequest(BaseModel):
    """Request to remove a family member"""
    user_id: str = Field(..., description="User ID of the member to remove")
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional reason for removal (max 200 characters)"
    )


class TransferOwnershipRequest(BaseModel):
    """Request to transfer family ownership"""
    new_owner_id: str = Field(..., description="User ID of the new owner")
    confirmation_message: str = Field(
        ...,
        pattern="^I understand that I will lose ownership of this family$",
        description="Confirmation message to prevent accidental transfers"
    )


class LeaveFamilyRequest(BaseModel):
    """Request to leave a family"""
    family_id: str = Field(..., description="Family ID to leave")
    reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional reason for leaving (max 200 characters)"
    )


class DeleteFamilyRequest(BaseModel):
    """Request to delete a family (owner only)"""
    family_id: str = Field(..., description="Family ID to delete")
    confirmation_message: str = Field(
        ...,
        pattern="^DELETE FAMILY PERMANENTLY$",
        description="Confirmation message to prevent accidental deletion"
    )


# ================================
# Permission & Access Models
# ================================

class FamilyPermissionInfo(BaseModel):
    """Family permission information for a user"""
    family_id: str
    user_id: str
    role: FamilyRole
    permissions: List[str]  # List of specific permissions
    can_invite_members: bool
    can_remove_members: bool
    can_view_all_data: bool
    can_modify_family_settings: bool
    can_delete_family: bool


class FamilyActivityLog(BaseModel):
    """Family activity log entry"""
    log_id: str
    family_id: str
    user_id: str
    username: str
    action: str  # e.g., "member_invited", "member_joined", "role_changed"
    details: Dict[str, Any]
    timestamp: datetime


class FamilySettingsRequest(BaseModel):
    """Request to update family settings"""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Family name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Family description"
    )
    privacy_settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Privacy settings for the family"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate family name if provided"""
        if v is not None and not v.strip():
            raise ValueError('Family name cannot be empty or whitespace only')
        return v.strip() if v else v


# ================================
# Member Switching Models
# ================================

class SwitchMemberRequest(BaseModel):
    """Request to switch active family member"""
    family_id: str = Field(..., description="Family ID")
    member_id: str = Field(..., description="Member ID to switch to")

    @field_validator('family_id')
    @classmethod
    def validate_family_id(cls, v):
        if not v.strip():
            raise ValueError('Family ID cannot be empty')
        return v.strip()

    @field_validator('member_id')
    @classmethod
    def validate_member_id(cls, v):
        if not v.strip():
            raise ValueError('Member ID cannot be empty')
        return v.strip()


class ActiveMemberInfo(BaseModel):
    """Active member information"""
    member_id: str
    user_id: str
    family_id: str
    username: str
    display_name: Optional[str] = None
    role: FamilyRole
    permissions: List[str]
    data_access_level: str  # 'full', 'limited', 'basic'
    switched_at: datetime


# ================================
# Data Privacy & Access Models
# ================================

class DataSanitizationRule(BaseModel):
    """Data sanitization rule"""
    field_name: str
    access_level: DataAccessLevel
    sanitization_type: str  # 'mask', 'remove', 'aggregate', 'anonymize'
    replacement_value: Optional[str] = None


class MemberDataContext(BaseModel):
    """Member data context for isolation"""
    user_id: str
    member_id: Optional[str] = None
    family_id: Optional[str] = None
    requester_role: Optional[FamilyRole] = None
    data_access_level: DataAccessLevel = DataAccessLevel.BASIC
    allowed_fields: List[str] = Field(default_factory=list)
    sanitization_rules: List[DataSanitizationRule] = Field(default_factory=list)

    @property
    def isolation_key(self) -> str:
        """Generate unique key for member data isolation"""
        return f"{self.user_id}:{self.member_id or 'self'}:{self.family_id or 'personal'}"

    @property
    def is_family_context(self) -> bool:
        """Check if this is a family member context"""
        return self.family_id is not None and self.member_id is not None


class DataPrivacySettings(BaseModel):
    """Data privacy settings for family members"""
    family_id: str
    member_id: str
    share_health_data: bool = False
    share_activity_data: bool = False
    share_conversation_history: bool = False
    share_goals: bool = False
    share_achievements: bool = False
    data_retention_days: int = Field(default=90, ge=1, le=365)
    anonymize_sensitive_data: bool = True


class FamilyDataAccessRequest(BaseModel):
    """Request for accessing family member data"""
    family_id: str
    target_member_id: str
    requested_data_types: List[str] = Field(..., min_length=1)
    access_reason: Optional[str] = None

    @field_validator('requested_data_types')
    @classmethod
    def validate_data_types(cls, v):
        allowed_types = {
            'health_data', 'activity_data', 'sleep_data', 
            'nutrition_data', 'goals', 'achievements', 
            'conversation_history', 'basic_profile'
        }
        invalid_types = set(v) - allowed_types
        if invalid_types:
            raise ValueError(f'Invalid data types: {invalid_types}')
        return v


class SanitizedUserData(BaseModel):
    """Sanitized user data based on access level"""
    user_id: str
    member_id: Optional[str] = None
    display_name: Optional[str] = None
    basic_health_info: Optional[Dict[str, Any]] = None
    activity_summary: Optional[Dict[str, Any]] = None
    goals_summary: Optional[Dict[str, Any]] = None
    data_access_level: DataAccessLevel
    sanitized_fields: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


# ================================
# Response Models
# ================================

class FamilyInfoResponse(SuccessResponse):
    """Family information response"""
    data: Optional[FamilyInfo] = None


class FamilyListResponse(SuccessResponse):
    """Family list response"""
    data: Optional[List[FamilyInfo]] = None


class FamilyMembersResponse(SuccessResponse):
    """Family members list response"""
    data: Optional[List[FamilyMember]] = None


class InviteMemberResponse(SuccessResponse):
    """Invite member response"""
    data: Optional[InviteInfo] = None


class PendingInviteResponse(SuccessResponse):
    """Pending invitations response"""
    data: Optional[List[InviteInfo]] = None


class FamilyPermissionResponse(SuccessResponse):
    """Family permission check response"""
    data: Optional[FamilyPermissionInfo] = None


class FamilyActivityLogResponse(SuccessResponse):
    """Family activity log response"""
    data: Optional[List[FamilyActivityLog]] = None


class FamilySettingsResponse(SuccessResponse):
    """Family settings response"""
    data: Optional[FamilySettings] = None


class SwitchMemberResponse(SuccessResponse):
    """Switch member response"""
    data: Optional[ActiveMemberInfo] = None


class FamilyDataAccessResponse(SuccessResponse):
    """Family data access response"""
    data: Optional[SanitizedUserData] = None 