"""
家庭管理数据库模型

定义家庭、成员、邀请等相关的SQLAlchemy数据库模型
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
from ..models.family_models import FamilyRole, InviteStatus


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
    
    # 邀请码
    invitation_code: Mapped[Optional[str]] = mapped_column(
        String(20), 
        unique=True, 
        nullable=True
    )
    
    # 统计信息
    member_count: Mapped[int] = mapped_column(Integer, default=1)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 设置 (JSON格式存储)
    privacy_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    member_permissions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    data_sharing_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 关系
    owner = relationship("UserProfileDB", foreign_keys=[owner_id])
    members = relationship("FamilyMemberDB", back_populates="family", cascade="all, delete-orphan")
    invitations = relationship("FamilyInvitationDB", back_populates="family", cascade="all, delete-orphan")
    activity_logs = relationship("FamilyActivityLogDB", back_populates="family", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index("idx_family_owner", "owner_id"),
        Index("idx_family_active", "is_active"),
        Index("idx_family_invitation_code", "invitation_code"),
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
    
    # 角色和权限
    role: Mapped[FamilyRole] = mapped_column(
        SQLEnum(FamilyRole), 
        nullable=False,
        default=FamilyRole.VIEWER
    )
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 加入时间
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 最后活跃时间
    last_active: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # 个人设置
    notification_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    data_access_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 关系
    family = relationship("FamilyDB", back_populates="members")
    user = relationship("UserProfileDB", foreign_keys=[user_id])
    
    # 约束和索引
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", name="uq_family_user"),
        Index("idx_family_member_family", "family_id"),
        Index("idx_family_member_user", "user_id"),
        Index("idx_family_member_role", "role"),
        Index("idx_family_member_active", "is_active"),
    )


class FamilyInvitationDB(Base):
    """家庭邀请数据库模型"""
    
    __tablename__ = "family_invitations"
    
    # 主键
    invite_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
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
    
    # 邀请信息
    family_name: Mapped[str] = mapped_column(String(100), nullable=False)
    inviter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    invitee_email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 邀请设置
    role: Mapped[FamilyRole] = mapped_column(
        SQLEnum(FamilyRole), 
        nullable=False,
        default=FamilyRole.VIEWER
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    
    # 状态
    status: Mapped[InviteStatus] = mapped_column(
        SQLEnum(InviteStatus), 
        nullable=False,
        default=InviteStatus.PENDING
    )
    
    # 时间戳
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 关系
    family = relationship("FamilyDB", back_populates="invitations")
    inviter = relationship("UserProfileDB", foreign_keys=[inviter_id])
    
    # 索引
    __table_args__ = (
        Index("idx_invitation_family", "family_id"),
        Index("idx_invitation_inviter", "inviter_id"),
        Index("idx_invitation_email", "invitee_email"),
        Index("idx_invitation_code", "invite_code"),
        Index("idx_invitation_status", "status"),
        Index("idx_invitation_expires", "expires_at"),
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
    
    # 用户信息快照
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 时间戳
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系
    family = relationship("FamilyDB", back_populates="activity_logs")
    user = relationship("UserProfileDB", foreign_keys=[user_id])
    
    # 索引
    __table_args__ = (
        Index("idx_activity_log_family", "family_id"),
        Index("idx_activity_log_user", "user_id"),
        Index("idx_activity_log_action", "action"),
        Index("idx_activity_log_timestamp", "timestamp"),
    )


class FamilyPermissionDB(Base):
    """家庭权限控制数据库模型"""
    
    __tablename__ = "family_permissions"
    
    # 主键
    permission_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # 外键
    grantor_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    grantee_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    target_user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 权限信息
    permission_type: Mapped[str] = mapped_column(String(50), nullable=False)  # read, write, admin
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)    # health_data, goals, reports, alerts
    
    # 过期时间
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 关系
    grantor = relationship("UserProfileDB", foreign_keys=[grantor_id])
    grantee = relationship("UserProfileDB", foreign_keys=[grantee_id])
    target_user = relationship("UserProfileDB", foreign_keys=[target_user_id])
    
    # 索引
    __table_args__ = (
        Index("idx_permission_grantor", "grantor_id"),
        Index("idx_permission_grantee", "grantee_id"),
        Index("idx_permission_target", "target_user_id"),
        Index("idx_permission_type", "permission_type", "resource_type"),
        Index("idx_permission_expires", "expires_at"),
    )
