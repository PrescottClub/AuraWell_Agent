"""
家庭仓库单元测试

测试真正的家庭仓库实现
"""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from aurawell.repositories.family_repository_real import RealFamilyRepository
from aurawell.models.family_models import FamilyRole, InviteStatus
from aurawell.core.exceptions import DatabaseError, ValidationError, ConflictError, NotFoundError
from aurawell.database.family_models import FamilyDB, FamilyMemberDB, UserProfileDB


@pytest.fixture
def mock_session():
    """模拟数据库会话"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def family_repository(mock_session):
    """家庭仓库实例"""
    return RealFamilyRepository(mock_session)


@pytest.fixture
def sample_family_data():
    """示例家庭数据"""
    return {
        "family_id": str(uuid.uuid4()),
        "name": "测试家庭",
        "description": "这是一个测试家庭",
        "owner_id": str(uuid.uuid4()),
        "privacy_settings": {"public": False},
        "member_permissions": {"invite": True},
        "data_sharing_settings": {"health_data": True}
    }


class TestRealFamilyRepository:
    """真正的家庭仓库测试"""

    @pytest.mark.asyncio
    async def test_create_family_success(self, family_repository, mock_session, sample_family_data):
        """测试成功创建家庭"""
        # 模拟用户存在检查
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = MagicMock()  # 用户存在
        mock_session.execute.return_value = user_result
        
        # 执行创建
        result = await family_repository.create_family(sample_family_data)
        
        # 验证结果
        assert result is not None
        assert "family_id" in result
        
        # 验证数据库操作
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_family_missing_required_field(self, family_repository, sample_family_data):
        """测试创建家庭时缺少必需字段"""
        # 删除必需字段
        del sample_family_data["name"]
        
        # 执行并验证异常
        with pytest.raises(ValidationError, match="Missing required field: name"):
            await family_repository.create_family(sample_family_data)

    @pytest.mark.asyncio
    async def test_create_family_user_not_found(self, family_repository, mock_session, sample_family_data):
        """测试创建家庭时用户不存在"""
        # 模拟用户不存在
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = user_result
        
        # 执行并验证异常
        with pytest.raises(NotFoundError):
            await family_repository.create_family(sample_family_data)

    @pytest.mark.asyncio
    async def test_create_family_duplicate_id(self, family_repository, mock_session, sample_family_data):
        """测试创建重复ID的家庭"""
        # 模拟用户存在
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute.return_value = user_result
        
        # 模拟完整性错误
        mock_session.add.side_effect = IntegrityError("", "", "")
        
        # 执行并验证异常
        with pytest.raises(ConflictError):
            await family_repository.create_family(sample_family_data)

    @pytest.mark.asyncio
    async def test_get_family_by_id_exists(self, family_repository, mock_session):
        """测试获取存在的家庭"""
        family_id = str(uuid.uuid4())
        
        # 模拟查询结果
        mock_family = MagicMock()
        mock_family.to_dict.return_value = {"family_id": family_id, "name": "测试家庭"}
        
        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_family
        mock_session.execute.return_value = result
        
        # 执行查询
        family = await family_repository.get_family_by_id(family_id)
        
        # 验证结果
        assert family is not None
        assert family["family_id"] == family_id
        assert family["name"] == "测试家庭"

    @pytest.mark.asyncio
    async def test_get_family_by_id_not_exists(self, family_repository, mock_session):
        """测试获取不存在的家庭"""
        family_id = str(uuid.uuid4())
        
        # 模拟查询结果为空
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result
        
        # 执行查询
        family = await family_repository.get_family_by_id(family_id)
        
        # 验证结果
        assert family is None

    @pytest.mark.asyncio
    async def test_get_user_owned_families_count(self, family_repository, mock_session):
        """测试获取用户拥有的家庭数量"""
        user_id = str(uuid.uuid4())
        expected_count = 2
        
        # 模拟查询结果
        result = MagicMock()
        result.scalar.return_value = expected_count
        mock_session.execute.return_value = result
        
        # 执行查询
        count = await family_repository.get_user_owned_families_count(user_id)
        
        # 验证结果
        assert count == expected_count

    @pytest.mark.asyncio
    async def test_add_family_member_success(self, family_repository, mock_session):
        """测试成功添加家庭成员"""
        family_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        role = FamilyRole.MEMBER
        
        # 模拟成员不存在检查
        existing_result = MagicMock()
        existing_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = existing_result
        
        # 执行添加
        await family_repository.add_family_member(family_id, user_id, role)
        
        # 验证数据库操作
        assert mock_session.add.called
        assert mock_session.execute.call_count >= 2  # 检查存在 + 更新计数

    @pytest.mark.asyncio
    async def test_add_family_member_already_exists(self, family_repository, mock_session):
        """测试添加已存在的家庭成员"""
        family_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        role = FamilyRole.MEMBER
        
        # 模拟成员已存在
        existing_result = MagicMock()
        existing_result.scalar_one_or_none.return_value = MagicMock()  # 成员存在
        mock_session.execute.return_value = existing_result
        
        # 执行并验证异常
        with pytest.raises(ConflictError):
            await family_repository.add_family_member(family_id, user_id, role)

    @pytest.mark.asyncio
    async def test_is_family_member_true(self, family_repository, mock_session):
        """测试用户是家庭成员"""
        family_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 模拟成员存在
        result = MagicMock()
        result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute.return_value = result
        
        # 执行检查
        is_member = await family_repository.is_family_member(family_id, user_id)
        
        # 验证结果
        assert is_member is True

    @pytest.mark.asyncio
    async def test_is_family_member_false(self, family_repository, mock_session):
        """测试用户不是家庭成员"""
        family_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 模拟成员不存在
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result
        
        # 执行检查
        is_member = await family_repository.is_family_member(family_id, user_id)
        
        # 验证结果
        assert is_member is False

    @pytest.mark.asyncio
    async def test_get_family_members(self, family_repository, mock_session):
        """测试获取家庭成员列表"""
        family_id = str(uuid.uuid4())
        
        # 模拟查询结果
        mock_member = MagicMock()
        mock_member.to_dict.return_value = {
            "member_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "role": FamilyRole.MEMBER
        }
        
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_user.display_name = "Test User"
        mock_user.email = "test@example.com"
        
        result = MagicMock()
        result.all.return_value = [(mock_member, mock_user)]
        mock_session.execute.return_value = result
        
        # 执行查询
        members = await family_repository.get_family_members(family_id)
        
        # 验证结果
        assert len(members) == 1
        assert members[0]["username"] == "testuser"
        assert members[0]["display_name"] == "Test User"
        assert members[0]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_log_family_activity(self, family_repository, mock_session):
        """测试记录家庭活动"""
        family_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        action = "member_added"
        details = {"new_member": "test_user"}
        
        # 模拟用户名查询
        user_result = MagicMock()
        user_result.scalar.return_value = "testuser"
        mock_session.execute.return_value = user_result
        
        # 执行记录
        await family_repository.log_family_activity(family_id, user_id, action, details)
        
        # 验证数据库操作
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_invitation(self, family_repository, mock_session):
        """测试创建邀请"""
        invite_data = {
            "invite_id": str(uuid.uuid4()),
            "family_id": str(uuid.uuid4()),
            "inviter_id": str(uuid.uuid4()),
            "family_name": "测试家庭",
            "inviter_name": "邀请者",
            "invitee_email": "invitee@example.com",
            "role": FamilyRole.MEMBER,
            "message": "欢迎加入我们的家庭",
            "invite_code": "ABC123",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
        }
        
        # 执行创建
        await family_repository.create_invitation(invite_data)
        
        # 验证数据库操作
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_invitation_by_code_exists(self, family_repository, mock_session):
        """测试根据邀请码获取邀请"""
        invite_code = "ABC123"
        
        # 模拟查询结果
        mock_invitation = MagicMock()
        mock_invitation.to_dict.return_value = {
            "invite_id": str(uuid.uuid4()),
            "invite_code": invite_code,
            "status": InviteStatus.PENDING
        }
        
        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_invitation
        mock_session.execute.return_value = result
        
        # 执行查询
        invitation = await family_repository.get_invitation_by_code(invite_code)
        
        # 验证结果
        assert invitation is not None
        assert invitation["invite_code"] == invite_code
        assert invitation["status"] == InviteStatus.PENDING

    @pytest.mark.asyncio
    async def test_update_invitation_status(self, family_repository, mock_session):
        """测试更新邀请状态"""
        invite_id = str(uuid.uuid4())
        status = InviteStatus.ACCEPTED
        responded_at = datetime.now(timezone.utc)
        
        # 执行更新
        await family_repository.update_invitation_status(invite_id, status, responded_at)
        
        # 验证数据库操作
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_can_invite_members_owner(self, family_repository, mock_session):
        """测试所有者可以邀请成员"""
        family_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 模拟成员查询 - 所有者
        mock_member = MagicMock()
        mock_member.to_dict.return_value = {"role": FamilyRole.OWNER}
        
        mock_user = MagicMock()
        result = MagicMock()
        result.first.return_value = (mock_member, mock_user)
        mock_session.execute.return_value = result
        
        # 执行检查
        can_invite = await family_repository.can_invite_members(family_id, user_id)
        
        # 验证结果
        assert can_invite is True

    @pytest.mark.asyncio
    async def test_can_invite_members_viewer(self, family_repository, mock_session):
        """测试查看者不能邀请成员"""
        family_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 模拟成员查询 - 查看者
        mock_member = MagicMock()
        mock_member.to_dict.return_value = {"role": FamilyRole.VIEWER}
        
        mock_user = MagicMock()
        result = MagicMock()
        result.first.return_value = (mock_member, mock_user)
        mock_session.execute.return_value = result
        
        # 执行检查
        can_invite = await family_repository.can_invite_members(family_id, user_id)
        
        # 验证结果
        assert can_invite is False


# 集成测试类
class TestFamilyRepositoryIntegration:
    """家庭仓库集成测试"""

    @pytest.mark.asyncio
    async def test_full_family_lifecycle(self, family_repository, mock_session, sample_family_data):
        """测试完整的家庭生命周期"""
        # 1. 创建家庭
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute.return_value = user_result

        family = await family_repository.create_family(sample_family_data)
        assert family is not None

        # 2. 添加成员
        new_user_id = str(uuid.uuid4())
        existing_result = MagicMock()
        existing_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = existing_result

        await family_repository.add_family_member(
            sample_family_data["family_id"],
            new_user_id,
            FamilyRole.MEMBER
        )

        # 3. 记录活动
        await family_repository.log_family_activity(
            sample_family_data["family_id"],
            new_user_id,
            "member_joined",
            {"member_role": "MEMBER"}
        )

        # 验证所有操作都被调用
        assert mock_session.add.call_count >= 3  # 家庭 + 成员 + 活动日志
