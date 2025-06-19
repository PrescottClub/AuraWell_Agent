"""
Family Repository - Database access layer for family-related operations

Provides database operations for families, members, and invitations.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.family_models import FamilyRole, InviteStatus
from ..core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class FamilyRepository:
    """Repository for family-related database operations"""

    def __init__(self, session: Session):
        self.session = session

    async def create_family(self, family_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new family in the database"""
        try:
            from ..database.family_models import FamilyDB

            # 创建家庭数据库记录（简化版本，只包含基本字段）
            family_db = FamilyDB(
                family_id=family_data["family_id"],
                name=family_data["name"],
                description=family_data.get("description"),
                owner_id=family_data["owner_id"],
                created_at=family_data["created_at"],
                updated_at=family_data["updated_at"],
                member_count=family_data.get("member_count", 1),
                is_active=family_data.get("is_active", True)
            )

            self.session.add(family_db)
            self.session.flush()  # 确保数据写入数据库

            logger.info(f"✅ 家庭创建成功: {family_data['name']} (ID: {family_data['family_id']})")
            return family_data

        except SQLAlchemyError as e:
            logger.error(f"Database error creating family: {e}")
            raise DatabaseError(
                f"Failed to create family: {str(e)}", operation="create_family"
            )

    async def get_family_by_id(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Get family by ID"""
        try:
            from ..database.family_models import FamilyDB

            # 查询家庭记录
            from sqlalchemy import select
            stmt = select(FamilyDB).where(
                FamilyDB.family_id == family_id,
                FamilyDB.is_active == True
            )
            result = await self.session.execute(stmt)
            family_db = result.scalar_one_or_none()

            if not family_db:
                logger.debug(f"Family not found: {family_id}")
                return None

            # 转换为字典格式（简化版本）
            family_data = {
                "family_id": family_db.family_id,
                "name": family_db.name,
                "description": family_db.description,
                "owner_id": family_db.owner_id,
                "created_at": family_db.created_at,
                "updated_at": family_db.updated_at,
                "member_count": family_db.member_count,
                "is_active": family_db.is_active
            }

            logger.debug(f"✅ 家庭查询成功: {family_db.name} (ID: {family_id})")
            return family_data

        except SQLAlchemyError as e:
            logger.error(f"Database error getting family: {e}")
            raise DatabaseError(
                f"Failed to get family: {str(e)}", operation="get_family"
            )

    async def get_user_families(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all families for a user"""
        try:
            from ..database.family_models import FamilyDB, FamilyMemberDB

            # 查询用户所属的所有家庭
            from sqlalchemy import select
            stmt = select(FamilyDB).join(
                FamilyMemberDB, FamilyDB.family_id == FamilyMemberDB.family_id
            ).where(
                FamilyMemberDB.user_id == user_id,
                FamilyMemberDB.is_active == True,
                FamilyDB.is_active == True
            ).order_by(FamilyDB.created_at.desc())

            result = await self.session.execute(stmt)

            families = []
            for family_db in result.scalars().all():
                family_data = {
                    "family_id": family_db.family_id,
                    "name": family_db.name,
                    "description": family_db.description,
                    "owner_id": family_db.owner_id,
                    "created_at": family_db.created_at,
                    "updated_at": family_db.updated_at,
                    "member_count": family_db.member_count,
                    "is_active": family_db.is_active
                }
                families.append(family_data)

            logger.debug(f"✅ 用户家庭查询成功: {len(families)} 个家庭 (用户: {user_id})")
            return families

        except SQLAlchemyError as e:
            logger.error(f"Database error getting user families: {e}")
            raise DatabaseError(
                f"Failed to get user families: {str(e)}", operation="get_user_families"
            )

    async def get_user_owned_families_count(self, user_id: str) -> int:
        """Get count of families owned by user"""
        try:
            # Mock implementation
            logger.debug(f"Getting owned families count for user: {user_id}")
            return 1
        except SQLAlchemyError as e:
            logger.error(f"Database error getting owned families count: {e}")
            raise DatabaseError(
                f"Failed to get owned families count: {str(e)}",
                operation="get_owned_families_count",
            )

    async def is_family_member(self, family_id: str, user_id: str) -> bool:
        """Check if user is a family member"""
        try:
            from ..database.family_models import FamilyMemberDB

            # 查询用户是否为家庭成员
            from sqlalchemy import select
            stmt = select(FamilyMemberDB).where(
                FamilyMemberDB.family_id == family_id,
                FamilyMemberDB.user_id == user_id,
                FamilyMemberDB.is_active == True
            )
            result = await self.session.execute(stmt)
            member_exists = result.scalar_one_or_none() is not None

            logger.debug(f"✅ 家庭成员检查: 用户 {user_id} {'是' if member_exists else '不是'} 家庭 {family_id} 的成员")
            return member_exists

        except SQLAlchemyError as e:
            logger.error(f"Database error checking family membership: {e}")
            raise DatabaseError(
                f"Failed to check family membership: {str(e)}",
                operation="check_membership",
            )

    async def add_family_member(
        self, family_id: str, user_id: str, role: FamilyRole
    ) -> None:
        """Add a member to a family"""
        try:
            from ..database.family_models import FamilyMemberDB
            import uuid

            # 创建家庭成员记录
            member_db = FamilyMemberDB(
                member_id=str(uuid.uuid4()),
                family_id=family_id,
                user_id=user_id,
                role=role.value,
                is_active=True,
                joined_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                permissions={},
                data_access_level="basic"
            )

            self.session.add(member_db)
            self.session.flush()

            logger.info(f"✅ 家庭成员添加成功: 用户 {user_id} 加入家庭 {family_id}，角色: {role.value}")

        except SQLAlchemyError as e:
            logger.error(f"Database error adding family member: {e}")
            raise DatabaseError(
                f"Failed to add family member: {str(e)}", operation="add_member"
            )

    async def get_family_members(self, family_id: str) -> List[Dict[str, Any]]:
        """Get all members of a family"""
        try:
            from ..database.family_models import FamilyMemberDB
            from sqlalchemy import select

            # 查询家庭成员（简化版本，暂时不JOIN用户表）
            stmt = select(FamilyMemberDB).where(
                FamilyMemberDB.family_id == family_id,
                FamilyMemberDB.is_active == True
            ).order_by(FamilyMemberDB.joined_at.asc())

            result = await self.session.execute(stmt)
            members = []

            for member_db in result.scalars().all():
                member_data = {
                    "user_id": member_db.user_id,
                    "username": f"user_{member_db.user_id[-4:]}",  # 临时用户名
                    "display_name": member_db.display_name or f"用户{member_db.user_id[-4:]}",
                    "email": f"user_{member_db.user_id[-4:]}@example.com",  # 临时邮箱
                    "role": FamilyRole(member_db.role),
                    "joined_at": member_db.joined_at,
                    "last_active": member_db.last_active,
                    "is_active": member_db.is_active
                }
                members.append(member_data)

            logger.debug(f"✅ 家庭成员查询成功: {len(members)} 个成员 (家庭: {family_id})")
            return members

        except SQLAlchemyError as e:
            logger.error(f"Database error getting family members: {e}")
            raise DatabaseError(
                f"Failed to get family members: {str(e)}", operation="get_members"
            )

    async def get_family_member(
        self, family_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific family member"""
        try:
            # Mock implementation
            logger.debug(f"Getting member {user_id} from family {family_id}")
            return {
                "user_id": user_id,
                "username": "testuser1",
                "display_name": "Test User 1",
                "email": "test1@example.com",
                "role": FamilyRole.OWNER,
                "joined_at": datetime.now(timezone.utc),
                "last_active": datetime.now(timezone.utc),
                "is_active": True,
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting family member: {e}")
            raise DatabaseError(
                f"Failed to get family member: {str(e)}", operation="get_member"
            )

    async def can_invite_members(self, family_id: str, user_id: str) -> bool:
        """Check if user can invite members"""
        try:
            # Mock implementation - check user role
            member = await self.get_family_member(family_id, user_id)
            if not member:
                return False
            role = member.get("role")
            return role in [FamilyRole.OWNER, FamilyRole.MANAGER]
        except SQLAlchemyError as e:
            logger.error(f"Database error checking invite permissions: {e}")
            raise DatabaseError(
                f"Failed to check invite permissions: {str(e)}",
                operation="check_invite_permissions",
            )

    async def create_invitation(self, invite_data: Dict[str, Any]) -> None:
        """Create an invitation"""
        try:
            # Mock implementation
            logger.info(f"Creating invitation for {invite_data['invitee_email']}")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating invitation: {e}")
            raise DatabaseError(
                f"Failed to create invitation: {str(e)}", operation="create_invitation"
            )

    async def get_invitation_by_code(
        self, invite_code: str
    ) -> Optional[Dict[str, Any]]:
        """Get invitation by code"""
        try:
            # Mock implementation
            logger.debug(f"Getting invitation by code: {invite_code}")
            return {
                "invite_id": "invite1",
                "family_id": "family1",
                "family_name": "Test Family",
                "inviter_id": "user1",
                "inviter_name": "Test User",
                "invitee_email": "test2@example.com",
                "role": FamilyRole.VIEWER,
                "status": InviteStatus.PENDING,
                "message": "Join our family!",
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc),
                "responded_at": None,
                "invite_code": invite_code,
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting invitation: {e}")
            raise DatabaseError(
                f"Failed to get invitation: {str(e)}", operation="get_invitation"
            )

    async def get_pending_invite(
        self, family_id: str, email: str
    ) -> Optional[Dict[str, Any]]:
        """Get pending invitation for family and email"""
        try:
            # Mock implementation
            logger.debug(f"Getting pending invite for {email} in family {family_id}")
            return None  # No pending invite
        except SQLAlchemyError as e:
            logger.error(f"Database error getting pending invite: {e}")
            raise DatabaseError(
                f"Failed to get pending invite: {str(e)}",
                operation="get_pending_invite",
            )

    async def update_invitation_status(
        self, invite_id: str, status: InviteStatus, responded_at: datetime
    ) -> None:
        """Update invitation status"""
        try:
            # Mock implementation
            logger.info(f"Updating invitation {invite_id} status to {status}")
        except SQLAlchemyError as e:
            logger.error(f"Database error updating invitation status: {e}")
            raise DatabaseError(
                f"Failed to update invitation status: {str(e)}",
                operation="update_invitation_status",
            )

    async def increment_family_member_count(self, family_id: str) -> None:
        """Increment family member count"""
        try:
            # Mock implementation
            logger.debug(f"Incrementing member count for family {family_id}")
        except SQLAlchemyError as e:
            logger.error(f"Database error incrementing member count: {e}")
            raise DatabaseError(
                f"Failed to increment member count: {str(e)}",
                operation="increment_member_count",
            )

    async def log_family_activity(
        self, family_id: str, user_id: str, action: str, details: Dict[str, Any]
    ) -> None:
        """Log family activity"""
        try:
            # Mock implementation
            logger.info(
                f"Logging family activity: {action} by {user_id} in family {family_id}"
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error logging family activity: {e}")
            raise DatabaseError(
                f"Failed to log family activity: {str(e)}", operation="log_activity"
            )
