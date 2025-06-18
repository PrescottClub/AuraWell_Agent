"""
真正的家庭仓库实现 - 替换Mock实现

提供基于SQLAlchemy的真实数据库操作
"""

import logging
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import selectinload

from ..models.family_models import FamilyRole, InviteStatus
from ..core.exceptions import DatabaseError, ValidationError, ConflictError, NotFoundError
from ..database.family_models import (
    FamilyDB, 
    FamilyMemberDB, 
    FamilyInvitationDB, 
    FamilyActivityLogDB,
    FamilyPermissionDB
)
from ..database.models import UserProfileDB

logger = logging.getLogger(__name__)


class RealFamilyRepository:
    """真正的家庭仓库实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_family(self, family_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新家庭"""
        try:
            # 验证必需字段
            required_fields = ['family_id', 'name', 'owner_id']
            for field in required_fields:
                if field not in family_data:
                    raise ValidationError(f"Missing required field: {field}")

            # 检查用户是否存在
            user_exists = await self.session.execute(
                select(UserProfileDB).where(UserProfileDB.user_id == family_data['owner_id'])
            )
            if not user_exists.scalar_one_or_none():
                raise NotFoundError(f"User {family_data['owner_id']} not found")

            # 创建家庭记录
            family = FamilyDB(
                family_id=family_data['family_id'],
                name=family_data['name'],
                description=family_data.get('description'),
                owner_id=family_data['owner_id'],
                member_count=1,
                is_active=True,
                privacy_settings=family_data.get('privacy_settings', {}),
                member_permissions=family_data.get('member_permissions', {}),
                data_sharing_settings=family_data.get('data_sharing_settings', {})
            )

            self.session.add(family)
            await self.session.flush()  # 确保family_id可用

            logger.info(f"Family created successfully: {family_data['family_id']}")
            return family.to_dict()

        except IntegrityError as e:
            logger.error(f"Integrity error creating family: {e}")
            raise ConflictError(f"Family with ID {family_data['family_id']} already exists")
        except (ValidationError, NotFoundError, ConflictError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error creating family: {e}")
            raise DatabaseError(f"Failed to create family: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating family: {e}")
            raise DatabaseError(f"Unexpected error creating family: {str(e)}")

    async def get_family_by_id(self, family_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取家庭信息"""
        try:
            result = await self.session.execute(
                select(FamilyDB)
                .options(selectinload(FamilyDB.owner))
                .where(and_(FamilyDB.family_id == family_id, FamilyDB.is_active == True))
            )
            family = result.scalar_one_or_none()
            
            if family:
                return family.to_dict()
            return None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting family: {e}")
            raise DatabaseError(f"Failed to get family: {str(e)}")

    async def get_user_owned_families_count(self, user_id: str) -> int:
        """获取用户拥有的家庭数量"""
        try:
            result = await self.session.execute(
                select(func.count(FamilyDB.family_id))
                .where(and_(
                    FamilyDB.owner_id == user_id,
                    FamilyDB.is_active == True
                ))
            )
            count = result.scalar() or 0
            logger.debug(f"User {user_id} owns {count} families")
            return count

        except SQLAlchemyError as e:
            logger.error(f"Database error getting families count: {e}")
            raise DatabaseError(f"Failed to get families count: {str(e)}")

    async def add_family_member(self, family_id: str, user_id: str, role: FamilyRole) -> None:
        """添加家庭成员"""
        try:
            # 检查是否已经是成员
            existing = await self.session.execute(
                select(FamilyMemberDB).where(and_(
                    FamilyMemberDB.family_id == family_id,
                    FamilyMemberDB.user_id == user_id
                ))
            )
            if existing.scalar_one_or_none():
                raise ConflictError(f"User {user_id} is already a member of family {family_id}")

            # 创建成员记录
            member = FamilyMemberDB(
                member_id=str(uuid.uuid4()),
                family_id=family_id,
                user_id=user_id,
                role=role,
                is_active=True,
                joined_at=datetime.now(timezone.utc),
                notification_settings={},
                data_access_settings={}
            )

            self.session.add(member)

            # 更新家庭成员数量
            await self.session.execute(
                update(FamilyDB)
                .where(FamilyDB.family_id == family_id)
                .values(member_count=FamilyDB.member_count + 1)
            )

            logger.info(f"Added user {user_id} to family {family_id} with role {role}")

        except ConflictError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error adding family member: {e}")
            raise DatabaseError(f"Failed to add family member: {str(e)}")

    async def is_family_member(self, family_id: str, user_id: str) -> bool:
        """检查用户是否是家庭成员"""
        try:
            result = await self.session.execute(
                select(FamilyMemberDB).where(and_(
                    FamilyMemberDB.family_id == family_id,
                    FamilyMemberDB.user_id == user_id,
                    FamilyMemberDB.is_active == True
                ))
            )
            return result.scalar_one_or_none() is not None

        except SQLAlchemyError as e:
            logger.error(f"Database error checking family membership: {e}")
            raise DatabaseError(f"Failed to check family membership: {str(e)}")

    async def get_family_members(self, family_id: str) -> List[Dict[str, Any]]:
        """获取家庭所有成员"""
        try:
            result = await self.session.execute(
                select(FamilyMemberDB, UserProfileDB)
                .join(UserProfileDB, FamilyMemberDB.user_id == UserProfileDB.user_id)
                .where(and_(
                    FamilyMemberDB.family_id == family_id,
                    FamilyMemberDB.is_active == True
                ))
                .order_by(FamilyMemberDB.joined_at)
            )

            members = []
            for member_db, user_db in result.all():
                member_dict = member_db.to_dict()
                member_dict.update({
                    'username': user_db.username,
                    'display_name': user_db.display_name,
                    'email': user_db.email
                })
                members.append(member_dict)

            return members

        except SQLAlchemyError as e:
            logger.error(f"Database error getting family members: {e}")
            raise DatabaseError(f"Failed to get family members: {str(e)}")

    async def get_family_member(self, family_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """获取特定家庭成员信息"""
        try:
            result = await self.session.execute(
                select(FamilyMemberDB, UserProfileDB)
                .join(UserProfileDB, FamilyMemberDB.user_id == UserProfileDB.user_id)
                .where(and_(
                    FamilyMemberDB.family_id == family_id,
                    FamilyMemberDB.user_id == user_id,
                    FamilyMemberDB.is_active == True
                ))
            )

            row = result.first()
            if row:
                member_db, user_db = row
                member_dict = member_db.to_dict()
                member_dict.update({
                    'username': user_db.username,
                    'display_name': user_db.display_name,
                    'email': user_db.email
                })
                return member_dict

            return None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting family member: {e}")
            raise DatabaseError(f"Failed to get family member: {str(e)}")

    async def log_family_activity(self, family_id: str, user_id: str, action: str, details: Dict[str, Any]) -> None:
        """记录家庭活动日志"""
        try:
            # 获取用户名
            user_result = await self.session.execute(
                select(UserProfileDB.username).where(UserProfileDB.user_id == user_id)
            )
            username = user_result.scalar() or "Unknown User"

            # 创建活动日志
            log = FamilyActivityLogDB(
                log_id=str(uuid.uuid4()),
                family_id=family_id,
                user_id=user_id,
                username=username,
                action=action,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )

            self.session.add(log)
            logger.info(f"Logged family activity: {action} by {user_id} in family {family_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error logging family activity: {e}")
            raise DatabaseError(f"Failed to log family activity: {str(e)}")

    async def create_invitation(self, invite_data: Dict[str, Any]) -> None:
        """创建邀请"""
        try:
            invitation = FamilyInvitationDB(
                invite_id=invite_data['invite_id'],
                family_id=invite_data['family_id'],
                inviter_id=invite_data['inviter_id'],
                family_name=invite_data['family_name'],
                inviter_name=invite_data['inviter_name'],
                invitee_email=invite_data['invitee_email'],
                role=invite_data['role'],
                message=invite_data.get('message'),
                invite_code=invite_data['invite_code'],
                status=InviteStatus.PENDING,
                expires_at=invite_data['expires_at']
            )

            self.session.add(invitation)
            logger.info(f"Created invitation for {invite_data['invitee_email']}")

        except SQLAlchemyError as e:
            logger.error(f"Database error creating invitation: {e}")
            raise DatabaseError(f"Failed to create invitation: {str(e)}")

    async def get_invitation_by_code(self, invite_code: str) -> Optional[Dict[str, Any]]:
        """根据邀请码获取邀请"""
        try:
            result = await self.session.execute(
                select(FamilyInvitationDB).where(
                    FamilyInvitationDB.invite_code == invite_code
                )
            )
            invitation = result.scalar_one_or_none()
            
            if invitation:
                return invitation.to_dict()
            return None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting invitation: {e}")
            raise DatabaseError(f"Failed to get invitation: {str(e)}")

    async def update_invitation_status(self, invite_id: str, status: InviteStatus, responded_at: datetime) -> None:
        """更新邀请状态"""
        try:
            await self.session.execute(
                update(FamilyInvitationDB)
                .where(FamilyInvitationDB.invite_id == invite_id)
                .values(status=status, responded_at=responded_at)
            )
            logger.info(f"Updated invitation {invite_id} status to {status}")

        except SQLAlchemyError as e:
            logger.error(f"Database error updating invitation status: {e}")
            raise DatabaseError(f"Failed to update invitation status: {str(e)}")

    async def get_pending_invite(self, family_id: str, email: str) -> Optional[Dict[str, Any]]:
        """获取待处理的邀请"""
        try:
            result = await self.session.execute(
                select(FamilyInvitationDB).where(and_(
                    FamilyInvitationDB.family_id == family_id,
                    FamilyInvitationDB.invitee_email == email,
                    FamilyInvitationDB.status == InviteStatus.PENDING,
                    FamilyInvitationDB.expires_at > datetime.now(timezone.utc)
                ))
            )
            invitation = result.scalar_one_or_none()
            
            if invitation:
                return invitation.to_dict()
            return None

        except SQLAlchemyError as e:
            logger.error(f"Database error getting pending invite: {e}")
            raise DatabaseError(f"Failed to get pending invite: {str(e)}")

    async def can_invite_members(self, family_id: str, user_id: str) -> bool:
        """检查用户是否可以邀请成员"""
        try:
            member = await self.get_family_member(family_id, user_id)
            if not member:
                return False
            
            role = member.get('role')
            return role in [FamilyRole.OWNER, FamilyRole.MANAGER]

        except Exception as e:
            logger.error(f"Error checking invite permissions: {e}")
            return False

    async def increment_family_member_count(self, family_id: str) -> None:
        """增加家庭成员数量"""
        try:
            await self.session.execute(
                update(FamilyDB)
                .where(FamilyDB.family_id == family_id)
                .values(member_count=FamilyDB.member_count + 1)
            )
            logger.debug(f"Incremented member count for family {family_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error incrementing member count: {e}")
            raise DatabaseError(f"Failed to increment member count: {str(e)}")
