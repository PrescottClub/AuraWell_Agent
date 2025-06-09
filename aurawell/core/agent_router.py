"""
代理路由器
根据功能开关选择使用传统Agent还是LangChain Agent
确保API接口完全向后兼容
"""
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from .feature_flags import feature_flags

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """代理基类，定义统一接口"""
    
    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理用户消息"""
        pass
    
    @abstractmethod
    async def get_conversation_history(self, limit: int = 10) -> list:
        """获取对话历史"""
        pass
    
    @abstractmethod
    async def clear_conversation_history(self) -> bool:
        """清除对话历史"""
        pass


class AgentRouter:
    """
    代理路由器
    
    核心职责：
    1. 根据功能开关选择使用哪个Agent
    2. 确保API接口完全向后兼容
    3. 支持渐进式升级
    """
    
    def __init__(self):
        self.feature_flags = feature_flags
        self._agent_cache = {}  # 缓存Agent实例
    
    async def get_agent(self, user_id: str, feature_context: str = "chat") -> BaseAgent:
        """
        获取合适的Agent实例
        
        Args:
            user_id: 用户ID
            feature_context: 功能上下文（chat, health_query, tool_call等）
            
        Returns:
            BaseAgent: Agent实例
        """
        # 检查是否启用LangChain Agent
        use_langchain = self.feature_flags.is_enabled(
            "langchain_agent", 
            user_id=user_id, 
            context=feature_context
        )
        
        agent_key = f"{user_id}_{feature_context}_{'langchain' if use_langchain else 'traditional'}"
        
        # 从缓存获取或创建新实例
        if agent_key not in self._agent_cache:
            # 只使用LangChain Agent - 传统Agent已废弃
            try:
                # 动态导入LangChain Agent（避免循环导入）
                from ..langchain_agent.agent import LangChainAgent
                agent = LangChainAgent(user_id)
                logger.info(f"为用户 {user_id} 创建 LangChain Agent")
            except Exception as e:
                logger.error(f"LangChain Agent 创建失败: {e}")
                # 创建一个最基本的Agent实例作为最后的回退
                agent = self._create_fallback_agent(user_id)

            self._agent_cache[agent_key] = agent
        
        return self._agent_cache[agent_key]

    def _create_fallback_agent(self, user_id: str) -> BaseAgent:
        """创建一个最基本的fallback agent"""

        class FallbackAgent(BaseAgent):
            def __init__(self, user_id: str):
                self.user_id = user_id

            async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
                return {
                    "success": True,
                    "message": f"收到您的消息：{message}。系统正在维护中，请稍后重试。",
                    "data": None,
                    "agent_type": "fallback"
                }

            async def get_conversation_history(self, limit: int = 10) -> list:
                return []

            async def clear_conversation_history(self) -> bool:
                return True

        logger.warning(f"为用户 {user_id} 创建 Fallback Agent")
        return FallbackAgent(user_id)
    
    async def process_message(
        self, 
        user_id: str, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理用户消息（统一接口）
        
        Args:
            user_id: 用户ID
            message: 用户消息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 响应结果，格式与现有API完全一致
        """
        try:
            # 获取合适的Agent
            agent = await self.get_agent(user_id, "chat")
            
            # 处理消息
            response = await agent.process_message(message, context)
            
            # 确保响应格式与现有API一致
            return self._normalize_response(response)
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            # 返回错误响应，格式与现有API一致
            return {
                "success": False,
                "message": "处理消息时发生错误",
                "error": str(e),
                "data": None
            }
    
    def _normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化响应格式，确保与现有API完全一致
        
        Args:
            response: 原始响应
            
        Returns:
            Dict[str, Any]: 标准化后的响应
        """
        # 如果响应已经是标准格式，直接返回
        if all(key in response for key in ["success", "message", "data"]):
            return response
        
        # 转换为标准格式
        return {
            "success": response.get("success", True),
            "message": response.get("message", response.get("response", "")),
            "data": response.get("data", response),
            "agent_type": response.get("agent_type", "traditional")
        }
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> list:
        """获取对话历史"""
        try:
            agent = await self.get_agent(user_id, "history")
            return await agent.get_conversation_history(limit)
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    async def clear_conversation_history(self, user_id: str) -> bool:
        """清除对话历史"""
        try:
            agent = await self.get_agent(user_id, "clear_history")
            return await agent.clear_conversation_history()
        except Exception as e:
            logger.error(f"清除对话历史失败: {e}")
            return False
    
    def get_feature_status(self) -> Dict[str, Any]:
        """获取功能开关状态"""
        return self.feature_flags.get_all_features()
    
    def enable_langchain_for_user(self, user_id: str) -> None:
        """为特定用户启用LangChain Agent"""
        self.feature_flags.add_user_to_whitelist("langchain_agent", user_id)
        # 清除缓存，强制重新创建Agent
        keys_to_remove = [key for key in self._agent_cache.keys() if key.startswith(user_id)]
        for key in keys_to_remove:
            del self._agent_cache[key]
    
    def disable_langchain_for_user(self, user_id: str) -> None:
        """为特定用户禁用LangChain Agent"""
        self.feature_flags.remove_user_from_whitelist("langchain_agent", user_id)
        # 清除缓存，强制重新创建Agent
        keys_to_remove = [key for key in self._agent_cache.keys() if key.startswith(user_id)]
        for key in keys_to_remove:
            del self._agent_cache[key]


# 全局代理路由器实例
agent_router = AgentRouter()
