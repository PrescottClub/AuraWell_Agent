"""
会话管理模块

支持会话创建、管理和上下文维护。
"""

import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, select

from ..database import get_database_manager, Base

logger = logging.getLogger(__name__)


class UserSession(Base):
    """用户会话数据模型"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    context_data = Column(Text, nullable=True)  # JSON格式的上下文数据
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active
        }


class SessionManager:
    """
    会话管理器

    支持会话创建、管理和上下文维护，包括会话超时处理。
    """

    def __init__(self, session_timeout_hours: int = 24):
        """
        初始化会话管理器

        Args:
            session_timeout_hours: 会话超时时间（小时），默认24小时
        """
        self.db_manager = get_database_manager()
        self.session_timeout_hours = session_timeout_hours

    async def create_session(self, user_id: str, context_data: Optional[Dict[str, Any]] = None) -> str:
        """
        创建新会话

        Args:
            user_id: 用户ID
            context_data: 初始上下文数据（可选）

        Returns:
            新创建的会话ID
        """
        try:
            # 生成唯一的会话ID
            session_id = f"session_{user_id}_{uuid.uuid4().hex[:8]}"

            # 计算过期时间
            expires_at = datetime.now(timezone.utc) + timedelta(hours=self.session_timeout_hours)

            async with self.db_manager.get_session() as session:
                # 创建会话记录
                user_session = UserSession(
                    session_id=session_id,
                    user_id=user_id,
                    context_data=json.dumps(context_data) if context_data else None,
                    created_at=datetime.now(timezone.utc),
                    last_activity=datetime.now(timezone.utc),
                    expires_at=expires_at,
                    is_active=True
                )

                session.add(user_session)
                await session.commit()

                logger.info("Session created successfully: %s for user: %s", session_id, user_id)
                return session_id

        except Exception as e:
            logger.error("Failed to create session for user %s: %s", user_id, str(e))
            # 返回一个临时会话ID作为fallback
            return f"temp_session_{user_id}_{uuid.uuid4().hex[:8]}"

    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话上下文

        Args:
            session_id: 会话ID

        Returns:
            包含会话上下文的字典
        """
        try:
            async with self.db_manager.get_session() as session:
                # 查询会话
                query = select(UserSession).filter(
                    UserSession.session_id == session_id,
                    UserSession.is_active == True
                )
                result = await session.execute(query)
                user_session = result.scalar_one_or_none()

                if not user_session:
                    logger.warning("Session not found or inactive: %s", session_id)
                    return {
                        "session_id": session_id,
                        "exists": False,
                        "error": "Session not found or inactive"
                    }

                # 检查会话是否过期
                current_time = datetime.now(timezone.utc)
                if user_session.expires_at and current_time > user_session.expires_at.replace(tzinfo=timezone.utc):
                    # 标记会话为过期
                    user_session.is_active = False
                    await session.commit()

                    logger.info("Session expired: %s", session_id)
                    return {
                        "session_id": session_id,
                        "exists": False,
                        "error": "Session expired"
                    }

                # 更新最后活动时间
                user_session.last_activity = datetime.now(timezone.utc)
                await session.commit()

                logger.info("Session context retrieved: %s", session_id)
                return {
                    "session_id": session_id,
                    "user_id": user_session.user_id,
                    "exists": True,
                    "context_data": user_session.context_data,
                    "created_at": user_session.created_at.isoformat() if user_session.created_at else None,
                    "last_activity": user_session.last_activity.isoformat() if user_session.last_activity else None,
                    "expires_at": user_session.expires_at.isoformat() if user_session.expires_at else None
                }

        except Exception as e:
            logger.error("Failed to get session context for %s: %s", session_id, str(e))
            return {
                "session_id": session_id,
                "exists": False,
                "error": str(e)
            }

    async def update_session_context(
        self,
        session_id: str,
        context_data: Dict[str, Any]
    ) -> bool:
        """
        更新会话上下文

        Args:
            session_id: 会话ID
            context_data: 新的上下文数据

        Returns:
            True表示更新成功，False表示失败
        """
        try:
            async with self.db_manager.get_session() as session:
                query = select(UserSession).filter(
                    UserSession.session_id == session_id,
                    UserSession.is_active == True
                )
                result = await session.execute(query)
                user_session = result.scalar_one_or_none()

                if not user_session:
                    logger.warning("Session not found for update: %s", session_id)
                    return False

                # 更新上下文数据和最后活动时间
                user_session.context_data = json.dumps(context_data)
                user_session.last_activity = datetime.now(timezone.utc)

                await session.commit()

                logger.info("Session context updated: %s", session_id)
                return True

        except Exception as e:
            logger.error("Failed to update session context for %s: %s", session_id, str(e))
            return False

    async def cleanup_expired_sessions(self) -> int:
        """
        清理过期的会话

        Returns:
            清理的会话数量
        """
        try:
            async with self.db_manager.get_session() as session:
                current_time = datetime.now(timezone.utc)

                # 查找过期的会话
                query = select(UserSession).filter(
                    UserSession.expires_at < current_time,
                    UserSession.is_active == True
                )
                result = await session.execute(query)
                expired_sessions = result.scalars().all()

                # 标记为非活跃
                count = 0
                for user_session in expired_sessions:
                    user_session.is_active = False
                    count += 1

                await session.commit()

                logger.info("Cleaned up %d expired sessions", count)
                return count

        except Exception as e:
            logger.error("Failed to cleanup expired sessions: %s", str(e))
            return 0