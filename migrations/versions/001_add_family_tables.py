"""添加家庭管理相关表

Revision ID: 001
Revises: 
Create Date: 2025-01-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级数据库结构 - 添加家庭管理表"""
    
    # 创建家庭表
    op.create_table('families',
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('invitation_code', sa.String(20), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=True, default=1),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('privacy_settings', sa.JSON(), nullable=True),
        sa.Column('member_permissions', sa.JSON(), nullable=True),
        sa.Column('data_sharing_settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['owner_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('family_id'),
        sa.UniqueConstraint('invitation_code')
    )
    
    # 创建索引
    op.create_index('idx_family_owner', 'families', ['owner_id'])
    op.create_index('idx_family_active', 'families', ['is_active'])
    op.create_index('idx_family_invitation_code', 'families', ['invitation_code'])

    # 创建家庭成员表
    op.create_table('family_members',
        sa.Column('member_id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role', sa.Enum('OWNER', 'MANAGER', 'MEMBER', 'VIEWER', name='familyrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notification_settings', sa.JSON(), nullable=True),
        sa.Column('data_access_settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['family_id'], ['families.family_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('member_id'),
        sa.UniqueConstraint('family_id', 'user_id', name='uq_family_user')
    )
    
    # 创建索引
    op.create_index('idx_family_member_family', 'family_members', ['family_id'])
    op.create_index('idx_family_member_user', 'family_members', ['user_id'])
    op.create_index('idx_family_member_role', 'family_members', ['role'])
    op.create_index('idx_family_member_active', 'family_members', ['is_active'])

    # 创建家庭邀请表
    op.create_table('family_invitations',
        sa.Column('invite_id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('inviter_id', sa.String(36), nullable=False),
        sa.Column('family_name', sa.String(100), nullable=False),
        sa.Column('inviter_name', sa.String(100), nullable=False),
        sa.Column('invitee_email', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('OWNER', 'MANAGER', 'MEMBER', 'VIEWER', name='familyrole'), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('invite_code', sa.String(20), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED', name='invitestatus'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['family_id'], ['families.family_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inviter_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('invite_id'),
        sa.UniqueConstraint('invite_code')
    )
    
    # 创建索引
    op.create_index('idx_invitation_family', 'family_invitations', ['family_id'])
    op.create_index('idx_invitation_inviter', 'family_invitations', ['inviter_id'])
    op.create_index('idx_invitation_email', 'family_invitations', ['invitee_email'])
    op.create_index('idx_invitation_code', 'family_invitations', ['invite_code'])
    op.create_index('idx_invitation_status', 'family_invitations', ['status'])
    op.create_index('idx_invitation_expires', 'family_invitations', ['expires_at'])

    # 创建家庭活动日志表
    op.create_table('family_activity_logs',
        sa.Column('log_id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['family_id'], ['families.family_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('log_id')
    )
    
    # 创建索引
    op.create_index('idx_activity_log_family', 'family_activity_logs', ['family_id'])
    op.create_index('idx_activity_log_user', 'family_activity_logs', ['user_id'])
    op.create_index('idx_activity_log_action', 'family_activity_logs', ['action'])
    op.create_index('idx_activity_log_timestamp', 'family_activity_logs', ['timestamp'])

    # 创建家庭权限表
    op.create_table('family_permissions',
        sa.Column('permission_id', sa.String(36), nullable=False),
        sa.Column('grantor_id', sa.String(36), nullable=False),
        sa.Column('grantee_id', sa.String(36), nullable=False),
        sa.Column('target_user_id', sa.String(36), nullable=False),
        sa.Column('permission_type', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['grantor_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['grantee_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_user_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('permission_id')
    )
    
    # 创建索引
    op.create_index('idx_permission_grantor', 'family_permissions', ['grantor_id'])
    op.create_index('idx_permission_grantee', 'family_permissions', ['grantee_id'])
    op.create_index('idx_permission_target', 'family_permissions', ['target_user_id'])
    op.create_index('idx_permission_type', 'family_permissions', ['permission_type', 'resource_type'])
    op.create_index('idx_permission_expires', 'family_permissions', ['expires_at'])


def downgrade() -> None:
    """降级数据库结构 - 删除家庭管理表"""
    
    # 删除表（按依赖关系逆序）
    op.drop_table('family_permissions')
    op.drop_table('family_activity_logs')
    op.drop_table('family_invitations')
    op.drop_table('family_members')
    op.drop_table('families')
    
    # 删除枚举类型（如果数据库支持）
    try:
        op.execute("DROP TYPE IF EXISTS familyrole")
        op.execute("DROP TYPE IF EXISTS invitestatus")
    except:
        pass  # SQLite 不支持 DROP TYPE
