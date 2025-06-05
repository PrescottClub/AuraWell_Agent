"""
Database Models for AuraWell

Defines database models that correspond to the database schema.
These models provide a bridge between the application domain models
and the database storage layer.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class UserModel:
    """Database model for user data"""
    user_id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    primary_goal: Optional[str] = None
    daily_steps_goal: Optional[int] = None
    sleep_duration_goal_hours: Optional[float] = None
    timezone: str = "UTC"
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None  # Database primary key
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        # Convert preferences to JSON string for SQLite
        if self.preferences:
            data['preferences'] = json.dumps(self.preferences)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        """Create from database row dictionary"""
        # Parse preferences JSON
        if data.get('preferences') and isinstance(data['preferences'], str):
            try:
                data['preferences'] = json.loads(data['preferences'])
            except json.JSONDecodeError:
                data['preferences'] = {}
        
        return cls(**data)


@dataclass
class HealthDataModel:
    """Database model for health data"""
    user_id: str
    data_type: str  # 'activity', 'sleep', 'heart_rate', 'nutrition'
    date: str  # YYYY-MM-DD format
    data_json: Dict[str, Any]
    source_platform: Optional[str] = None
    data_quality: Optional[str] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None  # Database primary key
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        # Convert data_json to JSON string for SQLite
        if self.data_json:
            data['data_json'] = json.dumps(self.data_json)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthDataModel':
        """Create from database row dictionary"""
        # Parse data_json
        if data.get('data_json') and isinstance(data['data_json'], str):
            try:
                data['data_json'] = json.loads(data['data_json'])
            except json.JSONDecodeError:
                data['data_json'] = {}
        
        return cls(**data)


@dataclass
class InsightModel:
    """Database model for health insights"""
    insight_id: str
    user_id: str
    insight_type: str
    priority: str
    title: str
    description: Optional[str] = None
    recommendations: Optional[List[str]] = None
    data_points: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    generated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None  # Database primary key
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        # Convert lists/dicts to JSON strings for SQLite
        if self.recommendations:
            data['recommendations'] = json.dumps(self.recommendations)
        if self.data_points:
            data['data_points'] = json.dumps(self.data_points)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InsightModel':
        """Create from database row dictionary"""
        # Parse JSON fields
        if data.get('recommendations') and isinstance(data['recommendations'], str):
            try:
                data['recommendations'] = json.loads(data['recommendations'])
            except json.JSONDecodeError:
                data['recommendations'] = []
        
        if data.get('data_points') and isinstance(data['data_points'], str):
            try:
                data['data_points'] = json.loads(data['data_points'])
            except json.JSONDecodeError:
                data['data_points'] = {}
        
        return cls(**data)


@dataclass
class PlanModel:
    """Database model for health plans"""
    plan_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    goals: Optional[List[Dict[str, Any]]] = None
    daily_recommendations: Optional[List[Dict[str, Any]]] = None
    weekly_targets: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    id: Optional[int] = None  # Database primary key
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        # Convert lists/dicts to JSON strings for SQLite
        if self.goals:
            data['goals'] = json.dumps(self.goals)
        if self.daily_recommendations:
            data['daily_recommendations'] = json.dumps(self.daily_recommendations)
        if self.weekly_targets:
            data['weekly_targets'] = json.dumps(self.weekly_targets)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanModel':
        """Create from database row dictionary"""
        # Parse JSON fields
        if data.get('goals') and isinstance(data['goals'], str):
            try:
                data['goals'] = json.loads(data['goals'])
            except json.JSONDecodeError:
                data['goals'] = []
        
        if data.get('daily_recommendations') and isinstance(data['daily_recommendations'], str):
            try:
                data['daily_recommendations'] = json.loads(data['daily_recommendations'])
            except json.JSONDecodeError:
                data['daily_recommendations'] = []
        
        if data.get('weekly_targets') and isinstance(data['weekly_targets'], str):
            try:
                data['weekly_targets'] = json.loads(data['weekly_targets'])
            except json.JSONDecodeError:
                data['weekly_targets'] = {}
        
        return cls(**data)


def convert_datetime_fields(data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """
    Convert datetime string fields to datetime objects
    
    Args:
        data: Dictionary containing the data
        fields: List of field names that should be converted to datetime
        
    Returns:
        Dictionary with converted datetime fields
    """
    converted_data = data.copy()
    
    for field in fields:
        if field in converted_data and converted_data[field]:
            if isinstance(converted_data[field], str):
                try:
                    # Try parsing ISO format
                    converted_data[field] = datetime.fromisoformat(
                        converted_data[field].replace('Z', '+00:00')
                    )
                except ValueError:
                    # Try parsing SQLite datetime format
                    try:
                        converted_data[field] = datetime.strptime(
                            converted_data[field], '%Y-%m-%d %H:%M:%S'
                        ).replace(tzinfo=timezone.utc)
                    except ValueError:
                        logger.warning(f"Could not parse datetime field {field}: {converted_data[field]}")
                        converted_data[field] = None
    
    return converted_data


def prepare_datetime_for_db(dt: Optional[datetime]) -> Optional[str]:
    """
    Prepare datetime for database storage
    
    Args:
        dt: Datetime object to convert
        
    Returns:
        ISO format string or None
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()


class ModelConverter:
    """Utility class for converting between domain models and database models"""
    
    @staticmethod
    def user_profile_to_db_model(user_profile: 'UserProfile') -> UserModel:
        """Convert UserProfile domain model to database model"""
        # This would be implemented when we have the domain models available
        # For now, return a placeholder
        return UserModel(user_id=user_profile.user_id)
    
    @staticmethod
    def db_model_to_user_profile(user_model: UserModel) -> 'UserProfile':
        """Convert database model to UserProfile domain model"""
        # This would be implemented when we have the domain models available
        # For now, return a placeholder
        pass
    
    @staticmethod
    def health_insight_to_db_model(insight: 'HealthInsight') -> InsightModel:
        """Convert HealthInsight domain model to database model"""
        # This would be implemented when we have the domain models available
        pass
    
    @staticmethod
    def db_model_to_health_insight(insight_model: InsightModel) -> 'HealthInsight':
        """Convert database model to HealthInsight domain model"""
        # This would be implemented when we have the domain models available
        pass
