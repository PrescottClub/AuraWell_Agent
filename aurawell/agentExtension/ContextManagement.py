from datetime import datetime, timezone
from typing import Dict
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

# 从提供的数据库工具中导入必要组件
from aurawell.database.base import Base
from aurawell.database.connection import get_database_manager
from aurawell.database.models import UserProfileDB
from IntensivePhrase import IntensivePhrase
# 定义合法用户意图列表
VALID_INTENTS = {
    "信息查询", "设置目标", "运动记录", "睡眠记录",
    "运动建议", "睡眠建议", "成就记录", "健康建议", "寻求指导"
}


class UserConversationDB(Base):
    """用户对话记录数据库模型"""
    __tablename__ = "user_conversations"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 外键关联到用户
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("user_profiles.user_id"),
        nullable=False
    )

    # 对话内容
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    user_intent: Mapped[str] = mapped_column(String(50), nullable=False)
    ai_response: Mapped[str] = mapped_column(Text, nullable=False)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    # 关联关系
    user = relationship("UserProfileDB", back_populates="conversations")


# 在UserProfileDB中添加反向关系
UserProfileDB.conversations = relationship(
    "UserConversationDB",
    order_by=UserConversationDB.created_at,
    back_populates="user"
)


async def store_conversation(data: Dict) -> bool:
    """
    存储用户对话到数据库

    Args:
        data: 包含对话数据的字典

    Returns:
        bool: 操作是否成功
    """
    # 获取数据库管理器
    db_manager = get_database_manager()
    await db_manager.initialize()

    try:
        # 解包数据
        username = data.get("用户名")
        user_query = data.get("用户提问")
        user_intent = data.get("用户意图")
        ai_response = data.get("大模型回答")

        # 验证输入数据
        if not user_query or not ai_response:
            raise ValueError("用户提问或大模型回答为空")

        # 标准化用户意图
        normalized_intent = user_intent if user_intent in VALID_INTENTS else "Unknown"

        async with db_manager.get_session() as session:
            # 检查用户是否存在
            user = await session.get(UserProfileDB, username)
            if not user:
                raise ValueError(f"用户 '{username}' 不存在")

            # 创建新对话记录
            conversation = UserConversationDB(
                user_id=username,
                user_query=user_query,
                user_intent=normalized_intent,
                ai_response=ai_response
            )

            # 添加到会话并提交
            session.add(conversation)
            await session.commit()

            return True

    except ValueError as ve:
        # 处理验证错误
        print(f"验证错误: {ve}")
        return False

    except Exception as e:
        # 处理其他异常
        print(f"数据库操作失败: {e}")
        return False
