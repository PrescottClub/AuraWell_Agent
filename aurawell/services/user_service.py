"""
User Service for AuraWell

Handles user-related business logic including user management,
profile updates, and user preferences.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from .base_service import BaseService, ServiceResult, ServiceStatus

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """
    Service for user management operations
    
    Provides async methods for:
    - User creation and management
    - Profile updates
    - Preference management
    - User authentication (future)
    """
    
    def __init__(self, user_repository=None, database_manager=None):
        """
        Initialize user service
        
        Args:
            user_repository: User repository instance
            database_manager: Database manager instance
        """
        super().__init__("UserService")
        self.user_repository = user_repository
        self.database_manager = database_manager
        self._user_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def _initialize_service(self) -> None:
        """Initialize user service"""
        if self.database_manager and not self.database_manager.is_connected():
            if not self.database_manager.connect():
                raise RuntimeError("Failed to connect to database")
        
        # Initialize user repository if not provided
        if not self.user_repository and self.database_manager:
            from ..database.repositories import UserRepository
            self.user_repository = UserRepository(self.database_manager)
        
        self.logger.info("User service initialized")
    
    async def _shutdown_service(self) -> None:
        """Shutdown user service"""
        self._user_cache.clear()
        self.logger.info("User service shutdown")
    
    async def _perform_health_check(self) -> Optional[Dict[str, Any]]:
        """Perform user service health check"""
        health_details = {
            "cache_size": len(self._user_cache),
            "repository_available": self.user_repository is not None,
            "database_connected": self.database_manager.is_connected() if self.database_manager else False
        }
        
        # Test database connectivity
        if self.user_repository:
            try:
                # Try to list users (with limit 1 to minimize impact)
                users = await self.list_users(limit=1)
                health_details["database_test"] = "success"
            except Exception as e:
                health_details["database_test"] = f"failed: {str(e)}"
                self._health_status = ServiceStatus.DEGRADED
        
        return health_details
    
    async def create_user(self, user_data: Dict[str, Any]) -> ServiceResult[Dict[str, Any]]:
        """
        Create a new user
        
        Args:
            user_data: User data dictionary
            
        Returns:
            ServiceResult with created user data
        """
        try:
            # Validate required fields
            if not user_data.get('user_id'):
                return ServiceResult.error_result(
                    error="user_id is required",
                    error_code="VALIDATION_ERROR"
                )
            
            user_id = user_data['user_id']
            
            # Check if user already exists
            existing_user = await self.get_user(user_id)
            if existing_user.success and existing_user.data:
                return ServiceResult.error_result(
                    error=f"User {user_id} already exists",
                    error_code="USER_EXISTS"
                )
            
            # Create user model
            from ..database.models import UserModel
            user_model = UserModel(
                user_id=user_id,
                email=user_data.get('email'),
                display_name=user_data.get('display_name'),
                age=user_data.get('age'),
                gender=user_data.get('gender'),
                height_cm=user_data.get('height_cm'),
                weight_kg=user_data.get('weight_kg'),
                activity_level=user_data.get('activity_level'),
                primary_goal=user_data.get('primary_goal'),
                daily_steps_goal=user_data.get('daily_steps_goal'),
                sleep_duration_goal_hours=user_data.get('sleep_duration_goal_hours'),
                timezone=user_data.get('timezone', 'UTC'),
                preferences=user_data.get('preferences', {})
            )
            
            # Store in database
            if self.user_repository:
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self.user_repository.create_user, user_model
                )
                
                if not success:
                    return ServiceResult.error_result(
                        error="Failed to create user in database",
                        error_code="DATABASE_ERROR"
                    )
            
            # Cache the user
            self._cache_user(user_id, user_model.to_dict())
            
            self.logger.info(f"Created user: {user_id}")
            return ServiceResult.success_result(user_model.to_dict())
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    async def get_user(self, user_id: str) -> ServiceResult[Optional[Dict[str, Any]]]:
        """
        Get user by ID
        
        Args:
            user_id: User identifier
            
        Returns:
            ServiceResult with user data or None if not found
        """
        try:
            # Check cache first
            cached_user = self._get_cached_user(user_id)
            if cached_user:
                return ServiceResult.success_result(cached_user)
            
            # Get from database
            if self.user_repository:
                user_model = await asyncio.get_event_loop().run_in_executor(
                    None, self.user_repository.get_user, user_id
                )
                
                if user_model:
                    user_data = user_model.to_dict()
                    self._cache_user(user_id, user_data)
                    return ServiceResult.success_result(user_data)
            
            return ServiceResult.success_result(None)
            
        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> ServiceResult[Dict[str, Any]]:
        """
        Update user data
        
        Args:
            user_id: User identifier
            update_data: Data to update
            
        Returns:
            ServiceResult with updated user data
        """
        try:
            # Get current user
            current_user_result = await self.get_user(user_id)
            if not current_user_result.success or not current_user_result.data:
                return ServiceResult.error_result(
                    error=f"User {user_id} not found",
                    error_code="USER_NOT_FOUND"
                )
            
            # Merge update data
            user_data = current_user_result.data.copy()
            user_data.update(update_data)
            user_data['updated_at'] = datetime.now(timezone.utc)
            
            # Create updated user model
            from ..database.models import UserModel
            user_model = UserModel.from_dict(user_data)
            
            # Update in database
            if self.user_repository:
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self.user_repository.update_user, user_model
                )
                
                if not success:
                    return ServiceResult.error_result(
                        error="Failed to update user in database",
                        error_code="DATABASE_ERROR"
                    )
            
            # Update cache
            self._cache_user(user_id, user_model.to_dict())
            
            self.logger.info(f"Updated user: {user_id}")
            return ServiceResult.success_result(user_model.to_dict())
            
        except Exception as e:
            self.logger.error(f"Error updating user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    async def delete_user(self, user_id: str) -> ServiceResult[bool]:
        """
        Delete user and all associated data
        
        Args:
            user_id: User identifier
            
        Returns:
            ServiceResult with deletion success status
        """
        try:
            # Delete from database
            if self.user_repository:
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self.user_repository.delete_user, user_id
                )
                
                if not success:
                    return ServiceResult.error_result(
                        error="Failed to delete user from database",
                        error_code="DATABASE_ERROR"
                    )
            
            # Remove from cache
            self._user_cache.pop(user_id, None)
            
            self.logger.info(f"Deleted user: {user_id}")
            return ServiceResult.success_result(True)
            
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    async def list_users(self, limit: int = 100, offset: int = 0) -> ServiceResult[List[Dict[str, Any]]]:
        """
        List users with pagination
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            ServiceResult with list of users
        """
        try:
            if self.user_repository:
                users = await asyncio.get_event_loop().run_in_executor(
                    None, self.user_repository.list_users, limit, offset
                )
                
                user_list = [user.to_dict() for user in users]
                return ServiceResult.success_result(user_list)
            
            return ServiceResult.success_result([])
            
        except Exception as e:
            self.logger.error(f"Error listing users: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INTERNAL_ERROR"
            )
    
    def _cache_user(self, user_id: str, user_data: Dict[str, Any]) -> None:
        """Cache user data with timestamp"""
        self._user_cache[user_id] = {
            'data': user_data,
            'cached_at': datetime.now(timezone.utc).timestamp()
        }
    
    def _get_cached_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from cache if not expired"""
        cached_entry = self._user_cache.get(user_id)
        if not cached_entry:
            return None
        
        # Check if cache entry is expired
        now = datetime.now(timezone.utc).timestamp()
        if now - cached_entry['cached_at'] > self._cache_ttl:
            self._user_cache.pop(user_id, None)
            return None
        
        return cached_entry['data']
    
    def clear_cache(self) -> None:
        """Clear user cache"""
        self._user_cache.clear()
        self.logger.info("User cache cleared")
