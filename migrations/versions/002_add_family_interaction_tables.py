"""Add family interaction tables

Revision ID: 002_add_family_interaction_tables
Revises: 001_add_family_tables
Create Date: 2025-06-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '002_add_family_interaction_tables'
down_revision = '001_add_family_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Add family interaction tables"""
    
    # 创建家庭成员点赞表
    op.create_table('family_member_likes',
        sa.Column('like_id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('liker_id', sa.String(36), nullable=False),
        sa.Column('liked_member_id', sa.String(36), nullable=False),
        sa.Column('like_type', sa.String(50), nullable=False, server_default='general'),
        sa.Column('like_reason', sa.Text(), nullable=True),
        sa.Column('related_activity_id', sa.String(36), nullable=True),
        sa.Column('related_achievement_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.family_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['liker_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['liked_member_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('like_id'),
        sa.UniqueConstraint('liker_id', 'liked_member_id', 'family_id', 'like_type', name='uq_family_member_like')
    )
    
    # 创建索引
    op.create_index('idx_family_like_family', 'family_member_likes', ['family_id'])
    op.create_index('idx_family_like_liker', 'family_member_likes', ['liker_id'])
    op.create_index('idx_family_like_liked', 'family_member_likes', ['liked_member_id'])
    op.create_index('idx_family_like_type', 'family_member_likes', ['like_type'])
    op.create_index('idx_family_like_active', 'family_member_likes', ['is_active'])
    op.create_index('idx_family_like_created', 'family_member_likes', ['created_at'])
    
    # 创建家庭健康告警表
    op.create_table('family_health_alerts',
        sa.Column('alert_id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('member_id', sa.String(36), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('trigger_value', sa.Float(), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('metric_unit', sa.String(20), nullable=True),
        sa.Column('alert_metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('acknowledged_by', sa.String(36), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('notification_channels', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.family_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['user_profiles.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('alert_id')
    )
    
    # 创建索引
    op.create_index('idx_health_alert_family', 'family_health_alerts', ['family_id'])
    op.create_index('idx_health_alert_member', 'family_health_alerts', ['member_id'])
    op.create_index('idx_health_alert_type', 'family_health_alerts', ['alert_type'])
    op.create_index('idx_health_alert_severity', 'family_health_alerts', ['severity'])
    op.create_index('idx_health_alert_status', 'family_health_alerts', ['status'])
    op.create_index('idx_health_alert_created', 'family_health_alerts', ['created_at'])
    op.create_index('idx_health_alert_family_status', 'family_health_alerts', ['family_id', 'status'])
    
    # 创建家庭互动统计表
    op.create_table('family_interaction_stats',
        sa.Column('stats_id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('member_id', sa.String(36), nullable=False),
        sa.Column('stats_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('stats_period', sa.String(20), nullable=False, server_default='daily'),
        sa.Column('likes_given', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('likes_received', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('alerts_triggered', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('alerts_acknowledged', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('family_interactions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('health_data_shares', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('interaction_details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.family_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['user_profiles.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('stats_id'),
        sa.UniqueConstraint('family_id', 'member_id', 'stats_date', 'stats_period', name='uq_family_interaction_stats')
    )
    
    # 创建索引
    op.create_index('idx_interaction_stats_family', 'family_interaction_stats', ['family_id'])
    op.create_index('idx_interaction_stats_member', 'family_interaction_stats', ['member_id'])
    op.create_index('idx_interaction_stats_date', 'family_interaction_stats', ['stats_date'])
    op.create_index('idx_interaction_stats_period', 'family_interaction_stats', ['stats_period'])


def downgrade():
    """Remove family interaction tables"""
    
    # 删除索引
    op.drop_index('idx_interaction_stats_period', table_name='family_interaction_stats')
    op.drop_index('idx_interaction_stats_date', table_name='family_interaction_stats')
    op.drop_index('idx_interaction_stats_member', table_name='family_interaction_stats')
    op.drop_index('idx_interaction_stats_family', table_name='family_interaction_stats')
    
    op.drop_index('idx_health_alert_family_status', table_name='family_health_alerts')
    op.drop_index('idx_health_alert_created', table_name='family_health_alerts')
    op.drop_index('idx_health_alert_status', table_name='family_health_alerts')
    op.drop_index('idx_health_alert_severity', table_name='family_health_alerts')
    op.drop_index('idx_health_alert_type', table_name='family_health_alerts')
    op.drop_index('idx_health_alert_member', table_name='family_health_alerts')
    op.drop_index('idx_health_alert_family', table_name='family_health_alerts')
    
    op.drop_index('idx_family_like_created', table_name='family_member_likes')
    op.drop_index('idx_family_like_active', table_name='family_member_likes')
    op.drop_index('idx_family_like_type', table_name='family_member_likes')
    op.drop_index('idx_family_like_liked', table_name='family_member_likes')
    op.drop_index('idx_family_like_liker', table_name='family_member_likes')
    op.drop_index('idx_family_like_family', table_name='family_member_likes')
    
    # 删除表
    op.drop_table('family_interaction_stats')
    op.drop_table('family_health_alerts')
    op.drop_table('family_member_likes')
