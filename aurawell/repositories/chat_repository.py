"""
Chat Repository

Handles database operations for conversations and messages.
Provides data access layer for health chat functionality.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..database.models import ConversationDB, MessageDB, UserHealthProfileDB
from ..models.api_models import (
    ConversationListItem, ChatMessage, HealthSuggestion, QuickReply
)

logger = logging.getLogger(__name__)


class ChatRepository:
    """Repository for chat-related database operations"""

    async def create_conversation(
        self,
        user_id: str,
        conversation_id: str,
        conversation_type: str = "health_consultation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationDB:
        """Create a new conversation"""
        try:
            conversation = ConversationDB(
                id=conversation_id,
                user_id=user_id,
                type=conversation_type,
                status="active",
                extra_metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Use mock database for now
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationListItem]:
        """Get user's conversation list"""
        try:
            # Mock data for now - replace with actual database query
            conversations = [
                ConversationListItem(
                    id=f"conv_{user_id}_1",
                    title="减重计划咨询",
                    last_message="我为您制定了个性化的减重方案...",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    message_count=15,
                    status="active"
                ),
                ConversationListItem(
                    id=f"conv_{user_id}_2",
                    title="睡眠质量改善",
                    last_message="根据您的作息情况，建议...",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    message_count=8,
                    status="active"
                )
            ]
            
            logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get conversations for user {user_id}: {e}")
            raise

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> Optional[ConversationDB]:
        """Get a specific conversation"""
        try:
            # Mock conversation for now
            conversation = ConversationDB(
                id=conversation_id,
                user_id=user_id,
                type="health_consultation",
                status="active",
                title="健康咨询对话",
                extra_metadata={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            logger.info(f"Retrieved conversation {conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            return None

    async def save_message(
        self,
        message_id: str,
        conversation_id: str,
        sender: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageDB:
        """Save a chat message"""
        try:
            message = MessageDB(
                id=message_id,
                conversation_id=conversation_id,
                sender=sender,
                content=content,
                extra_metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Saved message {message_id} in conversation {conversation_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ChatMessage], int]:
        """Get messages from a conversation"""
        try:
            # Mock messages for now
            messages = [
                ChatMessage(
                    id="msg_1",
                    sender="user",
                    content="我想制定一个减重计划",
                    timestamp=datetime.utcnow()
                ),
                ChatMessage(
                    id="msg_2",
                    sender="agent",
                    content="很高兴帮助您制定减重计划！为了给您最适合的建议，我需要了解一些基本信息...",
                    timestamp=datetime.utcnow(),
                    suggestions=[
                        HealthSuggestion(
                            title="科学减重原理",
                            content="健康减重的核心是创造热量缺口...",
                            action="learn_more",
                            action_text="了解更多"
                        )
                    ],
                    quick_replies=[
                        QuickReply(text="我身高170cm，体重75kg"),
                        QuickReply(text="我想在3个月内减重10kg")
                    ]
                )
            ]
            
            total = len(messages)
            logger.info(f"Retrieved {len(messages)} messages from conversation {conversation_id}")
            return messages, total
            
        except Exception as e:
            logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
            raise

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Delete a conversation and all its messages"""
        try:
            # Mock deletion for now
            logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False

    async def update_conversation_title(
        self,
        conversation_id: str,
        user_id: str,
        title: str
    ) -> bool:
        """Update conversation title"""
        try:
            # Mock update for now
            logger.info(f"Updated title for conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation title: {e}")
            return False

    async def get_health_suggestions(self) -> List[str]:
        """Get health suggestion templates"""
        return [
            "我想制定一个减重计划",
            "如何改善我的睡眠质量？",
            "请帮我分析我的运动数据",
            "我需要营养饮食建议",
            "如何建立健康的作息习惯？",
            "我想了解心率数据的含义",
            "如何制定合理的健身计划？",
            "请给我一些压力管理建议"
        ]
