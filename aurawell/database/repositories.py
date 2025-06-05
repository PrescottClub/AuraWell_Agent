"""
Repository Pattern Implementation for AuraWell

Provides data access layer with CRUD operations for all entities.
Implements the Repository pattern to abstract database operations.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

from .connection import DatabaseManager
from .models import UserModel, HealthDataModel, InsightModel, PlanModel, convert_datetime_fields

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Base repository class with common functionality"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def _ensure_connected(self) -> None:
        """Ensure database connection is active"""
        if not self.db_manager.is_connected():
            if not self.db_manager.connect():
                raise RuntimeError("Failed to connect to database")


class UserRepository(BaseRepository):
    """Repository for user data operations"""
    
    def create_user(self, user: UserModel) -> bool:
        """
        Create a new user
        
        Args:
            user: User model to create
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()
        
        try:
            query = """
                INSERT INTO users (
                    user_id, email, display_name, age, gender, height_cm, weight_kg,
                    activity_level, primary_goal, daily_steps_goal, sleep_duration_goal_hours,
                    timezone, preferences, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """
            
            now = datetime.now(timezone.utc)
            params = (
                user.user_id, user.email, user.display_name, user.age, user.gender,
                user.height_cm, user.weight_kg, user.activity_level, user.primary_goal,
                user.daily_steps_goal, user.sleep_duration_goal_hours, user.timezone,
                user.preferences, now, now
            )
            
            with self.db_manager.transaction():
                self.db_manager.execute_query(query, params, fetch_all=False)
            
            logger.info(f"Created user: {user.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create user {user.user_id}: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[UserModel]:
        """
        Get user by ID
        
        Args:
            user_id: User identifier
            
        Returns:
            User model or None if not found
        """
        self._ensure_connected()
        
        try:
            query = "SELECT * FROM users WHERE user_id = ?"
            result = self.db_manager.execute_query(query, (user_id,), fetch_one=True)
            
            if result:
                # Convert datetime fields
                result = convert_datetime_fields(result, ['created_at', 'updated_at'])
                return UserModel.from_dict(result)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    def update_user(self, user: UserModel) -> bool:
        """
        Update existing user
        
        Args:
            user: User model with updated data
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()
        
        try:
            query = """
                UPDATE users SET
                    email = ?, display_name = ?, age = ?, gender = ?, height_cm = ?,
                    weight_kg = ?, activity_level = ?, primary_goal = ?,
                    daily_steps_goal = ?, sleep_duration_goal_hours = ?, timezone = ?,
                    preferences = ?, updated_at = ?
                WHERE user_id = ?
            """
            
            now = datetime.now(timezone.utc)
            params = (
                user.email, user.display_name, user.age, user.gender, user.height_cm,
                user.weight_kg, user.activity_level, user.primary_goal,
                user.daily_steps_goal, user.sleep_duration_goal_hours, user.timezone,
                user.preferences, now, user.user_id
            )
            
            with self.db_manager.transaction():
                self.db_manager.execute_query(query, params, fetch_all=False)
            
            logger.info(f"Updated user: {user.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user {user.user_id}: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user and all associated data
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()
        
        try:
            with self.db_manager.transaction():
                # Delete in order to respect foreign key constraints
                queries = [
                    "DELETE FROM health_plans WHERE user_id = ?",
                    "DELETE FROM insights WHERE user_id = ?",
                    "DELETE FROM health_data WHERE user_id = ?",
                    "DELETE FROM users WHERE user_id = ?"
                ]
                
                for query in queries:
                    self.db_manager.execute_query(query, (user_id,), fetch_all=False)
            
            logger.info(f"Deleted user and all data: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[UserModel]:
        """
        List users with pagination
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of user models
        """
        self._ensure_connected()
        
        try:
            query = "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?"
            results = self.db_manager.execute_query(query, (limit, offset))
            
            users = []
            for result in results:
                result = convert_datetime_fields(result, ['created_at', 'updated_at'])
                users.append(UserModel.from_dict(result))
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []


class HealthDataRepository(BaseRepository):
    """Repository for health data operations"""
    
    def store_health_data(self, health_data: HealthDataModel) -> bool:
        """
        Store health data
        
        Args:
            health_data: Health data model to store
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()
        
        try:
            query = """
                INSERT INTO health_data (
                    user_id, data_type, date, data_json, source_platform, data_quality, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            data_dict = health_data.to_dict()
            params = (
                health_data.user_id, health_data.data_type, health_data.date,
                data_dict['data_json'], health_data.source_platform, health_data.data_quality,
                datetime.now(timezone.utc)
            )
            
            with self.db_manager.transaction():
                self.db_manager.execute_query(query, params, fetch_all=False)
            
            logger.info(f"Stored health data for user {health_data.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store health data: {e}")
            return False
    
    def get_health_data(
        self,
        user_id: str,
        data_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[HealthDataModel]:
        """
        Get health data for user with optional filters
        
        Args:
            user_id: User identifier
            data_type: Optional data type filter
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            limit: Maximum number of records
            
        Returns:
            List of health data models
        """
        self._ensure_connected()
        
        try:
            query = "SELECT * FROM health_data WHERE user_id = ?"
            params = [user_id]
            
            if data_type:
                query += " AND data_type = ?"
                params.append(data_type)
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)
            
            results = self.db_manager.execute_query(query, tuple(params))
            
            health_data_list = []
            for result in results:
                result = convert_datetime_fields(result, ['created_at'])
                health_data_list.append(HealthDataModel.from_dict(result))
            
            return health_data_list
            
        except Exception as e:
            logger.error(f"Failed to get health data for user {user_id}: {e}")
            return []


class InsightRepository(BaseRepository):
    """Repository for health insights operations"""

    def store_insight(self, insight: InsightModel) -> bool:
        """
        Store health insight

        Args:
            insight: Insight model to store

        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()

        try:
            query = """
                INSERT INTO insights (
                    insight_id, user_id, insight_type, priority, title, description,
                    recommendations, data_points, confidence_score, generated_at,
                    expires_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            data_dict = insight.to_dict()
            params = (
                insight.insight_id, insight.user_id, insight.insight_type, insight.priority,
                insight.title, insight.description, data_dict.get('recommendations'),
                data_dict.get('data_points'), insight.confidence_score, insight.generated_at,
                insight.expires_at, datetime.now(timezone.utc)
            )

            with self.db_manager.transaction():
                self.db_manager.execute_query(query, params, fetch_all=False)

            logger.info(f"Stored insight {insight.insight_id} for user {insight.user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store insight: {e}")
            return False

    def get_user_insights(
        self,
        user_id: str,
        insight_type: Optional[str] = None,
        priority: Optional[str] = None,
        active_only: bool = True,
        limit: int = 50
    ) -> List[InsightModel]:
        """
        Get insights for user with optional filters

        Args:
            user_id: User identifier
            insight_type: Optional insight type filter
            priority: Optional priority filter
            active_only: Only return non-expired insights
            limit: Maximum number of insights

        Returns:
            List of insight models
        """
        self._ensure_connected()

        try:
            query = "SELECT * FROM insights WHERE user_id = ?"
            params = [user_id]

            if insight_type:
                query += " AND insight_type = ?"
                params.append(insight_type)

            if priority:
                query += " AND priority = ?"
                params.append(priority)

            if active_only:
                query += " AND (expires_at IS NULL OR expires_at > ?)"
                params.append(datetime.now(timezone.utc))

            query += " ORDER BY generated_at DESC LIMIT ?"
            params.append(limit)

            results = self.db_manager.execute_query(query, tuple(params))

            insights = []
            for result in results:
                result = convert_datetime_fields(result, ['generated_at', 'expires_at', 'created_at'])
                insights.append(InsightModel.from_dict(result))

            return insights

        except Exception as e:
            logger.error(f"Failed to get insights for user {user_id}: {e}")
            return []

    def delete_expired_insights(self) -> int:
        """
        Delete expired insights

        Returns:
            Number of deleted insights
        """
        self._ensure_connected()

        try:
            query = "DELETE FROM insights WHERE expires_at IS NOT NULL AND expires_at <= ?"

            with self.db_manager.transaction():
                cursor = self.db_manager._connection.cursor()
                cursor.execute(query, (datetime.now(timezone.utc),))
                deleted_count = cursor.rowcount
                cursor.close()

            logger.info(f"Deleted {deleted_count} expired insights")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete expired insights: {e}")
            return 0


class PlanRepository(BaseRepository):
    """Repository for health plans operations"""

    def store_plan(self, plan: PlanModel) -> bool:
        """
        Store health plan

        Args:
            plan: Plan model to store

        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()

        try:
            query = """
                INSERT INTO health_plans (
                    plan_id, user_id, title, description, goals, daily_recommendations,
                    weekly_targets, created_at, valid_until, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            data_dict = plan.to_dict()
            params = (
                plan.plan_id, plan.user_id, plan.title, plan.description,
                data_dict.get('goals'), data_dict.get('daily_recommendations'),
                data_dict.get('weekly_targets'), plan.created_at, plan.valid_until,
                plan.last_updated
            )

            with self.db_manager.transaction():
                self.db_manager.execute_query(query, params, fetch_all=False)

            logger.info(f"Stored plan {plan.plan_id} for user {plan.user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store plan: {e}")
            return False

    def get_user_plan(self, user_id: str, active_only: bool = True) -> Optional[PlanModel]:
        """
        Get current health plan for user

        Args:
            user_id: User identifier
            active_only: Only return non-expired plans

        Returns:
            Plan model or None if not found
        """
        self._ensure_connected()

        try:
            query = "SELECT * FROM health_plans WHERE user_id = ?"
            params = [user_id]

            if active_only:
                query += " AND valid_until > ?"
                params.append(datetime.now(timezone.utc))

            query += " ORDER BY created_at DESC LIMIT 1"

            result = self.db_manager.execute_query(query, tuple(params), fetch_one=True)

            if result:
                result = convert_datetime_fields(result, ['created_at', 'valid_until', 'last_updated'])
                return PlanModel.from_dict(result)

            return None

        except Exception as e:
            logger.error(f"Failed to get plan for user {user_id}: {e}")
            return None

    def update_plan(self, plan: PlanModel) -> bool:
        """
        Update existing health plan

        Args:
            plan: Plan model with updated data

        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()

        try:
            query = """
                UPDATE health_plans SET
                    title = ?, description = ?, goals = ?, daily_recommendations = ?,
                    weekly_targets = ?, valid_until = ?, last_updated = ?
                WHERE plan_id = ?
            """

            data_dict = plan.to_dict()
            params = (
                plan.title, plan.description, data_dict.get('goals'),
                data_dict.get('daily_recommendations'), data_dict.get('weekly_targets'),
                plan.valid_until, datetime.now(timezone.utc), plan.plan_id
            )

            with self.db_manager.transaction():
                self.db_manager.execute_query(query, params, fetch_all=False)

            logger.info(f"Updated plan {plan.plan_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update plan {plan.plan_id}: {e}")
            return False
