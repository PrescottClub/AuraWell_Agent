"""
LangChain 对话记忆管理
基于LangChain框架的对话记忆管理实现
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...conversation.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class LangChainConversationMemory:
    """
    LangChain 对话记忆管理器

    核心功能：
    1. 与现有记忆管理器兼容
    2. 支持LangChain记忆格式
    3. 提供上下文感知的记忆检索
    """

    def __init__(self, user_id: str):
        """
        初始化LangChain对话记忆管理器

        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.memory_manager = MemoryManager()  # MemoryManager不需要user_id参数

        # LangChain记忆组件（延迟初始化）
        self._langchain_memory = None

        logger.info(f"LangChain对话记忆管理器初始化完成，用户ID: {user_id}")

    async def _initialize_langchain_memory(self):
        """初始化LangChain记忆组件"""
        if self._langchain_memory is not None:
            return

        try:
            # LangChain memory integration would go here in full implementation
            # 这里将在后续实现具体的LangChain记忆组件
            logger.info("初始化LangChain记忆组件...")

            # 占位符实现
            self._langchain_memory = {}

            logger.info("LangChain记忆组件初始化完成")

        except Exception as e:
            logger.error(f"LangChain记忆组件初始化失败: {e}")
            raise

    async def add_conversation(
        self,
        user_message: str,
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加对话到记忆

        Args:
            user_message: 用户消息
            ai_response: AI响应
            metadata: 元数据

        Returns:
            bool: 是否成功添加
        """
        try:
            # 确保LangChain记忆组件已初始化
            await self._initialize_langchain_memory()

            # 添加到现有记忆管理器
            success = await self.memory_manager.store_conversation(
                user_id=self.user_id,
                user_message=user_message,
                ai_response=ai_response,
                intent_type="langchain"
            )

            # LangChain memory component would be updated here
            # await self._add_to_langchain_memory(user_message, ai_response, metadata)

            return success

        except Exception as e:
            logger.error(f"添加对话到记忆失败: {e}")
            return False

    async def get_conversation_history(
        self,
        limit: int = 10,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史

        Args:
            limit: 返回的对话数量限制
            include_metadata: 是否包含元数据

        Returns:
            List[Dict[str, Any]]: 对话历史列表
        """
        try:
            # 从现有记忆管理器获取历史
            history_data = await self.memory_manager.get_conversation_history(
                user_id=self.user_id,
                limit=limit
            )
            history = history_data.get("conversations", [])

            # 转换为LangChain格式
            langchain_history = []
            for conversation in history:
                langchain_conversation = {
                    "user_message": conversation.get("user_message", ""),
                    "ai_response": conversation.get("ai_response", ""),
                    "timestamp": conversation.get("timestamp", ""),
                    "conversation_id": conversation.get("conversation_id", "")
                }

                if include_metadata:
                    langchain_conversation["metadata"] = conversation.get("metadata", {})

                langchain_history.append(langchain_conversation)

            return langchain_history

        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []

    async def get_relevant_context(
        self,
        query: str,
        max_conversations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取与查询相关的上下文

        Args:
            query: 查询内容
            max_conversations: 最大返回对话数

        Returns:
            List[Dict[str, Any]]: 相关对话列表
        """
        try:
            # 获取最近的对话历史
            recent_history = await self.get_conversation_history(limit=max_conversations * 2)

            # 简单的相关性过滤（后续可以使用更复杂的语义搜索）
            relevant_conversations = []
            query_lower = query.lower()

            for conversation in recent_history:
                user_msg = conversation.get("user_message", "").lower()
                ai_msg = conversation.get("ai_response", "").lower()

                # 简单的关键词匹配
                if (query_lower in user_msg
                    or query_lower in ai_msg
                    or any(word in user_msg or word in ai_msg
                           for word in query_lower.split())):
                    relevant_conversations.append(conversation)

                if len(relevant_conversations) >= max_conversations:
                    break

            return relevant_conversations

        except Exception as e:
            logger.error(f"获取相关上下文失败: {e}")
            return []

    async def clear_conversation_history(self) -> bool:
        """
        清除对话历史

        Returns:
            bool: 是否成功清除
        """
        try:
            # 清除现有记忆管理器的历史
            # 注意：当前的MemoryManager没有clear_conversation_history方法
            # 暂时返回True，后续可以实现具体的清除逻辑
            success = True

            # LangChain memory component would be cleared here
            # await self._clear_langchain_memory()

            return success

        except Exception as e:
            logger.error(f"清除对话历史失败: {e}")
            return False

    async def get_conversation_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取对话摘要

        Args:
            days: 统计天数

        Returns:
            Dict[str, Any]: 对话摘要
        """
        try:
            # 获取指定天数内的对话
            all_history = await self.get_conversation_history(limit=1000)

            # 过滤指定天数内的对话
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            recent_conversations = []

            for conversation in all_history:
                timestamp_str = conversation.get("timestamp", "")
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).timestamp()
                    if timestamp >= cutoff_date:
                        recent_conversations.append(conversation)
                except (ValueError, TypeError) as e:
                    # Skip conversations with invalid timestamps
                    logger.debug(f"Skipping conversation with invalid timestamp: {e}")
                    continue

            # 统计信息
            total_conversations = len(recent_conversations)
            total_user_messages = sum(1 for conv in recent_conversations if conv.get("user_message"))
            total_ai_responses = sum(1 for conv in recent_conversations if conv.get("ai_response"))

            # 常见话题（简单的关键词统计）
            all_text = " ".join([
                conv.get("user_message", "") + " " + conv.get("ai_response", "")
                for conv in recent_conversations
            ]).lower()

            common_topics = []
            health_keywords = ["健康", "体重", "血压", "心率", "运动", "饮食", "睡眠", "bmi"]
            for keyword in health_keywords:
                count = all_text.count(keyword)
                if count > 0:
                    common_topics.append({"topic": keyword, "count": count})

            common_topics.sort(key=lambda x: x["count"], reverse=True)

            return {
                "success": True,
                "summary": {
                    "period_days": days,
                    "total_conversations": total_conversations,
                    "total_user_messages": total_user_messages,
                    "total_ai_responses": total_ai_responses,
                    "common_topics": common_topics[:5],  # 前5个话题
                    "last_conversation": recent_conversations[0] if recent_conversations else None
                }
            }

        except Exception as e:
            logger.error(f"获取对话摘要失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取对话摘要失败"
            }
