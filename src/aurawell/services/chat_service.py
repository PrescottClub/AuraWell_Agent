"""
Chat Service

Business logic for health chat functionality.
Handles conversation management, message processing, and AI integration.
Supports family member data isolation.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..repositories.chat_repository import ChatRepository
from ..models.chat_models import (
    HealthChatResponse,
    ConversationResponse,
    ConversationListResponse,
    ChatHistoryResponse,
    HealthSuggestionsResponse,
    HealthSuggestion,
    QuickReply,
    ConversationHistoryKey,
)
from ..models.family_models import MemberDataContext
from ..core.agent_router import agent_router
from ..conversation.memory_manager import MemoryManager
from ..services.data_sanitization_service import DataSanitizationService
from ..services.model_fallback_service import get_model_fallback_service, ModelTier

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing health chat functionality with family member support"""

    def __init__(
        self, data_sanitization_service: Optional[DataSanitizationService] = None
    ):
        self.chat_repo = ChatRepository()
        self.memory_manager = MemoryManager()
        self.data_sanitization_service = data_sanitization_service

        # 初始化多模型梯度服务
        try:
            from ..core.service_factory import ServiceClientFactory
            deepseek_client = ServiceClientFactory.get_deepseek_client()
            self.model_fallback_service = get_model_fallback_service(deepseek_client)
            logger.info("多模型梯度服务初始化成功")
        except Exception as e:
            logger.warning(f"多模型梯度服务初始化失败: {e}")
            self.model_fallback_service = None

    async def create_conversation(
        self,
        user_id: str,
        conversation_type: str = "health_consultation",
        metadata: Optional[Dict[str, Any]] = None,
        member_id: Optional[str] = None,
    ) -> ConversationResponse:
        """Create a new health consultation conversation"""
        try:
            # Generate conversation ID with member context
            timestamp = int(datetime.utcnow().timestamp())
            if member_id:
                conversation_id = f"conv_{user_id}_{member_id}_{timestamp}"
            else:
                conversation_id = f"conv_{user_id}_{timestamp}"

            # Add member_id to metadata if provided
            enhanced_metadata = metadata or {}
            if member_id:
                enhanced_metadata["member_id"] = member_id

            conversation = await self.chat_repo.create_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                conversation_type=conversation_type,
                metadata=enhanced_metadata,
            )

            return ConversationResponse(
                conversation_id=conversation.id,
                type=conversation.type,
                created_at=conversation.created_at,
                title=conversation.title,
                status=conversation.status,
            )

        except Exception as e:
            logger.error(f"Failed to create conversation for user {user_id}: {e}")
            raise

    async def get_user_conversations(
        self, user_id: str, member_id: Optional[str] = None
    ) -> ConversationListResponse:
        """Get user's conversation list"""
        try:
            # Filter conversations by member_id if provided
            conversations = await self.chat_repo.get_user_conversations(
                user_id, member_id=member_id
            )

            return ConversationListResponse(
                message="Conversations retrieved successfully",
                conversations=conversations,
            )

        except Exception as e:
            logger.error(f"Failed to get conversations for user {user_id}: {e}")
            raise

    async def process_chat_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        member_id: Optional[str] = None,
    ) -> HealthChatResponse:
        """Process a chat message and generate AI response"""
        try:
            # Create conversation if not provided
            if not conversation_id:
                conv_response = await self.create_conversation(
                    user_id, member_id=member_id
                )
                conversation_id = conv_response.conversation_id

            # Verify conversation exists and belongs to user
            conversation = await self.chat_repo.get_conversation(
                conversation_id, user_id
            )
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Save user message
            user_message_id = f"msg_{uuid.uuid4().hex[:12]}"
            await self.chat_repo.save_message(
                message_id=user_message_id,
                conversation_id=conversation_id,
                sender="user",
                content=message,
            )

            # Generate AI response using agent router with member context
            enhanced_context = context or {}
            if member_id:
                enhanced_context["member_id"] = member_id

            ai_response = await self._generate_ai_response(
                user_id=user_id,
                message=message,
                conversation_id=conversation_id,
                context=enhanced_context,
            )

            # Save AI response
            ai_message_id = f"msg_{uuid.uuid4().hex[:12]}"
            await self.chat_repo.save_message(
                message_id=ai_message_id,
                conversation_id=conversation_id,
                sender="agent",
                content=ai_response["reply"],
                metadata={
                    "suggestions": ai_response.get("suggestions", []),
                    "quick_replies": ai_response.get("quick_replies", []),
                    "member_id": member_id,
                },
            )

            # Store conversation in memory manager with member isolation
            await self.memory_manager.store_conversation(
                user_id=user_id,
                user_message=message,
                ai_response=ai_response["reply"],
                session_id=conversation_id,
                member_id=member_id,
            )

            return HealthChatResponse(
                message="Chat processed successfully",
                reply=ai_response["reply"],
                conversation_id=conversation_id,
                message_id=ai_message_id,
                timestamp=datetime.utcnow(),
                suggestions=ai_response.get("suggestions"),
                quick_replies=ai_response.get("quick_replies"),
            )

        except Exception as e:
            logger.error(f"Failed to process chat message: {e}")
            raise

    async def get_chat_history(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        member_id: Optional[str] = None,
    ) -> ChatHistoryResponse:
        """Get chat history for a conversation"""
        try:
            # Verify conversation belongs to user
            conversation = await self.chat_repo.get_conversation(
                conversation_id, user_id
            )
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Get messages with member context filtering
            messages, total = await self.chat_repo.get_conversation_messages(
                conversation_id=conversation_id,
                limit=limit,
                offset=offset,
                member_id=member_id,
            )

            # Apply data sanitization if needed
            if self.data_sanitization_service and member_id:
                # Create data context for sanitization
                data_context = (
                    await self.data_sanitization_service.create_member_data_context(
                        requester_user_id=user_id,
                        target_user_id=user_id,
                        target_member_id=member_id,
                    )
                )

                # Sanitize messages based on access level
                sanitized_messages = []
                for msg in messages:
                    if data_context.data_access_level.value != "full":
                        # Apply basic sanitization to message content
                        msg_dict = msg.dict() if hasattr(msg, "dict") else msg.__dict__
                        sanitized_msg_data = (
                            await self.data_sanitization_service.sanitize_user_data(
                                msg_dict, data_context
                            )
                        )
                        # Update message with sanitized content if needed
                        sanitized_messages.append(msg)
                    else:
                        sanitized_messages.append(msg)
                messages = sanitized_messages

            has_more = (offset + len(messages)) < total

            return ChatHistoryResponse(
                message="Chat history retrieved successfully",
                messages=messages,
                total=total,
                has_more=has_more,
            )

        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            raise

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        try:
            return await self.chat_repo.delete_conversation(conversation_id, user_id)

        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False

    async def get_health_suggestions(self) -> HealthSuggestionsResponse:
        """Get health suggestion templates"""
        try:
            suggestions = await self.chat_repo.get_health_suggestions()

            return HealthSuggestionsResponse(
                message="Health suggestions retrieved successfully",
                suggestions=suggestions,
            )

        except Exception as e:
            logger.error(f"Failed to get health suggestions: {e}")
            raise

    async def _generate_ai_response(
        self,
        user_id: str,
        message: str,
        conversation_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate AI response using the agent router with multi-model fallback"""
        try:
            # 首先尝试使用agent router处理消息
            response = await agent_router.process_message(
                user_id=user_id,
                message=message,
                context={
                    "conversation_id": conversation_id,
                    "request_type": "health_chat",
                    **(context or {}),
                },
            )

            # Extract reply from response
            reply = response.get("message", "")

            # 如果agent router返回的回复为空或失败，尝试使用多模型服务
            if not reply or reply.strip() == "" or "抱歉" in reply:
                logger.info("Agent router响应不理想，尝试使用多模型梯度服务")
                reply = await self._get_fallback_ai_response(message, conversation_id)

            # Generate health-specific suggestions and quick replies
            suggestions, quick_replies = self._generate_health_suggestions(
                message, reply
            )

            return {
                "reply": reply,
                "suggestions": suggestions,
                "quick_replies": quick_replies,
                "tools_used": response.get("tools_used", []),
            }

        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            # 尝试使用多模型服务作为最后的备选
            try:
                fallback_reply = await self._get_fallback_ai_response(message, conversation_id)
                return {
                    "reply": fallback_reply,
                    "suggestions": [],
                    "quick_replies": [],
                }
            except Exception as fallback_error:
                logger.error(f"Fallback AI response also failed: {fallback_error}")
                return {
                    "reply": "抱歉，我现在无法处理您的请求。请稍后再试。",
                    "suggestions": [],
                    "quick_replies": [],
                }

    async def _get_fallback_ai_response(self, message: str, conversation_id: str) -> str:
        """使用多模型梯度服务获取AI响应"""
        if not self.model_fallback_service:
            return "AI服务暂时不可用，请稍后再试。"

        try:
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的健康助手，请为用户提供有用的健康建议和信息。回答要简洁、准确、有帮助。"
                },
                {
                    "role": "user",
                    "content": message
                }
            ]

            # 使用多模型服务获取响应
            model_response = await self.model_fallback_service.get_model_response(
                messages=messages,
                conversation_id=conversation_id,
                preferred_tier=ModelTier.HIGH_PRECISION,
                temperature=0.7,
                max_tokens=1024
            )

            if model_response.success:
                logger.info(f"多模型服务响应成功，使用模型: {model_response.model_used}")
                return model_response.content
            else:
                logger.error(f"多模型服务响应失败: {model_response.error_message}")
                return "抱歉，AI服务暂时不可用，请稍后再试。"

        except Exception as e:
            logger.error(f"多模型服务调用失败: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"

    def _generate_health_suggestions(
        self, user_message: str, ai_reply: str
    ) -> tuple[List[HealthSuggestion], List[QuickReply]]:
        """Generate contextual health suggestions and quick replies"""
        suggestions = []
        quick_replies = []

        message_lower = user_message.lower()

        # Generate suggestions based on message content
        if any(keyword in message_lower for keyword in ["减重", "减肥", "瘦身"]):
            suggestions.extend(
                [
                    HealthSuggestion(
                        title="科学减重原理",
                        content="健康减重的核心是创造热量缺口，即消耗的热量大于摄入的热量。",
                        action="learn_more",
                        action_text="了解更多",
                    ),
                    HealthSuggestion(
                        title="运动建议",
                        content="结合有氧运动和力量训练，有氧运动燃烧脂肪，力量训练保持肌肉量。",
                        action="view_plan",
                        action_text="查看计划",
                    ),
                ]
            )
            quick_replies.extend(
                [
                    QuickReply(text="我身高170cm，体重75kg"),
                    QuickReply(text="我想在3个月内减重10kg"),
                    QuickReply(text="我平时很少运动"),
                    QuickReply(text="我没有特殊饮食限制"),
                ]
            )

        elif any(keyword in message_lower for keyword in ["睡眠", "失眠", "睡觉"]):
            suggestions.extend(
                [
                    HealthSuggestion(
                        title="睡眠卫生原则",
                        content="保持规律作息、创造良好睡眠环境、避免睡前刺激性活动。",
                        action="learn_more",
                        action_text="了解更多",
                    ),
                    HealthSuggestion(
                        title="放松技巧",
                        content="尝试深呼吸、渐进性肌肉放松或冥想来帮助入睡。",
                        action="try_technique",
                        action_text="尝试技巧",
                    ),
                ]
            )
            quick_replies.extend(
                [
                    QuickReply(text="我通常12点睡觉，7点起床"),
                    QuickReply(text="入睡很困难，要1小时以上"),
                    QuickReply(text="睡前会看手机"),
                    QuickReply(text="卧室比较吵闹"),
                ]
            )

        elif any(keyword in message_lower for keyword in ["运动", "锻炼", "健身"]):
            suggestions.extend(
                [
                    HealthSuggestion(
                        title="运动频率建议",
                        content="建议每周至少150分钟中等强度有氧运动，加上2次力量训练。",
                        action="create_plan",
                        action_text="制定计划",
                    ),
                    HealthSuggestion(
                        title="循序渐进原则",
                        content="从低强度开始，逐步增加运动量和强度，避免运动伤害。",
                        action="learn_more",
                        action_text="了解更多",
                    ),
                ]
            )
            quick_replies.extend(
                [
                    QuickReply(text="我想减重和提高体能"),
                    QuickReply(text="我是运动新手"),
                    QuickReply(text="每周能运动3-4次"),
                    QuickReply(text="我喜欢跑步和游泳"),
                ]
            )

        return suggestions, quick_replies
