"""
家庭管理数据库模型

包含家庭、成员、邀请等核心家庭功能的数据库模型
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import (
    String, Text, Boolean, Integer, DateTime, ForeignKey, 
    UniqueConstraint, Index, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class FamilyDB(Base):
    """家庭数据库模型"""
    
    __tablename__ = "families"
    
    # 主键
    family_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 所有者
    owner_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 家庭设置
    privacy_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    member_permissions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    data_sharing_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    member_count: Mapped[int] = mapped_column(Integer, default=1)
    
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
    owner = relationship("UserProfileDB", foreign_keys=[owner_id])
    members = relationship("FamilyMemberDB", back_populates="family", cascade="all, delete-orphan")
    invitations = relationship("FamilyInvitationDB", back_populates="family", cascade="all, delete-orphan")
    activity_logs = relationship("FamilyActivityLogDB", back_populates="family", cascade="all, delete-orphan")
    
    # 约束和索引
    __table_args__ = (
        Index("idx_family_owner", "owner_id"),
        Index("idx_family_active", "is_active"),
        Index("idx_family_created", "created_at"),
        Index("idx_family_name", "name"),
    )


class FamilyMemberDB(Base):
    """家庭成员数据库模型"""
    
    __tablename__ = "family_members"
    
    # 主键
    member_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    family_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 成员信息
    role: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="member"
    )  # owner, admin, member, viewer
    
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 权限设置
    permissions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    data_access_level: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="basic"
    )  # full, limited, basic
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_active: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # 时间戳
    joined_at: Mapped[datetime] = mapped_column(
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
    family = relationship("FamilyDB", back_populates="members")
    user = relationship("UserProfileDB", foreign_keys=[user_id])
    
    # 约束和索引
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", name="uq_family_member"),
        Index("idx_family_member_family", "family_id"),
        Index("idx_family_member_user", "user_id"),
        Index("idx_family_member_role", "role"),
        Index("idx_family_member_active", "is_active"),
        Index("idx_family_member_joined", "joined_at"),
    )


class FamilyInvitationDB(Base):
    """家庭邀请数据库模型"""
    
    __tablename__ = "family_invitations"
    
    # 主键
    invitation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    family_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False
    )
    inviter_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    invitee_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=True
    )
    
    # 邀请信息
    invitee_email: Mapped[str] = mapped_column(String(255), nullable=False)
    invitation_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="pending"
    )  # pending, accepted, declined, expired, cancelled
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # 关系
    family = relationship("FamilyDB", back_populates="invitations")
    inviter = relationship("UserProfileDB", foreign_keys=[inviter_id])
    invitee = relationship("UserProfileDB", foreign_keys=[invitee_id])
    
    # 约束和索引
    __table_args__ = (
        Index("idx_invitation_family", "family_id"),
        Index("idx_invitation_inviter", "inviter_id"),
        Index("idx_invitation_invitee", "invitee_id"),
        Index("idx_invitation_email", "invitee_email"),
        Index("idx_invitation_code", "invitation_code"),
        Index("idx_invitation_status", "status"),
        Index("idx_invitation_expires", "expires_at"),
        Index("idx_invitation_created", "created_at"),
    )


class FamilyActivityLogDB(Base):
    """家庭活动日志数据库模型"""
    
    __tablename__ = "family_activity_logs"
    
    # 主键
    log_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    family_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 活动信息
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间戳
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系
    family = relationship("FamilyDB", back_populates="activity_logs")
    user = relationship("UserProfileDB", foreign_keys=[user_id])
    
    # 约束和索引
    __table_args__ = (
        Index("idx_activity_log_family", "family_id"),
        Index("idx_activity_log_user", "user_id"),
        Index("idx_activity_log_action", "action"),
        Index("idx_activity_log_timestamp", "timestamp"),
        Index("idx_activity_log_family_time", "family_id", "timestamp"),
    )


class FamilyPermissionDB(Base):
    """家庭权限数据库模型"""
    
    __tablename__ = "family_permissions"
    
    # 主键
    permission_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    family_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("families.family_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 权限信息
    permission_type: Mapped[str] = mapped_column(String(50), nullable=False)
    permission_value: Mapped[bool] = mapped_column(Boolean, default=False)
    granted_by: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 时间戳
    granted_at: Mapped[datetime] = mapped_column(
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
    user = relationship("UserProfileDB", foreign_keys=[user_id])
    granter = relationship("UserProfileDB", foreign_keys=[granted_by])
    
    # 约束和索引
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", "permission_type", name="uq_family_permission"),
        Index("idx_permission_family", "family_id"),
        Index("idx_permission_user", "user_id"),
        Index("idx_permission_type", "permission_type"),
        Index("idx_permission_granted", "granted_at"),
    )
