"""
User Repository

Provides data access operations for user profiles and related data.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..database.models import UserProfileDB, PlatformConnectionDB
from ..models.user_profile import UserProfile, Gender, ActivityLevel
from ..models.enums import HealthPlatform, HealthGoal


class UserRepository(BaseRepository[UserProfileDB]):
    """Repository for user profile operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserProfileDB)
    
    async def create_user(self, user_profile: UserProfile) -> UserProfileDB:
        """
        Create new user from Pydantic model
        
        Args:
            user_profile: UserProfile Pydantic model
            
        Returns:
            Created UserProfileDB instance
        """
        user_data = {
            "user_id": user_profile.user_id,
            "display_name": user_profile.display_name,
            "email": user_profile.email,
            "age": user_profile.age,
            "gender": user_profile.gender.value if user_profile.gender else None,
            "height_cm": user_profile.height_cm,
            "weight_kg": user_profile.weight_kg,
            "activity_level": user_profile.activity_level.value if user_profile.activity_level else None,
            "daily_steps_goal": user_profile.daily_steps_goal,
            "daily_calories_goal": user_profile.daily_calories_goal,
            "sleep_duration_goal_hours": user_profile.sleep_duration_goal_hours,
            "weekly_exercise_minutes_goal": user_profile.weekly_exercise_goal_minutes,
            "timezone": user_profile.timezone,
            "preferred_units": user_profile.preferred_units,
            "notification_preferences": user_profile.notification_preferences,
            "connected_platforms": [p.value for p in user_profile.connected_platforms],
            "platform_user_ids": user_profile.platform_user_ids,
            "health_goals": [
                {"type": user_profile.primary_goal.value, "is_primary": True}
            ] + [
                {"type": goal.value, "is_primary": False} for goal in user_profile.secondary_goals
            ],
        }
        
        return await self.create(**user_data)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserProfileDB]:
        """
        Get user by ID with all related data
        
        Args:
            user_id: User identifier
            
        Returns:
            UserProfileDB instance or None
        """
        stmt = select(UserProfileDB).where(
            UserProfileDB.user_id == user_id
        ).options(
            selectinload(UserProfileDB.platform_connections),
            selectinload(UserProfileDB.achievement_progress)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[UserProfileDB]:
        """
        Get user by email address
        
        Args:
            email: User email address
            
        Returns:
            UserProfileDB instance or None
        """
        return await self.get_by_field("email", email)
    
    async def update_user_profile(self, user_id: str, **kwargs) -> Optional[UserProfileDB]:
        """
        Update user profile fields
        
        Args:
            user_id: User identifier
            **kwargs: Fields to update
            
        Returns:
            Updated UserProfileDB instance or None
        """
        return await self.update_by_id(user_id, **kwargs)
    
    async def update_health_goals(self, user_id: str, health_goals: List[Dict[str, Any]]) -> Optional[UserProfileDB]:
        """
        Update user health goals
        
        Args:
            user_id: User identifier
            health_goals: List of health goal dictionaries
            
        Returns:
            Updated UserProfileDB instance or None
        """
        return await self.update_by_id(user_id, health_goals=health_goals)
    
    async def add_platform_connection(self, user_id: str, platform_name: str, 
                                    platform_user_id: str, **kwargs) -> PlatformConnectionDB:
        """
        Add or update platform connection for user
        
        Args:
            user_id: User identifier
            platform_name: Platform name (e.g., 'xiaomi_health')
            platform_user_id: User ID on the platform
            **kwargs: Additional connection data
            
        Returns:
            PlatformConnectionDB instance
        """
        connection_data = {
            "user_id": user_id,
            "platform_name": platform_name,
            "platform_user_id": platform_user_id,
            **kwargs
        }
        
        # Check if connection already exists
        existing = await self.session.execute(
            select(PlatformConnectionDB).where(
                and_(
                    PlatformConnectionDB.user_id == user_id,
                    PlatformConnectionDB.platform_name == platform_name
                )
            )
        )
        existing_connection = existing.scalar_one_or_none()
        
        if existing_connection:
            # Update existing connection
            for key, value in connection_data.items():
                if hasattr(existing_connection, key):
                    setattr(existing_connection, key, value)
            await self.session.flush()
            await self.session.refresh(existing_connection)
            return existing_connection
        
        # Create new connection
        connection = PlatformConnectionDB(**connection_data)
        self.session.add(connection)
        await self.session.flush()
        await self.session.refresh(connection)
        return connection
    
    async def get_platform_connections(self, user_id: str, 
                                     active_only: bool = True) -> List[PlatformConnectionDB]:
        """
        Get user's platform connections
        
        Args:
            user_id: User identifier
            active_only: If True, return only active connections
            
        Returns:
            List of PlatformConnectionDB instances
        """
        stmt = select(PlatformConnectionDB).where(
            PlatformConnectionDB.user_id == user_id
        )
        
        if active_only:
            stmt = stmt.where(PlatformConnectionDB.is_active == True)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_platform_connection(self, user_id: str, 
                                    platform_name: str) -> Optional[PlatformConnectionDB]:
        """
        Get specific platform connection for user
        
        Args:
            user_id: User identifier
            platform_name: Platform name
            
        Returns:
            PlatformConnectionDB instance or None
        """
        stmt = select(PlatformConnectionDB).where(
            and_(
                PlatformConnectionDB.user_id == user_id,
                PlatformConnectionDB.platform_name == platform_name
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_platform_sync_status(self, user_id: str, platform_name: str,
                                        sync_status: str, last_sync_at: Optional[datetime] = None) -> bool:
        """
        Update platform sync status
        
        Args:
            user_id: User identifier
            platform_name: Platform name
            sync_status: New sync status
            last_sync_at: Last sync timestamp
            
        Returns:
            True if updated successfully
        """
        update_data = {"sync_status": sync_status}
        if last_sync_at:
            update_data["last_sync_at"] = last_sync_at
        
        connection = await self.get_platform_connection(user_id, platform_name)
        if connection:
            for key, value in update_data.items():
                setattr(connection, key, value)
            await self.session.flush()
            return True
        return False
    
    async def deactivate_platform_connection(self, user_id: str, platform_name: str) -> bool:
        """
        Deactivate platform connection
        
        Args:
            user_id: User identifier
            platform_name: Platform name
            
        Returns:
            True if deactivated successfully
        """
        connection = await self.get_platform_connection(user_id, platform_name)
        if connection:
            connection.is_active = False
            await self.session.flush()
            return True
        return False
    
    async def search_users(self, query: str, limit: int = 10) -> List[UserProfileDB]:
        """
        Search users by display name or email
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching UserProfileDB instances
        """
        search_pattern = f"%{query}%"
        stmt = select(UserProfileDB).where(
            or_(
                UserProfileDB.display_name.ilike(search_pattern),
                UserProfileDB.email.ilike(search_pattern)
            )
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    def to_pydantic(self, user_db: UserProfileDB) -> UserProfile:
        """
        Convert database model to Pydantic model
        
        Args:
            user_db: UserProfileDB instance
            
        Returns:
            UserProfile Pydantic model
        """
        return UserProfile(
            user_id=user_db.user_id,
            display_name=user_db.display_name,
            email=user_db.email,
            age=user_db.age,
            gender=Gender(user_db.gender) if user_db.gender else None,
            height_cm=user_db.height_cm,
            weight_kg=user_db.weight_kg,
            activity_level=ActivityLevel(user_db.activity_level) if user_db.activity_level else None,
            daily_steps_goal=user_db.daily_steps_goal,
            daily_calories_goal=user_db.daily_calories_goal,
            sleep_duration_goal_hours=user_db.sleep_duration_goal_hours,
            weekly_exercise_goal_minutes=user_db.weekly_exercise_minutes_goal,
            timezone=user_db.timezone,
            preferred_units=user_db.preferred_units,
            notification_preferences=user_db.notification_preferences,
            connected_platforms=[HealthPlatform(p) for p in user_db.connected_platforms],
            platform_user_ids=user_db.platform_user_ids,
            # Extract primary and secondary goals from health_goals JSON
            primary_goal=HealthGoal.GENERAL_WELLNESS,  # Default, could be extracted from health_goals
            secondary_goals=[],  # Could be extracted from health_goals
        )
