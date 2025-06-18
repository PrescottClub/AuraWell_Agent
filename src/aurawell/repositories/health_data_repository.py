"""
Health Data Repository

Provides data access operations for health data (activity, sleep, heart rate, nutrition).
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, asc
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..database.models import (
    ActivitySummaryDB,
    SleepSessionDB,
    HeartRateSampleDB,
    NutritionEntryDB,
)
from ..models.health_data_model import (
    UnifiedActivitySummary,
    UnifiedSleepSession,
    UnifiedHeartRateSample,
    NutritionEntry,
)
from ..models.enums import HealthPlatform, DataQuality


class HealthDataRepository:
    """Repository for health data operations"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.activity_repo = BaseRepository[ActivitySummaryDB](session, ActivitySummaryDB)
        self.sleep_repo = BaseRepository[SleepSessionDB](session, SleepSessionDB)
        self.heart_rate_repo = BaseRepository[HeartRateSampleDB](session, HeartRateSampleDB)
        self.nutrition_repo = BaseRepository[NutritionEntryDB](session, NutritionEntryDB)
    
    # Activity Data Methods
    async def save_activity_summary(
        self, user_id: str, activity: UnifiedActivitySummary
    ) -> ActivitySummaryDB:
        """
        Save activity summary data

        Args:
            user_id: User identifier
            activity: UnifiedActivitySummary Pydantic model

        Returns:
            Saved ActivitySummaryDB instance
        """
        activity_data = {
            "user_id": user_id,
            "date": datetime.strptime(activity.date, "%Y-%m-%d").date(),
            "steps": activity.steps,
            "distance_meters": activity.distance_meters,
            "active_calories": activity.active_calories,
            "total_calories": activity.total_calories,
            "active_minutes": activity.active_minutes,
            "source_platform": activity.source_platform.value,
            "data_quality": activity.data_quality.value,
            "recorded_at": activity.recorded_at,
        }

        # Use upsert to handle duplicates
        unique_fields = {
            "user_id": user_id,
            "date": activity_data["date"],
            "source_platform": activity_data["source_platform"],
        }

        return await self.activity_repo.upsert(unique_fields, **activity_data)

    async def get_activity_summaries(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        platform: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[ActivitySummaryDB]:
        """
        Get activity summaries for user with optional filters

        Args:
            user_id: User identifier
            start_date: Start date filter
            end_date: End date filter
            platform: Platform filter
            limit: Maximum number of records

        Returns:
            List of ActivitySummaryDB instances
        """
        stmt = select(ActivitySummaryDB).where(ActivitySummaryDB.user_id == user_id)

        if start_date:
            stmt = stmt.where(ActivitySummaryDB.date >= start_date)
        if end_date:
            stmt = stmt.where(ActivitySummaryDB.date <= end_date)
        if platform:
            stmt = stmt.where(ActivitySummaryDB.source_platform == platform)

        stmt = stmt.order_by(desc(ActivitySummaryDB.date))

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_activity(
        self, user_id: str, platform: Optional[str] = None
    ) -> Optional[ActivitySummaryDB]:
        """
        Get latest activity summary for user

        Args:
            user_id: User identifier
            platform: Optional platform filter

        Returns:
            Latest ActivitySummaryDB instance or None
        """
        stmt = select(ActivitySummaryDB).where(ActivitySummaryDB.user_id == user_id)

        if platform:
            stmt = stmt.where(ActivitySummaryDB.source_platform == platform)

        stmt = stmt.order_by(desc(ActivitySummaryDB.date)).limit(1)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Sleep Data Methods
    async def save_sleep_session(
        self, user_id: str, sleep: UnifiedSleepSession
    ) -> SleepSessionDB:
        """
        Save sleep session data

        Args:
            user_id: User identifier
            sleep: UnifiedSleepSession Pydantic model

        Returns:
            Saved SleepSessionDB instance
        """
        # Extract date from start_time_utc
        sleep_date = sleep.start_time_utc.date()

        sleep_data = {
            "user_id": user_id,
            "date": sleep_date,
            "bedtime_utc": sleep.start_time_utc,
            "wake_time_utc": sleep.end_time_utc,
            "total_sleep_minutes": (
                sleep.total_duration_seconds // 60
                if sleep.total_duration_seconds
                else None
            ),
            "deep_sleep_minutes": (
                sleep.deep_sleep_seconds // 60 if sleep.deep_sleep_seconds else None
            ),
            "light_sleep_minutes": (
                sleep.light_sleep_seconds // 60 if sleep.light_sleep_seconds else None
            ),
            "rem_sleep_minutes": (
                sleep.rem_sleep_seconds // 60 if sleep.rem_sleep_seconds else None
            ),
            "awake_minutes": sleep.awake_seconds // 60 if sleep.awake_seconds else None,
            "sleep_efficiency": sleep.sleep_efficiency,
            "sleep_quality_score": None,  # UnifiedSleepSession doesn't have this field
            "source_platform": sleep.source_platform.value,
            "data_quality": sleep.data_quality.value,
            "recorded_at": sleep.recorded_at,
        }

        # Use upsert to handle duplicates
        unique_fields = {
            "user_id": user_id,
            "date": sleep_data["date"],
            "source_platform": sleep_data["source_platform"],
        }

        return await self.sleep_repo.upsert(unique_fields, **sleep_data)

    async def get_sleep_sessions(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        platform: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[SleepSessionDB]:
        """
        Get sleep sessions for user with optional filters

        Args:
            user_id: User identifier
            start_date: Start date filter
            end_date: End date filter
            platform: Platform filter
            limit: Maximum number of records

        Returns:
            List of SleepSessionDB instances
        """
        stmt = select(SleepSessionDB).where(SleepSessionDB.user_id == user_id)

        if start_date:
            stmt = stmt.where(SleepSessionDB.date >= start_date)
        if end_date:
            stmt = stmt.where(SleepSessionDB.date <= end_date)
        if platform:
            stmt = stmt.where(SleepSessionDB.source_platform == platform)

        stmt = stmt.order_by(desc(SleepSessionDB.date))

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Heart Rate Data Methods
    async def save_heart_rate_sample(
        self, user_id: str, heart_rate: UnifiedHeartRateSample
    ) -> HeartRateSampleDB:
        """
        Save heart rate sample data

        Args:
            user_id: User identifier
            heart_rate: UnifiedHeartRateSample Pydantic model

        Returns:
            Saved HeartRateSampleDB instance
        """
        hr_data = {
            "user_id": user_id,
            "timestamp_utc": heart_rate.timestamp_utc,
            "bpm": heart_rate.bpm,
            "measurement_type": heart_rate.measurement_type.value,
            "context": heart_rate.context,
            "source_platform": heart_rate.source_platform.value,
            "data_quality": heart_rate.data_quality.value,
            "recorded_at": heart_rate.recorded_at,
        }

        return await self.heart_rate_repo.create(**hr_data)

    async def get_heart_rate_samples(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        measurement_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[HeartRateSampleDB]:
        """
        Get heart rate samples for user with optional filters

        Args:
            user_id: User identifier
            start_time: Start timestamp filter
            end_time: End timestamp filter
            measurement_type: Measurement type filter
            limit: Maximum number of records

        Returns:
            List of HeartRateSampleDB instances
        """
        stmt = select(HeartRateSampleDB).where(HeartRateSampleDB.user_id == user_id)

        if start_time:
            stmt = stmt.where(HeartRateSampleDB.timestamp_utc >= start_time)
        if end_time:
            stmt = stmt.where(HeartRateSampleDB.timestamp_utc <= end_time)
        if measurement_type:
            stmt = stmt.where(HeartRateSampleDB.measurement_type == measurement_type)

        stmt = stmt.order_by(desc(HeartRateSampleDB.timestamp_utc))

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Nutrition Data Methods
    async def save_nutrition_entry(
        self, user_id: str, nutrition: NutritionEntry
    ) -> NutritionEntryDB:
        """
        Save nutrition entry data

        Args:
            user_id: User identifier
            nutrition: NutritionEntry Pydantic model

        Returns:
            Saved NutritionEntryDB instance
        """
        nutrition_data = {
            "user_id": user_id,
            "date": datetime.strptime(nutrition.date, "%Y-%m-%d").date(),
            "meal_type": nutrition.meal_type,
            "food_name": nutrition.food_name,
            "quantity": nutrition.quantity,
            "unit": nutrition.unit,
            "calories": nutrition.calories,
            "protein_g": nutrition.protein_g,
            "carbs_g": nutrition.carbs_g,
            "fat_g": nutrition.fat_g,
            "fiber_g": nutrition.fiber_g,
            "sugar_g": nutrition.sugar_g,
            "sodium_mg": nutrition.sodium_mg,
            "source_platform": nutrition.source_platform.value,
            "data_quality": nutrition.data_quality.value,
            "recorded_at": nutrition.recorded_at,
        }

        return await self.nutrition_repo.create(**nutrition_data)

    async def get_nutrition_entries(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        meal_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[NutritionEntryDB]:
        """
        Get nutrition entries for user with optional filters

        Args:
            user_id: User identifier
            start_date: Start date filter
            end_date: End date filter
            meal_type: Meal type filter
            limit: Maximum number of records

        Returns:
            List of NutritionEntryDB instances
        """
        stmt = select(NutritionEntryDB).where(NutritionEntryDB.user_id == user_id)

        if start_date:
            stmt = stmt.where(NutritionEntryDB.date >= start_date)
        if end_date:
            stmt = stmt.where(NutritionEntryDB.date <= end_date)
        if meal_type:
            stmt = stmt.where(NutritionEntryDB.meal_type == meal_type)

        stmt = stmt.order_by(desc(NutritionEntryDB.date))

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
