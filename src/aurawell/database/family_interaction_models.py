"""
家庭交互功能数据库模型

包含成员点赞、健康告警等家庭互动功能的数据库模型
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import (
    String, Text, Boolean, Integer, DateTime, ForeignKey, 
    UniqueConstraint, Index, Enum as SQLEnum, JSON, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class FamilyMemberLikeDB(Base):
    """家庭成员点赞数据库模型"""
    
    __tablename__ = "family_member_likes"
    
    # 主键
    like_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    family_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False
    )
    liker_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    liked_member_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 点赞类型和内容
    like_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        default="general"  # general, achievement, progress, goal_completion
    )
    like_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关联的活动或成就ID（可选）
    related_activity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    related_achievement_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # 点赞状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系
    liker = relationship("UserProfileDB", foreign_keys=[liker_id])
    liked_member = relationship("UserProfileDB", foreign_keys=[liked_member_id])
    
    # 约束和索引
    __table_args__ = (
        UniqueConstraint("liker_id", "liked_member_id", "family_id", "like_type", 
                        name="uq_family_member_like"),
        Index("idx_family_like_family", "family_id"),
        Index("idx_family_like_liker", "liker_id"),
        Index("idx_family_like_liked", "liked_member_id"),
        Index("idx_family_like_type", "like_type"),
        Index("idx_family_like_active", "is_active"),
        Index("idx_family_like_created", "created_at"),
    )


class FamilyHealthAlertDB(Base):
    """家庭健康告警数据库模型"""
    
    __tablename__ = "family_health_alerts"
    
    # 主键
    alert_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    family_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False
    )
    member_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 告警基本信息
    alert_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # low_activity, insufficient_sleep, weight_change, heart_rate_abnormal, goal_missed
    
    severity: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="medium"
    )  # low, medium, high, critical
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 告警数据
    trigger_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metric_unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # 告警元数据
    alert_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="active"
    )  # active, acknowledged, resolved, dismissed
    
    acknowledged_by: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="SET NULL"),
        nullable=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # 通知设置
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_channels: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系
    member = relationship("UserProfileDB", foreign_keys=[member_id])
    acknowledger = relationship("UserProfileDB", foreign_keys=[acknowledged_by])
    
    # 约束和索引
    __table_args__ = (
        Index("idx_health_alert_family", "family_id"),
        Index("idx_health_alert_member", "member_id"),
        Index("idx_health_alert_type", "alert_type"),
        Index("idx_health_alert_severity", "severity"),
        Index("idx_health_alert_status", "status"),
        Index("idx_health_alert_created", "created_at"),
        Index("idx_health_alert_family_status", "family_id", "status"),
    )


class FamilyInteractionStatsDB(Base):
    """家庭互动统计数据库模型"""
    
    __tablename__ = "family_interaction_stats"
    
    # 主键
    stats_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    family_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False
    )
    member_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 统计周期
    stats_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stats_period: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="daily"
    )  # daily, weekly, monthly
    
    # 互动统计
    likes_given: Mapped[int] = mapped_column(Integer, default=0)
    likes_received: Mapped[int] = mapped_column(Integer, default=0)
    alerts_triggered: Mapped[int] = mapped_column(Integer, default=0)
    alerts_acknowledged: Mapped[int] = mapped_column(Integer, default=0)
    
    # 活跃度统计
    family_interactions: Mapped[int] = mapped_column(Integer, default=0)
    health_data_shares: Mapped[int] = mapped_column(Integer, default=0)
    
    # 扩展统计数据
    interaction_details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系
    member = relationship("UserProfileDB", foreign_keys=[member_id])
    
    # 约束和索引
    __table_args__ = (
        UniqueConstraint("family_id", "member_id", "stats_date", "stats_period", 
                        name="uq_family_interaction_stats"),
        Index("idx_interaction_stats_family", "family_id"),
        Index("idx_interaction_stats_member", "member_id"),
        Index("idx_interaction_stats_date", "stats_date"),
        Index("idx_interaction_stats_period", "stats_period"),
    )
