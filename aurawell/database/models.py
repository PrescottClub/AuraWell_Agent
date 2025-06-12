"""
SQLAlchemy Database Models

Defines database schema for AuraWell health data persistence.
Maps Pydantic models to SQLAlchemy ORM models for database storage.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Date, Text, JSON,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserProfileDB(Base):
    """User profile database model"""
    __tablename__ = "user_profiles"
    
    # Primary key
    user_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # Basic info
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    height_cm: Mapped[Optional[float]] = mapped_column(Float)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    
    # Activity and goals
    activity_level: Mapped[Optional[str]] = mapped_column(String(50))
    daily_steps_goal: Mapped[Optional[int]] = mapped_column(Integer)
    daily_calories_goal: Mapped[Optional[float]] = mapped_column(Float)
    sleep_duration_goal_hours: Mapped[Optional[float]] = mapped_column(Float)
    weekly_exercise_minutes_goal: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Preferences (stored as JSON)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    preferred_units: Mapped[str] = mapped_column(String(20), default="metric")
    notification_preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    connected_platforms: Mapped[List[str]] = mapped_column(JSON, default=list)
    platform_user_ids: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)
    
    # Health goals (stored as JSON)
    health_goals: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # Relationships
    activity_summaries = relationship("ActivitySummaryDB", back_populates="user")
    sleep_sessions = relationship("SleepSessionDB", back_populates="user")
    heart_rate_samples = relationship("HeartRateSampleDB", back_populates="user")
    nutrition_entries = relationship("NutritionEntryDB", back_populates="user")
    achievement_progress = relationship("AchievementProgressDB", back_populates="user")
    platform_connections = relationship("PlatformConnectionDB", back_populates="user")
    conversations = relationship("ConversationDB", back_populates="user")
    health_profile = relationship("UserHealthProfileDB", back_populates="user", uselist=False)


class ActivitySummaryDB(Base):
    """Daily activity summary database model"""
    __tablename__ = "activity_summaries"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"))
    
    # Activity data
    date: Mapped[date] = mapped_column(Date, nullable=False)
    steps: Mapped[Optional[int]] = mapped_column(Integer)
    distance_meters: Mapped[Optional[float]] = mapped_column(Float)
    active_calories: Mapped[Optional[float]] = mapped_column(Float)
    total_calories: Mapped[Optional[float]] = mapped_column(Float)
    active_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Metadata
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    data_quality: Mapped[str] = mapped_column(String(20), default="unknown")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="activity_summaries")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "date", "source_platform", name="uq_user_date_platform"),
        Index("idx_activity_user_date", "user_id", "date"),
    )


class SleepSessionDB(Base):
    """Sleep session database model"""
    __tablename__ = "sleep_sessions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"))
    
    # Sleep data
    date: Mapped[date] = mapped_column(Date, nullable=False)
    bedtime_utc: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    wake_time_utc: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_sleep_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    deep_sleep_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    light_sleep_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    rem_sleep_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    awake_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    sleep_efficiency: Mapped[Optional[float]] = mapped_column(Float)
    sleep_quality_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Metadata
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    data_quality: Mapped[str] = mapped_column(String(20), default="unknown")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="sleep_sessions")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "date", "source_platform", name="uq_sleep_user_date_platform"),
        Index("idx_sleep_user_date", "user_id", "date"),
    )


class HeartRateSampleDB(Base):
    """Heart rate sample database model"""
    __tablename__ = "heart_rate_samples"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"))
    
    # Heart rate data
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    bpm: Mapped[int] = mapped_column(Integer, nullable=False)
    measurement_type: Mapped[str] = mapped_column(String(50), default="unknown")
    context: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Metadata
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    data_quality: Mapped[str] = mapped_column(String(20), default="unknown")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="heart_rate_samples")
    
    # Constraints
    __table_args__ = (
        Index("idx_hr_user_timestamp", "user_id", "timestamp_utc"),
    )


class NutritionEntryDB(Base):
    """Nutrition entry database model"""
    __tablename__ = "nutrition_entries"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"))
    
    # Nutrition data
    date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[Optional[str]] = mapped_column(String(50))
    food_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    calories: Mapped[Optional[float]] = mapped_column(Float)
    protein_g: Mapped[Optional[float]] = mapped_column(Float)
    carbs_g: Mapped[Optional[float]] = mapped_column(Float)
    fat_g: Mapped[Optional[float]] = mapped_column(Float)
    fiber_g: Mapped[Optional[float]] = mapped_column(Float)
    sugar_g: Mapped[Optional[float]] = mapped_column(Float)
    sodium_mg: Mapped[Optional[float]] = mapped_column(Float)
    
    # Metadata
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    data_quality: Mapped[str] = mapped_column(String(20), default="unknown")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="nutrition_entries")
    
    # Constraints
    __table_args__ = (
        Index("idx_nutrition_user_date", "user_id", "date"),
    )


class AchievementProgressDB(Base):
    """Achievement progress database model"""
    __tablename__ = "achievement_progress"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"))
    
    # Achievement data
    achievement_type: Mapped[str] = mapped_column(String(100), nullable=False)
    achievement_level: Mapped[str] = mapped_column(String(50), nullable=False)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    unlocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Progress tracking
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("UserProfileDB", back_populates="achievement_progress")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_type", "achievement_level", 
                        name="uq_user_achievement"),
        Index("idx_achievement_user_type", "user_id", "achievement_type"),
    )


class PlatformConnectionDB(Base):
    """Platform connection database model"""
    __tablename__ = "platform_connections"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"))

    # Platform data
    platform_name: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Connection status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sync_status: Mapped[str] = mapped_column(String(50), default="pending")

    # Configuration (stored as JSON)
    sync_preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    user = relationship("UserProfileDB", back_populates="platform_connections")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "platform_name", name="uq_user_platform"),
        Index("idx_platform_user_name", "user_id", "platform_name"),
    )


class ConversationDB(Base):
    """Conversation database model for health chat sessions"""
    __tablename__ = "conversations"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"))

    # Conversation metadata
    title: Mapped[Optional[str]] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(50), default="health_consultation")
    status: Mapped[str] = mapped_column(String(20), default="active")

    # Additional metadata (stored as JSON)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("UserProfileDB")
    messages = relationship("MessageDB", back_populates="conversation", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        Index("idx_conversation_user_id", "user_id"),
        Index("idx_conversation_created_at", "created_at"),
        Index("idx_conversation_status", "status"),
    )


class MessageDB(Base):
    """Message database model for chat messages"""
    __tablename__ = "messages"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign keys
    conversation_id: Mapped[str] = mapped_column(String(255), ForeignKey("conversations.id"))

    # Message data
    sender: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'agent'
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Additional message metadata (stored as JSON)
    extra_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    conversation = relationship("ConversationDB", back_populates="messages")

    # Constraints
    __table_args__ = (
        Index("idx_message_conversation_id", "conversation_id"),
        Index("idx_message_created_at", "created_at"),
        Index("idx_message_sender", "sender"),
    )


class UserHealthProfileDB(Base):
    """User health profile database model for storing health-specific information"""
    __tablename__ = "user_health_profiles"

    # Primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Foreign key
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("user_profiles.user_id"), unique=True)

    # Basic health information (stored as JSON for flexibility)
    basic_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # height, weight, age, etc.
    health_goals: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # weight loss, fitness goals, etc.
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # dietary preferences, exercise preferences
    medical_history: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # encrypted sensitive data

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("UserProfileDB")

    # Constraints
    __table_args__ = (
        Index("idx_health_profile_user_id", "user_id"),
    )
