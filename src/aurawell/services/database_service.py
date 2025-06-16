"""
Database Service

High-level service for database operations using repositories.
Provides unified interface for all data access operations.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from contextlib import asynccontextmanager

from ..database.connection import DatabaseManager, get_database_manager
from ..repositories.user_repository import UserRepository
from ..repositories.health_data_repository import HealthDataRepository
from ..repositories.achievement_repository import AchievementRepository
from ..models.user_profile import UserProfile
from ..models.health_data_model import (
    UnifiedActivitySummary, UnifiedSleepSession, 
    UnifiedHeartRateSample, NutritionEntry
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    High-level database service providing unified data access
    
    Manages repositories and provides transaction support for complex operations.
    """
    
    def __init__(self, database_manager: Optional[DatabaseManager] = None):
        """
        Initialize database service
        
        Args:
            database_manager: Optional DatabaseManager instance
        """
        self.db_manager = database_manager or get_database_manager()
    
    @asynccontextmanager
    async def get_repositories(self):
        """
        Get repository instances with shared session
        
        Yields:
            Tuple of (user_repo, health_repo, achievement_repo)
        """
        async with self.db_manager.get_session() as session:
            user_repo = UserRepository(session)
            health_repo = HealthDataRepository(session)
            achievement_repo = AchievementRepository(session)
            
            yield user_repo, health_repo, achievement_repo
    
    # User Profile Operations
    async def create_user_profile(self, user_profile: UserProfile) -> bool:
        """
        Create new user profile
        
        Args:
            user_profile: UserProfile Pydantic model
            
        Returns:
            True if user was created successfully
        """
        try:
            async with self.get_repositories() as (user_repo, _, _):
                await user_repo.create_user(user_profile)
                logger.info(f"User profile created: {user_profile.user_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by ID
        
        Args:
            user_id: User identifier
            
        Returns:
            UserProfile Pydantic model or None
        """
        try:
            async with self.get_repositories() as (user_repo, _, _):
                user_db = await user_repo.get_user_by_id(user_id)
                if user_db:
                    return user_repo.to_pydantic(user_db)
                return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, **kwargs) -> bool:
        """
        Update user profile fields
        
        Args:
            user_id: User identifier
            **kwargs: Fields to update
            
        Returns:
            True if update was successful
        """
        try:
            async with self.get_repositories() as (user_repo, _, _):
                result = await user_repo.update_user_profile(user_id, **kwargs)
                if result:
                    logger.info(f"User profile updated: {user_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False
    
    async def add_platform_connection(self, user_id: str, platform_name: str,
                                    platform_user_id: str, **kwargs) -> bool:
        """
        Add platform connection for user
        
        Args:
            user_id: User identifier
            platform_name: Platform name
            platform_user_id: Platform user ID
            **kwargs: Additional connection data
            
        Returns:
            True if connection was added successfully
        """
        try:
            async with self.get_repositories() as (user_repo, _, _):
                await user_repo.add_platform_connection(
                    user_id, platform_name, platform_user_id, **kwargs
                )
                logger.info(f"Platform connection added: {user_id} -> {platform_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to add platform connection: {e}")
            return False
    
    # Health Data Operations
    async def save_activity_data(self, user_id: str, 
                               activity: UnifiedActivitySummary) -> bool:
        """
        Save activity summary data
        
        Args:
            user_id: User identifier
            activity: UnifiedActivitySummary model
            
        Returns:
            True if data was saved successfully
        """
        try:
            async with self.get_repositories() as (_, health_repo, _):
                await health_repo.save_activity_summary(user_id, activity)
                logger.debug(f"Activity data saved: {user_id} - {activity.date}")
                return True
        except Exception as e:
            logger.error(f"Failed to save activity data: {e}")
            return False
    
    async def save_sleep_data(self, user_id: str, 
                            sleep: UnifiedSleepSession) -> bool:
        """
        Save sleep session data
        
        Args:
            user_id: User identifier
            sleep: UnifiedSleepSession model
            
        Returns:
            True if data was saved successfully
        """
        try:
            async with self.get_repositories() as (_, health_repo, _):
                await health_repo.save_sleep_session(user_id, sleep)
                logger.debug(f"Sleep data saved: {user_id} - {sleep.date}")
                return True
        except Exception as e:
            logger.error(f"Failed to save sleep data: {e}")
            return False
    
    async def save_heart_rate_data(self, user_id: str,
                                 heart_rate: UnifiedHeartRateSample) -> bool:
        """
        Save heart rate sample data
        
        Args:
            user_id: User identifier
            heart_rate: UnifiedHeartRateSample model
            
        Returns:
            True if data was saved successfully
        """
        try:
            async with self.get_repositories() as (_, health_repo, _):
                await health_repo.save_heart_rate_sample(user_id, heart_rate)
                logger.debug(f"Heart rate data saved: {user_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to save heart rate data: {e}")
            return False
    
    async def save_nutrition_data(self, user_id: str,
                                nutrition: NutritionEntry) -> bool:
        """
        Save nutrition entry data
        
        Args:
            user_id: User identifier
            nutrition: NutritionEntry model
            
        Returns:
            True if data was saved successfully
        """
        try:
            async with self.get_repositories() as (_, health_repo, _):
                await health_repo.save_nutrition_entry(user_id, nutrition)
                logger.debug(f"Nutrition data saved: {user_id} - {nutrition.date}")
                return True
        except Exception as e:
            logger.error(f"Failed to save nutrition data: {e}")
            return False
    
    async def get_activity_summary(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent activity summary for user
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
            
        Returns:
            List of activity summary dictionaries
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            async with self.get_repositories() as (_, health_repo, _):
                activities = await health_repo.get_activity_summaries(
                    user_id, start_date, end_date, limit=days
                )
                
                return [activity.to_dict() for activity in activities]
        except Exception as e:
            logger.error(f"Failed to get activity summary: {e}")
            return []
    
    async def get_sleep_summary(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent sleep summary for user
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
            
        Returns:
            List of sleep summary dictionaries
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            async with self.get_repositories() as (_, health_repo, _):
                sleep_sessions = await health_repo.get_sleep_sessions(
                    user_id, start_date, end_date, limit=days
                )
                
                return [session.to_dict() for session in sleep_sessions]
        except Exception as e:
            logger.error(f"Failed to get sleep summary: {e}")
            return []
    
    # Achievement Operations
    async def update_achievement_progress(self, user_id: str, achievement_type: str,
                                        achievement_level: str, current_value: float,
                                        target_value: float) -> bool:
        """
        Update achievement progress
        
        Args:
            user_id: User identifier
            achievement_type: Achievement type
            achievement_level: Achievement level
            current_value: Current progress value
            target_value: Target value
            
        Returns:
            True if progress was updated successfully
        """
        try:
            async with self.get_repositories() as (_, _, achievement_repo):
                # Check if achievement should be unlocked
                is_unlocked = current_value >= target_value
                unlocked_at = datetime.utcnow() if is_unlocked else None
                
                await achievement_repo.save_achievement_progress(
                    user_id, achievement_type, achievement_level,
                    current_value, target_value, is_unlocked, unlocked_at
                )
                
                if is_unlocked:
                    logger.info(f"Achievement unlocked: {user_id} - {achievement_type} {achievement_level}")
                
                return True
        except Exception as e:
            logger.error(f"Failed to update achievement progress: {e}")
            return False
    
    async def get_user_achievements(self, user_id: str) -> Dict[str, Any]:
        """
        Get user achievement statistics
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with achievement data
        """
        try:
            async with self.get_repositories() as (_, _, achievement_repo):
                achievements = await achievement_repo.get_user_achievements(user_id)
                stats = await achievement_repo.get_achievement_stats(user_id)
                
                return {
                    'achievements': [achievement.to_dict() for achievement in achievements],
                    'statistics': stats
                }
        except Exception as e:
            logger.error(f"Failed to get user achievements: {e}")
            return {'achievements': [], 'statistics': {}}
    
    # Health Check and Utilities
    async def health_check(self) -> bool:
        """
        Check database connectivity
        
        Returns:
            True if database is accessible
        """
        return await self.db_manager.health_check()
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        try:
            async with self.get_repositories() as (user_repo, health_repo, achievement_repo):
                user_count = await user_repo.count()
                activity_count = await health_repo.activity_repo.count()
                sleep_count = await health_repo.sleep_repo.count()
                achievement_count = await achievement_repo.count()
                
                return {
                    'users': user_count,
                    'activity_records': activity_count,
                    'sleep_records': sleep_count,
                    'achievement_records': achievement_count,
                    'database_url': self.db_manager.database_url,
                    'is_healthy': await self.health_check()
                }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}


# Global database service instance
_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """
    Get global database service instance
    
    Returns:
        DatabaseService instance
    """
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
