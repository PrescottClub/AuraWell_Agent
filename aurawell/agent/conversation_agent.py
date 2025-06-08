"""
ConversationAgent - 集成意图识别和对话管理的智能对话代理

M2-7: 集成所有模块并优化对话流程
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from .tools_registry import HealthToolsRegistry
from .intent_parser import IntentParser, IntentType
from ..conversation.memory_manager import MemoryManager
from ..conversation.session_manager import SessionManager
from ..core.deepseek_client import DeepSeekClient

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class ConversationAgent:
    """
    集成意图识别和对话管理的智能对话代理

    功能特性:
    - 智能意图识别
    - 对话历史管理
    - 会话上下文维护
    - 工具调用优化
    - 性能监控
    """

    def __init__(self, user_id: str, demo_mode: bool = False, session_id: Optional[str] = None):
        """
        初始化对话代理

        Args:
            user_id: 用户ID
            demo_mode: 是否为演示模式
            session_id: 会话ID（可选，如果不提供会自动创建）
        """
        self.user_id = user_id
        self.demo_mode = demo_mode
        self.session_id = session_id

        # 初始化核心组件
        self.tools_registry = HealthToolsRegistry()
        self.intent_parser = IntentParser()
        self.memory_manager = MemoryManager()
        self.session_manager = SessionManager()

        # 初始化对话历史
        self.history: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": ("You are AuraWell, a personalized health and wellness assistant. "
                           "Your goal is to help users understand their health data and achieve "
                           "their wellness goals. You should be encouraging, clear, and provide "
                           "actionable advice. When you need to access health data or perform "
                           "specific actions, use the available tools.")
            }
        ]

        # 初始化DeepSeek客户端
        self._initialize_deepseek_client()

        # 会话将在第一次调用a_run时初始化
        self._session_initialized = False

    def _initialize_deepseek_client(self):
        """初始化DeepSeek客户端"""
        if not self.demo_mode:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                logger.warning("DEEPSEEK_API_KEY not found. Switching to demo mode.")
                self.demo_mode = True
            else:
                try:
                    self.deepseek_client = DeepSeekClient()
                    logger.info("DeepSeek client initialized successfully")
                except Exception as e:
                    logger.error("Failed to initialize DeepSeek client: %s", str(e))
                    self.demo_mode = True

    async def _initialize_session(self):
        """初始化或恢复会话"""
        try:
            if not self.session_id:
                # 创建新会话
                self.session_id = await self.session_manager.create_session(self.user_id)
                logger.info("Created new session: %s", self.session_id)
            else:
                # 验证现有会话
                session_context = await self.session_manager.get_session_context(self.session_id)
                if not session_context.get("exists", False):
                    # 会话不存在或已过期，创建新会话
                    self.session_id = await self.session_manager.create_session(self.user_id)
                    logger.info("Session expired, created new session: %s", self.session_id)
                else:
                    logger.info("Restored existing session: %s", self.session_id)

            # 加载对话历史
            await self._load_conversation_history()

        except Exception as e:
            logger.error("Failed to initialize session: %s", str(e))
            # 使用临时会话ID作为fallback
            self.session_id = f"temp_{self.user_id}"

    async def _load_conversation_history(self):
        """加载对话历史到内存"""
        try:
            history_data = await self.memory_manager.get_conversation_history(
                self.user_id, limit=5, session_id=self.session_id
            )

            conversations = history_data.get("conversations", [])
            for conv in conversations:
                self.history.append({"role": "user", "content": conv["user_message"]})
                self.history.append({"role": "assistant", "content": conv["ai_response"]})

            logger.info("Loaded %d conversation rounds from history", len(conversations))

        except Exception as e:
            logger.error("Failed to load conversation history: %s", str(e))

    async def a_run(self, user_message: str) -> str:
        """
        异步处理用户消息，集成意图识别、对话管理和工具调用

        Args:
            user_message: 用户输入的文本消息

        Returns:
            AI的回复字符串
        """
        logger.info("Processing user message: %s", user_message[:50] + "..." if len(user_message) > 50 else user_message)

        # 确保会话已初始化
        if not self._session_initialized:
            await self._initialize_session()
            self._session_initialized = True

        try:
            # 1. 意图识别
            intent_result = await self.intent_parser.parse_intent(user_message)
            intent_type = intent_result.get("RequestType", IntentType.GENERAL_CHAT.value)
            confidence = intent_result.get("confidence", 0.0)

            logger.info("Intent identified: %s (confidence: %.2f)", intent_type, confidence)

            # 2. 添加用户消息到历史
            self.history.append({"role": "user", "content": user_message})

            # 3. 根据模式处理
            if self.demo_mode:
                ai_response = await self._demo_response_with_intent(user_message, intent_result)
            else:
                ai_response = await self._production_response(user_message, intent_result)

            # 4. 存储对话历史
            await self._store_conversation(user_message, ai_response, intent_type, confidence)

            # 5. 添加AI回复到历史
            self.history.append({"role": "assistant", "content": ai_response})

            logger.info("Response generated successfully")
            return ai_response

        except Exception as e:
            logger.error("Error in a_run: %s", str(e))
            error_response = f"抱歉，处理您的请求时出现了问题。错误信息：{str(e)}"

            # 即使出错也要存储对话
            try:
                await self._store_conversation(user_message, error_response, "error", 0.0)
            except:
                pass

            return error_response

    async def _production_response(self, user_message: str, intent_result: Dict[str, Any]) -> str:
        """生产模式下的响应处理"""
        try:
            # 获取工具定义
            tools = self.tools_registry.get_tools_schema()

            # 构建消息历史
            messages = self.history.copy()

            # 调用DeepSeek API
            response = self.deepseek_client.get_deepseek_response(
                messages=messages,
                tools=tools,
                model_name="deepseek-chat",
                temperature=0.7
            )

            # 处理工具调用
            if response.tool_calls:
                return await self._handle_tool_calls_v2(response.tool_calls, messages)
            else:
                return response.content

        except Exception as e:
            logger.error("Production response failed: %s", str(e))
            # 降级到演示模式
            return await self._demo_response_with_intent(user_message, intent_result)

    async def _store_conversation(
        self,
        user_message: str,
        ai_response: str,
        intent_type: str,
        confidence: float
    ):
        """存储对话到数据库"""
        try:
            success = await self.memory_manager.store_conversation(
                user_id=self.user_id,
                user_message=user_message,
                ai_response=ai_response,
                session_id=self.session_id,
                intent_type=intent_type,
                confidence=confidence
            )

            if success:
                logger.debug("Conversation stored successfully")
            else:
                logger.warning("Failed to store conversation")

        except Exception as e:
            logger.error("Error storing conversation: %s", str(e))

    async def _demo_response_with_intent(self, user_message: str, intent_result: Dict[str, Any]) -> str:
        """基于意图识别的演示模式响应"""
        intent_type = intent_result.get("RequestType", IntentType.GENERAL_CHAT.value)
        confidence = intent_result.get("confidence", 0.0)

        logger.info("Demo mode: Processing intent %s (confidence: %.2f)", intent_type, confidence)

        # 根据意图类型调用相应的工具
        try:
            if intent_type == IntentType.ACTIVITY_QUERY.value:
                result = await self.tools_registry.get_tool("get_user_activity_summary")(self.user_id, 7)
                return (f"根据您的活动数据分析: {result['message']} "
                       f"在演示模式下，我模拟调用了活动摘要工具。建议您每天保持适量运动，目标是每天8000-10000步。")

            elif intent_type == IntentType.SLEEP_ANALYSIS.value:
                result = await self.tools_registry.get_tool("analyze_sleep_quality")(self.user_id, "2024-06-01_to_2024-06-07")
                return (f"睡眠质量分析: {result['message']} "
                       f"在演示模式下，我模拟分析了您的睡眠数据。建议保持每晚7-8小时的优质睡眠。")

            elif intent_type == IntentType.GOAL_SETTING.value:
                demo_goals = {"daily_steps": 8000, "sleep_hours": 7.5, "exercise_minutes": 30}
                result = await self.tools_registry.get_tool("update_health_goals")(self.user_id, demo_goals)
                return (f"健康目标设置: {result['message']} "
                       f"在演示模式下，我帮您设置了示例健康目标：每天8000步、7.5小时睡眠、30分钟运动。")

            elif intent_type == IntentType.ACHIEVEMENT_CHECK.value:
                result = await self.tools_registry.get_tool("check_achievements")(self.user_id)
                achievement_info = result[0] if result and len(result) > 0 else {"message": "暂无成就数据"}
                achievement_text = achievement_info.get('achievement', achievement_info.get('message', '成就数据获取成功'))
                return (f"成就检查: {achievement_text} "
                       f"在演示模式下，我查看了您的成就进度。继续保持健康的生活方式！")

            elif intent_type == IntentType.HEALTH_INSIGHTS.value:
                result = await self.tools_registry.get_tool("get_health_insights")(self.user_id)
                return (f"健康洞察: {result[0]['insight']} "
                       f"在演示模式下，我生成了健康建议。建议您保持规律的作息，均衡饮食，适量运动。")

            elif intent_type == IntentType.NUTRITION_ANALYSIS.value:
                result = await self.tools_registry.get_tool("analyze_nutrition_intake")(self.user_id, "2024-06-08")
                return (f"营养分析: {result['message']} "
                       f"在演示模式下，我分析了您的营养摄入。建议保持均衡饮食，多吃蔬菜水果。")

            elif intent_type == IntentType.EXERCISE_PLAN.value:
                result = await self.tools_registry.get_tool("generate_exercise_plan")(
                    self.user_id, "weight_loss", "beginner", 4
                )
                return (f"运动计划: {result['message']} "
                       f"在演示模式下，我为您生成了个性化运动计划。请根据自身情况调整强度。")

            else:
                return (f"您好！我是AuraWell健康助手。当前运行在演示模式下。"
                       f"我识别到您的意图是：{intent_type}（置信度：{confidence:.2f}）。"
                       f"我可以帮您查看活动数据、分析睡眠质量、设置健康目标、检查成就进度，或提供健康洞察。"
                       f"\n\n（注意：要使用完整的AI功能，请在.env文件中设置DEEPSEEK_API_KEY）")

        except Exception as e:
            logger.error("Demo response error: %s", str(e))
            return (f"演示模式下处理您的请求时出现问题。意图：{intent_type}，错误：{str(e)}")

    async def _handle_tool_calls_v2(self, tool_calls: List[Dict], messages: List[Dict]) -> str:
        """处理工具调用（优化版本）"""
        tool_results = []

        for tool_call in tool_calls:
            try:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])

                # 确保user_id正确
                if 'user_id' in tool_args:
                    tool_args['user_id'] = self.user_id

                # 获取工具函数
                tool_function = self.tools_registry.get_tool(tool_name)
                if not tool_function:
                    logger.warning("Tool not found: %s", tool_name)
                    continue

                logger.info("Executing tool: %s with args: %s", tool_name, tool_args)

                # 执行工具
                result = await tool_function(**tool_args)

                # 添加工具结果
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })

            except Exception as e:
                logger.error("Tool execution failed: %s", str(e))
                tool_results.append({
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "role": "tool",
                    "name": tool_call.get("function", {}).get("name", "unknown"),
                    "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                })

        # 将工具结果添加到消息历史
        messages.extend(tool_results)

        # 获取最终回复
        try:
            final_response = self.deepseek_client.get_deepseek_response(
                messages=messages,
                model_name="deepseek-chat",
                temperature=0.7
            )
            return final_response.content

        except Exception as e:
            logger.error("Failed to get final response: %s", str(e))
            return "工具调用执行完成，但获取最终回复时出错。"

    async def get_session_info(self) -> Dict[str, Any]:
        """获取当前会话信息"""
        try:
            session_context = await self.session_manager.get_session_context(self.session_id)
            history_data = await self.memory_manager.get_conversation_history(
                self.user_id, limit=10, session_id=self.session_id
            )

            return {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "demo_mode": self.demo_mode,
                "session_context": session_context,
                "conversation_count": history_data.get("total_conversations", 0),
                "last_activity": session_context.get("last_activity"),
                "session_expires": session_context.get("expires_at")
            }

        except Exception as e:
            logger.error("Failed to get session info: %s", str(e))
            return {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "demo_mode": self.demo_mode,
                "error": str(e)
            }

    async def cleanup_session(self):
        """清理会话资源"""
        try:
            # 清理过期会话
            await self.session_manager.cleanup_expired_sessions()
            logger.info("Session cleanup completed")

        except Exception as e:
            logger.error("Session cleanup failed: %s", str(e))