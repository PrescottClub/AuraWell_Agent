"""
Achievement Repository

Provides data access operations for achievement and gamification data.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, cast, Integer

from .base import BaseRepository
from ..database.models import AchievementProgressDB


class AchievementRepository(BaseRepository[AchievementProgressDB]):
    """Repository for achievement operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AchievementProgressDB)
    
    async def save_achievement_progress(self, user_id: str, 
                                      achievement_type: str,
                                      achievement_level: str,
                                      current_value: float,
                                      target_value: float,
                                      is_unlocked: bool = False,
                                      unlocked_at: Optional[datetime] = None) -> AchievementProgressDB:
        """
        Save or update achievement progress
        
        Args:
            user_id: User identifier
            achievement_type: Type of achievement
            achievement_level: Achievement level (bronze, silver, etc.)
            current_value: Current progress value
            target_value: Target value for completion
            is_unlocked: Whether achievement is unlocked
            unlocked_at: Timestamp when unlocked
            
        Returns:
            Saved AchievementProgressDB instance
        """
        progress_percentage = min(100.0, (current_value / target_value) * 100.0) if target_value > 0 else 0.0
        
        achievement_data = {
            "user_id": user_id,
            "achievement_type": achievement_type,
            "achievement_level": achievement_level,
            "current_value": current_value,
            "target_value": target_value,
            "is_unlocked": is_unlocked,
            "unlocked_at": unlocked_at,
            "progress_percentage": progress_percentage,
            "last_updated": datetime.now(timezone.utc),
        }
        
        # Use upsert to handle duplicates
        unique_fields = {
            "user_id": user_id,
            "achievement_type": achievement_type,
            "achievement_level": achievement_level
        }
        
        return await self.upsert(unique_fields, **achievement_data)
    
    async def get_user_achievements(self, user_id: str,
                                  achievement_type: Optional[str] = None,
                                  unlocked_only: bool = False) -> List[AchievementProgressDB]:
        """
        Get achievements for user with optional filters
        
        Args:
            user_id: User identifier
            achievement_type: Optional achievement type filter
            unlocked_only: If True, return only unlocked achievements
            
        Returns:
            List of AchievementProgressDB instances
        """
        stmt = select(AchievementProgressDB).where(
            AchievementProgressDB.user_id == user_id
        )
        
        if achievement_type:
            stmt = stmt.where(AchievementProgressDB.achievement_type == achievement_type)
        
        if unlocked_only:
            stmt = stmt.where(AchievementProgressDB.is_unlocked == True)
        
        stmt = stmt.order_by(
            desc(AchievementProgressDB.is_unlocked),
            desc(AchievementProgressDB.progress_percentage),
            AchievementProgressDB.achievement_type
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_achievement_progress(self, user_id: str,
                                     achievement_type: str,
                                     achievement_level: str) -> Optional[AchievementProgressDB]:
        """
        Get specific achievement progress
        
        Args:
            user_id: User identifier
            achievement_type: Achievement type
            achievement_level: Achievement level
            
        Returns:
            AchievementProgressDB instance or None
        """
        stmt = select(AchievementProgressDB).where(
            and_(
                AchievementProgressDB.user_id == user_id,
                AchievementProgressDB.achievement_type == achievement_type,
                AchievementProgressDB.achievement_level == achievement_level
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def unlock_achievement(self, user_id: str,
                               achievement_type: str,
                               achievement_level: str,
                               unlocked_at: Optional[datetime] = None) -> bool:
        """
        Mark achievement as unlocked
        
        Args:
            user_id: User identifier
            achievement_type: Achievement type
            achievement_level: Achievement level
            unlocked_at: Unlock timestamp (defaults to now)
            
        Returns:
            True if achievement was unlocked successfully
        """
        if unlocked_at is None:
            unlocked_at = datetime.now(timezone.utc)
        
        achievement = await self.get_achievement_progress(
            user_id, achievement_type, achievement_level
        )
        
        if achievement and not achievement.is_unlocked:
            achievement.is_unlocked = True
            achievement.unlocked_at = unlocked_at
            achievement.progress_percentage = 100.0
            achievement.last_updated = datetime.now(timezone.utc)
            await self.session.flush()
            return True
        
        return False
    
    async def get_unlocked_achievements(self, user_id: str,
                                      since: Optional[datetime] = None) -> List[AchievementProgressDB]:
        """
        Get unlocked achievements for user
        
        Args:
            user_id: User identifier
            since: Optional timestamp to filter recent unlocks
            
        Returns:
            List of unlocked AchievementProgressDB instances
        """
        stmt = select(AchievementProgressDB).where(
            and_(
                AchievementProgressDB.user_id == user_id,
                AchievementProgressDB.is_unlocked == True
            )
        )
        
        if since:
            stmt = stmt.where(AchievementProgressDB.unlocked_at >= since)
        
        stmt = stmt.order_by(desc(AchievementProgressDB.unlocked_at))
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_achievement_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get achievement statistics for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with achievement statistics
        """
        # Total achievements
        total_stmt = select(func.count()).select_from(AchievementProgressDB).where(
            AchievementProgressDB.user_id == user_id
        )
        total_result = await self.session.execute(total_stmt)
        total_achievements = total_result.scalar()
        
        # Unlocked achievements
        unlocked_stmt = select(func.count()).select_from(AchievementProgressDB).where(
            and_(
                AchievementProgressDB.user_id == user_id,
                AchievementProgressDB.is_unlocked == True
            )
        )
        unlocked_result = await self.session.execute(unlocked_stmt)
        unlocked_achievements = unlocked_result.scalar()
        
        # Average progress
        avg_stmt = select(func.avg(AchievementProgressDB.progress_percentage)).where(
            AchievementProgressDB.user_id == user_id
        )
        avg_result = await self.session.execute(avg_stmt)
        avg_progress = avg_result.scalar() or 0.0
        
        # Achievements by type
        type_stmt = select(
            AchievementProgressDB.achievement_type,
            func.count().label('total'),
            func.sum(cast(AchievementProgressDB.is_unlocked, Integer)).label('unlocked')
        ).where(
            AchievementProgressDB.user_id == user_id
        ).group_by(AchievementProgressDB.achievement_type)
        
        type_result = await self.session.execute(type_stmt)
        achievements_by_type = {
            row.achievement_type: {
                'total': row.total,
                'unlocked': row.unlocked or 0
            }
            for row in type_result
        }
        
        return {
            'total_achievements': total_achievements,
            'unlocked_achievements': unlocked_achievements,
            'completion_percentage': (unlocked_achievements / total_achievements * 100.0) if total_achievements > 0 else 0.0,
            'average_progress': round(avg_progress, 2),
            'achievements_by_type': achievements_by_type
        }
    
    async def get_leaderboard(self, achievement_type: Optional[str] = None,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get achievement leaderboard
        
        Args:
            achievement_type: Optional achievement type filter
            limit: Maximum number of results
            
        Returns:
            List of user achievement statistics
        """
        if achievement_type:
            # Leaderboard for specific achievement type
            stmt = select(
                AchievementProgressDB.user_id,
                func.count().label('total'),
                func.sum(cast(AchievementProgressDB.is_unlocked, Integer)).label('unlocked'),
                func.avg(AchievementProgressDB.progress_percentage).label('avg_progress')
            ).where(
                AchievementProgressDB.achievement_type == achievement_type
            ).group_by(
                AchievementProgressDB.user_id
            ).order_by(
                desc('unlocked'),
                desc('avg_progress')
            ).limit(limit)
        else:
            # Overall leaderboard
            stmt = select(
                AchievementProgressDB.user_id,
                func.count().label('total'),
                func.sum(cast(AchievementProgressDB.is_unlocked, Integer)).label('unlocked'),
                func.avg(AchievementProgressDB.progress_percentage).label('avg_progress')
            ).group_by(
                AchievementProgressDB.user_id
            ).order_by(
                desc('unlocked'),
                desc('avg_progress')
            ).limit(limit)
        
        result = await self.session.execute(stmt)
        
        leaderboard = []
        for i, row in enumerate(result, 1):
            leaderboard.append({
                'rank': i,
                'user_id': row.user_id,
                'total_achievements': row.total,
                'unlocked_achievements': row.unlocked or 0,
                'completion_percentage': (row.unlocked / row.total * 100.0) if row.total > 0 else 0.0,
                'average_progress': round(row.avg_progress or 0.0, 2)
            })
        
        return leaderboard
