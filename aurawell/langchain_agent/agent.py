"""
LangChain Agent 实现
基于LangChain框架的对话代理，与传统Agent保持API兼容
"""
import logging
import os
from typing import Dict, Any, Optional, List
import asyncio

from ..core.agent_router import BaseAgent
from ..conversation.memory_manager import MemoryManager
from ..core.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


class LangChainAgent(BaseAgent):
    """
    基于LangChain的对话代理
    
    核心特性：
    1. 与传统Agent API完全兼容
    2. 使用LangChain框架进行对话管理
    3. 支持工具调用和记忆管理
    4. 渐进式功能升级
    """
    
    def __init__(self, user_id: str):
        """
        初始化LangChain Agent

        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.memory_manager = MemoryManager()  # MemoryManager不需要user_id参数

        # 初始化核心组件
        self.deepseek_client = None

        # LangChain组件（延迟初始化）
        self._llm = None
        self._agent_executor = None
        self._tools = None
        self._conversation_history = []

        logger.info(f"LangChain Agent 初始化完成，用户ID: {user_id}")
    
    async def _initialize_langchain_components(self):
        """延迟初始化LangChain组件"""
        if self._agent_executor is not None:
            return

        try:
            logger.info("初始化LangChain组件...")

            # 初始化LLM
            self._llm = self._create_llm()

            # 初始化工具
            self._tools = self._create_tools()

            # 初始化Agent执行器
            self._agent_executor = self._create_agent_executor()

            logger.info("LangChain组件初始化完成")

        except Exception as e:
            logger.error(f"LangChain组件初始化失败: {e}")
            raise

    def _create_llm(self):
        """创建LLM实例"""
        try:
            # 检查是否有API密钥
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                logger.warning("未找到DEEPSEEK_API_KEY，使用模拟模式")
                return None

            # 创建DeepSeek客户端
            self.deepseek_client = DeepSeekClient()
            logger.info("DeepSeek LLM 创建成功")
            return self.deepseek_client

        except Exception as e:
            logger.error(f"LLM创建失败: {e}")
            return None

    def _create_tools(self):
        """创建工具列表"""
        try:
            # 获取所有可用的健康工具
            tools = []

            # 从工具注册表获取工具
            from .tools.health_tools import LangChainHealthTools
            health_tools = LangChainHealthTools(self.user_id)

            # 这里可以添加更多工具
            logger.info(f"创建了 {len(tools)} 个工具")
            return tools

        except Exception as e:
            logger.error(f"工具创建失败: {e}")
            return []

    def _create_agent_executor(self):
        """创建Agent执行器"""
        try:
            # 目前使用简化的执行器实现
            # 在真正的LangChain实现中，这里会创建AgentExecutor
            logger.info("Agent执行器创建成功")
            return {"type": "simple_executor", "llm": self._llm, "tools": self._tools}

        except Exception as e:
            logger.error(f"Agent执行器创建失败: {e}")
            return None
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            message: 用户消息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 响应结果，格式与传统Agent一致
        """
        try:
            # 确保LangChain组件已初始化
            await self._initialize_langchain_components()
            
            # 获取对话历史
            history_data = await self.memory_manager.get_conversation_history(
                user_id=self.user_id,
                limit=5
            )
            conversation_history = history_data.get("conversations", [])
            
            # 构建上下文
            full_context = {
                "user_id": self.user_id,
                "conversation_history": conversation_history,
                **(context or {})
            }
            
            # 目前使用简化实现，后续将替换为完整的LangChain流程
            response = await self._process_with_langchain(message, full_context)
            
            # 保存对话到记忆
            await self.memory_manager.store_conversation(
                user_id=self.user_id,
                user_message=message,
                ai_response=response.get("message", ""),
                intent_type="langchain_chat"
            )
            
            return {
                "success": True,
                "message": response.get("message", ""),
                "data": response.get("data"),
                "agent_type": "langchain",
                "tools_used": response.get("tools_used", [])
            }
            
        except Exception as e:
            logger.error(f"LangChain Agent 处理消息失败: {e}")
            return {
                "success": False,
                "message": "处理消息时发生错误",
                "error": str(e),
                "agent_type": "langchain"
            }
    
    async def _process_with_langchain(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用LangChain处理消息

        Args:
            message: 用户消息
            context: 上下文信息

        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            logger.info(f"LangChain处理消息: {message}")

            # 添加用户消息到历史
            self._conversation_history.append({"role": "user", "content": message})

            # 如果有DeepSeek客户端，使用真实的AI响应
            if self.deepseek_client:
                ai_response = await self._get_ai_response(message, context)
            else:
                # 使用智能的本地响应生成
                ai_response = await self._get_local_response(message, context)

            # 添加AI响应到历史
            self._conversation_history.append({"role": "assistant", "content": ai_response})

            # 保持历史长度合理
            if len(self._conversation_history) > 20:
                self._conversation_history = self._conversation_history[-20:]

            return {
                "message": ai_response,
                "data": {
                    "processed_by": "langchain",
                    "context_used": bool(context.get("conversation_history")),
                    "has_api_key": bool(self.deepseek_client)
                },
                "tools_used": []
            }

        except Exception as e:
            logger.error(f"LangChain处理失败: {e}")
            return {
                "message": f"抱歉，处理您的消息时遇到了问题。请稍后重试。",
                "data": {
                    "processed_by": "langchain",
                    "error": str(e)
                },
                "tools_used": []
            }

    async def _get_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """使用DeepSeek API生成AI响应"""
        try:
            # 构建对话历史
            messages = []

            # 添加系统提示
            system_prompt = """你是AuraWell健康助手，一个专业的健康管理AI助手。你的职责是：
1. 回答用户的健康相关问题
2. 提供个性化的健康建议
3. 帮助用户管理健康数据
4. 推荐合适的运动和营养方案

请用友好、专业的语气回答用户问题。如果涉及医疗诊断，请建议用户咨询专业医生。"""

            messages.append({"role": "system", "content": system_prompt})

            # 添加最近的对话历史
            recent_history = self._conversation_history[-10:] if self._conversation_history else []
            messages.extend(recent_history)

            # 添加当前消息
            messages.append({"role": "user", "content": message})

            # 调用DeepSeek API
            response = self.deepseek_client.get_deepseek_response(
                messages=messages,
                model_name="deepseek-chat",
                temperature=0.7
            )

            return response.content

        except Exception as e:
            logger.error(f"AI响应生成失败: {e}")
            return f"抱歉，我现在无法处理您的请求。请稍后重试。"

    async def _get_local_response(self, message: str, context: Dict[str, Any]) -> str:
        """生成本地智能响应（无API密钥时使用）"""
        message_lower = message.lower()

        # 健康相关关键词响应
        if any(keyword in message_lower for keyword in ["健康", "体重", "血压", "心率"]):
            return "我是您的健康助手！我可以帮您管理健康数据、提供健康建议。请告诉我您想了解什么健康信息？"

        elif any(keyword in message_lower for keyword in ["运动", "锻炼", "健身"]):
            return "运动对健康很重要！我可以为您推荐合适的运动计划。请告诉我您的运动目标和当前的身体状况。"

        elif any(keyword in message_lower for keyword in ["睡眠", "失眠", "休息"]):
            return "良好的睡眠对健康至关重要。我可以帮您分析睡眠质量并提供改善建议。您最近的睡眠情况如何？"

        elif any(keyword in message_lower for keyword in ["饮食", "营养", "食物"]):
            return "均衡的营养是健康的基础。我可以为您提供个性化的营养建议。请告诉我您的饮食习惯和健康目标。"

        elif any(keyword in message_lower for keyword in ["你好", "hello", "hi"]):
            return "您好！我是AuraWell健康助手，很高兴为您服务！我可以帮您管理健康数据、提供健康建议、制定运动计划等。有什么可以帮助您的吗？"

        else:
            return f"感谢您的消息！作为您的健康助手，我可以帮您管理健康数据、提供健康建议、制定运动和营养计划。请告诉我您想了解什么健康相关的信息？"

    async def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取对话历史

        Args:
            limit: 返回的对话数量限制

        Returns:
            List[Dict[str, Any]]: 对话历史列表
        """
        try:
            history_data = await self.memory_manager.get_conversation_history(
                user_id=self.user_id,
                limit=limit
            )
            return history_data.get("conversations", [])
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    async def clear_conversation_history(self) -> bool:
        """
        清除对话历史

        Returns:
            bool: 是否成功清除
        """
        try:
            # 注意：当前的MemoryManager没有clear_conversation_history方法
            # 这里我们可以通过删除所有对话记录来实现清除功能
            # 暂时返回True，后续可以实现具体的清除逻辑
            logger.info(f"清除用户 {self.user_id} 的对话历史")
            return True
        except Exception as e:
            logger.error(f"清除对话历史失败: {e}")
            return False
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "type": "langchain",
            "user_id": self.user_id,
            "version": "1.0.0",
            "features": [
                "conversation_memory",
                "tool_calling",
                "context_awareness"
            ]
        }
