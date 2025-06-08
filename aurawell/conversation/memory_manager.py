"""
对话历史管理模块

支持多用户独立对话历史存储和检索。
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from sqlalchemy import Column, String, Text, DateTime, Integer, desc, select

from ..database import get_database_manager, Base

logger = logging.getLogger(__name__)


class ConversationHistory(Base):
    """对话历史数据模型"""
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
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
            "session_id": self.session_id,
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
            intent_type: 意图类型（可选）
            confidence: 置信度（可选）

        Returns:
            True表示操作成功，False表示操作失败
        """
        try:
            async with self.db_manager.get_session() as session:
                # 创建对话记录
                conversation = ConversationHistory(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=user_message,
                    ai_response=ai_response,
                    intent_type=intent_type,
                    confidence=str(confidence) if confidence else None,
                    created_at=datetime.now(timezone.utc)
                )

                session.add(conversation)
                await session.commit()

                # 清理旧的对话历史（保持最新的max_history_rounds轮）
                await self._cleanup_old_conversations(user_id)

                logger.info("Conversation stored successfully for user: %s", user_id)
                return True

        except Exception as e:
            logger.error("Failed to store conversation for user %s: %s", user_id, str(e))
            return False

    async def get_conversation_history(
        self,
        user_id: str,
        limit: int = 10,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取对话历史

        Args:
            user_id: 用户ID
            limit: 限制返回的对话轮数（默认10轮）
            session_id: 会话ID（可选，用于获取特定会话的历史）

        Returns:
            包含对话历史的字典
        """
        try:
            async with self.db_manager.get_session() as session:
                # 构建查询
                query = select(ConversationHistory).filter(
                    ConversationHistory.user_id == user_id
                )

                if session_id:
                    query = query.filter(ConversationHistory.session_id == session_id)

                # 按时间倒序排列，取最新的limit条记录
                query = query.order_by(
                    desc(ConversationHistory.created_at)
                ).limit(limit)

                result = await session.execute(query)
                conversations = result.scalars().all()

                # 转换为字典格式并按时间正序排列（最早的在前）
                history_list = [conv.to_dict() for conv in reversed(conversations)]

                logger.info("Retrieved %d conversation records for user: %s",
                           len(history_list), user_id)

                return {
                    "user_id": user_id,
                    "session_id": session_id,
                    "total_conversations": len(history_list),
                    "conversations": history_list,
                    "retrieved_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error("Failed to get conversation history for user %s: %s",
                        user_id, str(e))
            return {
                "user_id": user_id,
                "session_id": session_id,
                "total_conversations": 0,
                "conversations": [],
                "error": str(e)
            }

    async def _cleanup_old_conversations(self, user_id: str) -> None:
        """
        清理旧的对话历史，保持最新的max_history_rounds轮对话

        Args:
            user_id: 用户ID
        """
        try:
            async with self.db_manager.get_session() as session:
                # 获取该用户的所有对话，按时间倒序
                query = select(ConversationHistory).filter(
                    ConversationHistory.user_id == user_id
                ).order_by(desc(ConversationHistory.created_at))

                result = await session.execute(query)
                all_conversations = result.scalars().all()

                # 如果超过限制，删除旧的对话
                if len(all_conversations) > self.max_history_rounds:
                    conversations_to_delete = all_conversations[self.max_history_rounds:]

                    for conv in conversations_to_delete:
                        await session.delete(conv)

                    await session.commit()
                    logger.info("Cleaned up %d old conversations for user: %s",
                               len(conversations_to_delete), user_id)

        except Exception as e:
            logger.error("Failed to cleanup conversations for user %s: %s",
                        user_id, str(e))