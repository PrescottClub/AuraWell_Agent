"""
Permission decorators and validators for AuraWell application.

This module provides decorators for role-based access control,
specifically for family management features.
"""

from functools import wraps
from typing import List, Optional, Set
from fastapi import HTTPException, status
from ..models.api_models import FamilyRole
import logging

logger = logging.getLogger(__name__)


def require_family_permission(
    required_roles: Optional[List[FamilyRole]] = None,
    allow_self: bool = False,
    family_id_param: str = "family_id"
):
    """
    Decorator to enforce family permission requirements.
    
    Args:
        required_roles: List of required family roles
        allow_self: Whether to allow access if user is the target (for self-operations)
        family_id_param: Parameter name containing the family ID in the request
        
    Usage:
        @require_family_permission([FamilyRole.OWNER, FamilyRole.MANAGER])
        async def delete_family_member(...):
            ...
    """
    if required_roles is None:
        required_roles = []
        
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get required dependencies
            try:
                # Extract family_id from kwargs
                family_id = kwargs.get(family_id_param)
                if not family_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing {family_id_param} parameter"
                    )
                
                # Get current user ID (should be injected as dependency)
                current_user_id = kwargs.get('current_user_id')
                if not current_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                # Get family service (should be injected as dependency)
                family_service = kwargs.get('family_service')
                if not family_service:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Family service not available"
                    )
                
                # Check if user has required permissions
                try:
                    permissions = await family_service.get_user_family_permissions(
                        family_id, current_user_id
                    )
                    
                    user_role = permissions.role
                    
                    # Check role requirements
                    if required_roles and user_role not in required_roles:
                        # Check if this is a self-operation and it's allowed
                        if allow_self:
                            target_user_id = kwargs.get('target_user_id') or kwargs.get('user_id')
                            if target_user_id and target_user_id == current_user_id:
                                logger.info(f"Self-operation allowed for user {current_user_id}")
                            else:
                                raise HTTPException(
                                    status_code=status.HTTP_403_FORBIDDEN,
                                    detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}, current role: {user_role.value}"
                                )
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}, current role: {user_role.value}"
                            )
                    
                    # Add permission info to kwargs for use in the handler
                    kwargs['user_permissions'] = permissions
                    
                    logger.info(f"Permission check passed for user {current_user_id} in family {family_id} with role {user_role.value}")
                    
                except Exception as e:
                    if hasattr(e, 'error_code') and e.error_code == "NOT_FOUND":
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not a member of this family"
                        )
                    raise
                
                # Call the original function
                return await func(*args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Permission check error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Permission check failed"
                )
        
        return wrapper
    return decorator


def require_family_membership(family_id_param: str = "family_id"):
    """
    Decorator to ensure user is a member of the specified family.
    
    Args:
        family_id_param: Parameter name containing the family ID
        
    Usage:
        @require_family_membership()
        async def view_family_data(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                family_id = kwargs.get(family_id_param)
                if not family_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Missing {family_id_param} parameter"
                    )
                
                current_user_id = kwargs.get('current_user_id')
                if not current_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                family_service = kwargs.get('family_service')
                if not family_service:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Family service not available"
                    )
                
                # Check membership
                try:
                    permissions = await family_service.get_user_family_permissions(
                        family_id, current_user_id
                    )
                    kwargs['user_permissions'] = permissions
                    
                    logger.info(f"Membership check passed for user {current_user_id} in family {family_id}")
                    
                except Exception as e:
                    if hasattr(e, 'error_code') and e.error_code == "NOT_FOUND":
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not a member of this family"
                        )
                    raise
                
                return await func(*args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Membership check error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Membership check failed"
                )
        
        return wrapper
    return decorator


def check_family_role_hierarchy(user_role: FamilyRole, target_role: FamilyRole) -> bool:
    """
    Check if user_role has permission to manage target_role.
    
    Role hierarchy (higher roles can manage lower roles):
    OWNER > MANAGER > VIEWER
    
    Args:
        user_role: Role of the user performing the action
        target_role: Role being managed/assigned
        
    Returns:
        bool: True if user_role can manage target_role
    """
    role_hierarchy = {
        FamilyRole.OWNER: 3,
        FamilyRole.MANAGER: 2,
        FamilyRole.VIEWER: 1
    }
    
    return role_hierarchy.get(user_role, 0) > role_hierarchy.get(target_role, 0)


def get_allowed_roles_for_user(user_role: FamilyRole) -> List[FamilyRole]:
    """
    Get list of roles that a user can assign to others.
    
    Args:
        user_role: Role of the user
        
    Returns:
        List[FamilyRole]: Roles that can be assigned
    """
    if user_role == FamilyRole.OWNER:
        return [FamilyRole.MANAGER, FamilyRole.VIEWER]
    elif user_role == FamilyRole.MANAGER:
        return [FamilyRole.VIEWER]
    else:
        return []


class FamilyPermissionChecker:
    """
    Utility class for checking family permissions.
    """
    
    @staticmethod
    def can_invite_members(role: FamilyRole) -> bool:
        """Check if role can invite new members."""
        return role in [FamilyRole.OWNER, FamilyRole.MANAGER]
    
    @staticmethod
    def can_remove_members(role: FamilyRole) -> bool:
        """Check if role can remove members."""
        return role in [FamilyRole.OWNER, FamilyRole.MANAGER]
    
    @staticmethod
    def can_modify_family_info(role: FamilyRole) -> bool:
        """Check if role can modify family information."""
        return role == FamilyRole.OWNER
    
    @staticmethod
    def can_delete_family(role: FamilyRole) -> bool:
        """Check if role can delete the family."""
        return role == FamilyRole.OWNER
    
    @staticmethod
    def can_change_member_role(user_role: FamilyRole, target_role: FamilyRole, new_role: FamilyRole) -> bool:
        """Check if user can change another member's role."""
        # Only owners can change roles
        if user_role != FamilyRole.OWNER:
            return False
        
        # Cannot change owner role
        if target_role == FamilyRole.OWNER or new_role == FamilyRole.OWNER:
            return False
        
        return True
    
    @staticmethod
    def can_view_family_data(role: FamilyRole) -> bool:
        """Check if role can view family health data."""
        return role in [FamilyRole.OWNER, FamilyRole.MANAGER, FamilyRole.VIEWER]
    
    @staticmethod
    def can_modify_family_data(role: FamilyRole) -> bool:
        """Check if role can modify family health data."""
        return role in [FamilyRole.OWNER, FamilyRole.MANAGER]


# Pre-defined permission decorators for common use cases
require_owner = require_family_permission([FamilyRole.OWNER])
require_manager_or_owner = require_family_permission([FamilyRole.OWNER, FamilyRole.MANAGER])
require_member = require_family_membership()

# Decorator with self-access allowance
require_manager_or_self = require_family_permission([FamilyRole.OWNER, FamilyRole.MANAGER], allow_self=True) 