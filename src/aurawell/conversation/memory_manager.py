"""
对话历史管理模块

支持多用户独立对话历史存储和检索，支持家庭成员数据隔离。
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from sqlalchemy import Column, String, Text, DateTime, Integer, desc, select

from ..database import get_database_manager, Base
from ..models.api_models import ConversationHistoryKey, MemberDataContext

logger = logging.getLogger(__name__)


class ConversationHistory(Base):
    """对话历史数据模型 - 支持家庭成员数据隔离"""
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    member_id = Column(String(50), nullable=True, index=True)  # 新增：家庭成员ID
    session_id = Column(String(100), nullable=True, index=True)
    isolation_key = Column(String(150), nullable=False, index=True)  # 新增：复合隔离键
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    intent_type = Column(String(50), nullable=True)
    confidence = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "member_id": self.member_id,
            "session_id": self.session_id,
            "isolation_key": self.isolation_key,
            "user_message": self.user_message,
            "ai_response": self.ai_response,
            "intent_type": self.intent_type,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MemoryManager:
    """
    对话历史管理器

    支持多用户独立对话历史存储和检索，限制10轮对话历史。
    """

    def __init__(self):
        """初始化内存管理器"""
        self.db_manager = get_database_manager()
        self.max_history_rounds = 10

    async def store_conversation(
        self,
        user_id: str,
        user_message: str,
        ai_response: str,
        session_id: Optional[str] = None,
        member_id: Optional[str] = None,
        intent_type: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """
        存储对话历史

        Args:
            user_id: 用户ID
            user_message: 用户消息
            ai_response: AI回复
            session_id: 会话ID（可选）
            member_id: 家庭成员ID（可选，用于数据隔离）
            intent_type: 意图类型（可选）
            confidence: 置信度（可选）

        Returns:
            True表示操作成功，False表示操作失败
        """
        try:
            async with self.db_manager.get_session() as session:
                # 生成隔离键
                history_key = ConversationHistoryKey(
                    user_id=user_id,
                    member_id=member_id,
                    session_id=session_id
                )
                isolation_key = history_key.composite_key
                
                # 创建对话记录
                conversation = ConversationHistory(
                    user_id=user_id,
                    member_id=member_id,
                    session_id=session_id,
                    isolation_key=isolation_key,
                    user_message=user_message,
                    ai_response=ai_response,
                    intent_type=intent_type,
                    confidence=str(confidence) if confidence else None,
                    created_at=datetime.now(timezone.utc)
                )

                session.add(conversation)
                await session.commit()

                # 清理旧的对话历史（保持最新的max_history_rounds轮）
                await self._cleanup_old_conversations(isolation_key)

                logger.info("Conversation stored successfully for isolation_key: %s", isolation_key)
                return True

        except Exception as e:
            logger.error("Failed to store conversation for user %s: %s", user_id, str(e))
            return False

    async def get_conversation_history(
        self,
        user_id: str,
        limit: int = 10,
        session_id: Optional[str] = None,
        member_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取对话历史

        Args:
            user_id: 用户ID
            limit: 限制返回的对话轮数（默认10轮）
            session_id: 会话ID（可选，用于获取特定会话的历史）
            member_id: 家庭成员ID（可选，用于数据隔离）

        Returns:
            包含对话历史的字典
        """
        try:
            async with self.db_manager.get_session() as session:
                # 生成隔离键进行查询
                history_key = ConversationHistoryKey(
                    user_id=user_id,
                    member_id=member_id,
                    session_id=session_id
                )
                isolation_key = history_key.composite_key
                
                # 构建查询 - 使用隔离键进行精确匹配
                if session_id:
                    # 如果指定了session_id，使用完整的隔离键
                    query = select(ConversationHistory).filter(
                        ConversationHistory.isolation_key == isolation_key
                    )
                else:
                    # 如果没有指定session_id，匹配用户和成员的所有对话
                    base_key = f"{user_id}:{member_id}" if member_id else user_id
                    query = select(ConversationHistory).filter(
                        ConversationHistory.isolation_key.like(f"{base_key}%")
                    )

                # 按时间倒序排列，取最新的limit条记录
                query = query.order_by(
                    desc(ConversationHistory.created_at)
                ).limit(limit)

                result = await session.execute(query)
                conversations = result.scalars().all()

                # 转换为字典格式并按时间正序排列（最早的在前）
                history_list = [conv.to_dict() for conv in reversed(conversations)]

                logger.info("Retrieved %d conversation records for isolation_key: %s",
                           len(history_list), isolation_key)

                return {
                    "user_id": user_id,
                    "member_id": member_id,
                    "session_id": session_id,
                    "isolation_key": isolation_key,
                    "total_conversations": len(history_list),
                    "conversations": history_list,
                    "retrieved_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error("Failed to get conversation history for user %s: %s",
                        user_id, str(e))
            return {
                "user_id": user_id,
                "member_id": member_id,
                "session_id": session_id,
                "total_conversations": 0,
                "conversations": [],
                "error": str(e)
            }

    async def _cleanup_old_conversations(self, isolation_key: str) -> None:
        """
        清理旧的对话历史，保持最新的max_history_rounds轮对话

        Args:
            isolation_key: 隔离键（用户ID或用户ID:成员ID的组合）
        """
        try:
            async with self.db_manager.get_session() as session:
                # 获取该隔离键的所有对话，按时间倒序
                base_key = isolation_key.split(':')[0] + ':' + isolation_key.split(':')[1] if ':' in isolation_key else isolation_key
                query = select(ConversationHistory).filter(
                    ConversationHistory.isolation_key.like(f"{base_key}%")
                ).order_by(desc(ConversationHistory.created_at))

                result = await session.execute(query)
                all_conversations = result.scalars().all()

                # 如果超过限制，删除旧的对话
                if len(all_conversations) > self.max_history_rounds:
                    conversations_to_delete = all_conversations[self.max_history_rounds:]

                    for conv in conversations_to_delete:
                        await session.delete(conv)

                    await session.commit()
                    logger.info("Cleaned up %d old conversations for isolation_key: %s",
                               len(conversations_to_delete), isolation_key)

        except Exception as e:
            logger.error("Failed to cleanup conversations for isolation_key %s: %s",
                        isolation_key, str(e))