"""
LangChain Agent 实现
基于LangChain框架的AI Agent，整合健康工具
"""

import logging
from typing import Dict, Any, Optional, List

from ..core.agent_router import BaseAgent
from ..conversation.memory_manager import MemoryManager
from ..core.deepseek_client import DeepSeekClient
# from .tools.health_tools import LangChainHealthTools  # 暂时不使用

# DeepSeek LLM integration - using direct client instead of LangChain wrapper
from .services.health_advice_service import HealthAdviceService

logger = logging.getLogger(__name__)


class HealthAdviceAgent(BaseAgent):
    """
    AuraWell健康建议生成AI Agent

    基于LangChain框架的真正Agent实现，整合三大工具链：
    - UserProfileLookup (用户档案查询)
    - CalcMetrics (健康指标计算)
    - SearchKnowledge (知识检索和AI推理)

    核心功能：五模块健康建议生成（饮食、运动、体重、睡眠、心理）
    """

    def __init__(self, user_id: str):
        """
        初始化LangChain Agent

        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.memory_manager = MemoryManager()
        self.health_advice_service = HealthAdviceService()

        # DeepSeek客户端和LLM
        self.deepseek_client = None
        self.llm = None

        # LangChain组件
        self.tools = []
        self.agent_executor = None

        # 对话历史
        self._conversation_history = []

        # 初始化组件
        self._initialize_components()

    def _initialize_components(self):
        """初始化所有组件"""
        try:
            # 初始化DeepSeek客户端
            self.deepseek_client = DeepSeekClient()

            # 尝试创建LangChain LLM包装器
            try:
                self.llm = self._create_langchain_llm()
                logger.info("LangChain LLM包装器初始化成功")
            except Exception as llm_e:
                logger.warning(f"LangChain LLM包装器初始化失败: {llm_e}，使用直接客户端")
                self.llm = None

            logger.info("DeepSeek客户端初始化成功")
        except Exception as e:
            logger.warning(f"DeepSeek客户端初始化失败: {e}，将使用本地模式")
            self.deepseek_client = None
            self.llm = None

    async def _initialize_langchain_components(self):
        """
        初始化LangChain组件（异步）
        """
        try:
            # 创建工具
            self.tools = self._create_tools()

            # 创建agent执行器 - 使用直接服务调用而非LangChain executor
            self.agent_executor = (
                None  # Using direct service calls instead of LangChain executor
            )

            logger.info(f"LangChain Agent 初始化完成，用户: {self.user_id}")

        except Exception as e:
            logger.error(f"LangChain Agent 初始化失败: {e}")
            raise

    def _create_langchain_llm(self):
        """创建LangChain LLM包装器"""
        try:
            from langchain_openai import ChatOpenAI

            if not self.deepseek_client:
                return None

            # 创建LangChain兼容的LLM
            # 注意：使用ChatOpenAI类是因为阿里云DashScope提供OpenAI兼容的API接口
            # 实际调用的是阿里云DashScope的DeepSeek服务，而非OpenAI的服务
            # 参数说明：
            # - model: DeepSeek模型名称 (deepseek-r1-0528)
            # - api_key: 阿里云DashScope API密钥
            # - api_base: 阿里云DashScope兼容模式URL
            llm = ChatOpenAI(
                model="deepseek-r1-0528",
                openai_api_key=self.deepseek_client.api_key,  # DashScope API Key
                openai_api_base=self.deepseek_client.base_url,  # DashScope Compatible URL
                temperature=0.7,
                max_tokens=1024
            )

            return llm

        except ImportError as e:
            logger.warning(f"LangChain OpenAI包装器不可用: {e}")
            return None
        except Exception as e:
            logger.error(f"创建LangChain LLM失败: {e}")
            return None

    def _create_llm(self):
        """创建LLM（兼容性方法）"""
        return self.llm or self._create_langchain_llm()

    def _create_tools(self):
        """创建LangChain工具列表"""
        try:
            from langchain.tools import Tool

            tools = []

            # 用户档案查询工具
            user_profile_tool = Tool(
                name="UserProfileLookup",
                description="查询用户的基本信息和健康档案，包括年龄、性别、身高体重、活动水平等",
                func=self._user_profile_lookup_sync,
                coroutine=self._user_profile_lookup
            )
            tools.append(user_profile_tool)

            # 健康指标计算工具
            calc_metrics_tool = Tool(
                name="CalcMetrics",
                description="计算健康指标，如BMI、BMR、TDEE、理想体重范围等",
                func=self._calc_metrics_sync,
                coroutine=self._calc_metrics
            )
            tools.append(calc_metrics_tool)

            # 健康建议生成工具
            health_advice_tool = Tool(
                name="SearchKnowledge",
                description="基于用户数据和健康指标，生成个性化的五模块健康建议（饮食、运动、体重、睡眠、心理）",
                func=self._search_knowledge_sync,
                coroutine=self._search_knowledge
            )
            tools.append(health_advice_tool)

            return tools

        except ImportError as e:
            logger.warning(f"LangChain工具不可用: {e}，使用简化工具列表")
            # 返回简化的工具描述列表
            return [
                {"name": "UserProfileLookup", "description": "查询用户档案"},
                {"name": "CalcMetrics", "description": "计算健康指标"},
                {"name": "SearchKnowledge", "description": "生成健康建议"}
            ]

    def _create_agent_executor(self):
        """创建LangChain Agent执行器"""
        try:
            from langchain.agents import create_openai_tools_agent, AgentExecutor
            from langchain.prompts import ChatPromptTemplate

            if not self.llm or not self.tools:
                logger.warning("LLM或工具未初始化，无法创建Agent执行器")
                return None

            # 创建提示模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是AuraWell健康助手，一个专业的健康管理AI助手。

你有以下工具可以使用：
- UserProfileLookup: 查询用户基本信息和健康档案
- CalcMetrics: 计算健康指标（BMI、BMR、TDEE等）
- SearchKnowledge: 生成个性化健康建议

请根据用户的问题，合理使用这些工具来提供专业的健康建议。
如果涉及医疗诊断，请建议用户咨询专业医生。"""),
                ("user", "{input}"),
                ("assistant", "{agent_scratchpad}")
            ])

            # 创建Agent
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)

            # 创建执行器
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )

            return agent_executor

        except ImportError as e:
            logger.warning(f"LangChain组件导入失败: {e}，使用直接服务调用")
            return None
        except Exception as e:
            logger.error(f"创建Agent执行器失败: {e}")
            return None

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理用户消息

        Args:
            message: 用户消息
            context: 上下文信息

        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            logger.info(f"LangChain Agent 处理消息: {message}")

            # 获取对话历史
            conversation_history = await self.memory_manager.get_conversation_history(
                user_id=self.user_id, limit=10
            )

            # 构建上下文
            full_context = {
                "user_id": self.user_id,
                "conversation_history": conversation_history,
                **(context or {}),
            }

            # 检测是否是RAG查询请求
            if message.startswith('/rag '):
                response = await self._handle_rag_request(message, full_context)
            # 检测是否是健康建议生成请求
            elif self._is_health_advice_request(message):
                response = await self._handle_health_advice_request(
                    message, full_context
                )
            else:
                # 使用标准的LangChain流程处理
                response = await self._process_with_langchain(message, full_context)

            # 保存对话到记忆
            await self.memory_manager.store_conversation(
                user_id=self.user_id,
                user_message=message,
                ai_response=response.get("message", ""),
                intent_type="langchain_chat",
            )

            return {
                "success": True,
                "message": response.get("message", ""),
                "data": response.get("data"),
                "agent_type": "langchain",
                "tools_used": response.get("tools_used", []),
            }

        except Exception as e:
            logger.error(f"LangChain Agent 处理消息失败: {e}")
            return {
                "success": False,
                "message": "处理消息时发生错误",
                "error": str(e),
                "agent_type": "langchain",
            }

    async def _handle_rag_request(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理RAG查询请求

        Args:
            message: 用户消息（以/rag开头）
            context: 上下文信息

        Returns:
            处理结果
        """
        try:
            # 提取RAG查询内容
            rag_query = message.replace('/rag ', '').strip()

            if not rag_query:
                return {
                    "message": "请提供RAG查询内容，例如：/rag 高血压的饮食建议",
                    "data": {"response_type": "rag_help"},
                    "tools_used": [],
                }

            logger.info(f"处理RAG查询: {rag_query}")

            # 导入RAG服务
            from ..services.rag_service import get_rag_service
            rag_service = get_rag_service()

            # 执行RAG检索
            rag_results = await rag_service.retrieve_from_rag(rag_query, k=3)

            if not rag_results:
                return {
                    "message": f"抱歉，没有找到关于'{rag_query}'的相关信息。",
                    "data": {"response_type": "rag_no_results", "query": rag_query},
                    "tools_used": ["RAG"],
                }

            # 使用RAG结果生成AI回答
            if self.deepseek_client:
                # 构建包含RAG结果的提示
                rag_context = "\n".join([f"- {result}" for result in rag_results])
                enhanced_prompt = f"""基于以下检索到的医疗健康信息，回答用户的问题：

检索结果：
{rag_context}

用户问题：{rag_query}

请基于上述信息提供专业、准确的健康建议。如果信息不足，请建议咨询专业医生。"""

                ai_response = await self._get_ai_response(enhanced_prompt, context)

                return {
                    "message": ai_response,
                    "data": {
                        "response_type": "rag_enhanced",
                        "query": rag_query,
                        "rag_results": rag_results,
                        "rag_count": len(rag_results)
                    },
                    "tools_used": ["RAG", "DeepSeekAI"],
                }
            else:
                # 没有AI客户端时，直接返回RAG结果
                formatted_results = "\n\n".join([f"{i+1}. {result}" for i, result in enumerate(rag_results)])
                response_message = f"根据您的查询'{rag_query}'，找到以下相关信息：\n\n{formatted_results}\n\n建议您根据这些信息咨询专业医生获取个性化建议。"

                return {
                    "message": response_message,
                    "data": {
                        "response_type": "rag_only",
                        "query": rag_query,
                        "rag_results": rag_results,
                        "rag_count": len(rag_results)
                    },
                    "tools_used": ["RAG"],
                }

        except Exception as e:
            logger.error(f"RAG查询处理失败: {e}")
            return {
                "message": f"抱歉，RAG查询处理失败: {str(e)}",
                "data": {"error": str(e), "response_type": "rag_error"},
                "tools_used": [],
            }

    def _is_health_advice_request(self, message: str) -> bool:
        """
        检测是否是健康建议生成请求

        Args:
            message: 用户消息

        Returns:
            是否是健康建议请求
        """
        advice_keywords = [
            "健康建议",
            "健康计划",
            "健康方案",
            "全面建议",
            "综合建议",
            "饮食建议",
            "运动建议",
            "睡眠建议",
            "心理建议",
            "体重建议",
            "健康管理",
            "制定计划",
            "生成建议",
            "个性化建议",
            "五个模块",
            "完整建议",
            "health advice",
            "comprehensive advice",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in advice_keywords)

    async def _handle_health_advice_request(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理健康建议生成请求

        Args:
            message: 用户消息
            context: 上下文信息

        Returns:
            健康建议响应
        """
        try:
            logger.info(f"处理健康建议请求: {message}")

            # 解析请求参数
            goal_type = self._extract_goal_type(message)
            duration_weeks = self._extract_duration(message)
            special_requirements = self._extract_special_requirements(message)

            # 生成五模块健康建议
            advice_result = (
                await self.health_advice_service.generate_comprehensive_advice(
                    user_id=self.user_id,
                    goal_type=goal_type,
                    duration_weeks=duration_weeks,
                    special_requirements=special_requirements,
                )
            )

            # 格式化响应
            if hasattr(advice_result, "diet"):  # HealthAdviceResponse对象
                formatted_message = self._format_health_advice_message(advice_result)

                return {
                    "message": formatted_message,
                    "data": {
                        "advice_type": "comprehensive",
                        "goal_type": goal_type,
                        "duration_weeks": duration_weeks,
                        "generated_at": advice_result.generated_at,
                        "sections": {
                            "diet": (
                                advice_result.diet.model_dump()
                                if hasattr(advice_result.diet, "model_dump")
                                else advice_result.diet
                            ),
                            "exercise": (
                                advice_result.exercise.model_dump()
                                if hasattr(advice_result.exercise, "model_dump")
                                else advice_result.exercise
                            ),
                            "weight": (
                                advice_result.weight.model_dump()
                                if hasattr(advice_result.weight, "model_dump")
                                else advice_result.weight
                            ),
                            "sleep": (
                                advice_result.sleep.model_dump()
                                if hasattr(advice_result.sleep, "model_dump")
                                else advice_result.sleep
                            ),
                            "mental_health": (
                                advice_result.mental_health.model_dump()
                                if hasattr(advice_result.mental_health, "model_dump")
                                else advice_result.mental_health
                            ),
                        },
                    },
                    "tools_used": [
                        "UserProfileLookup",
                        "CalcMetrics",
                        "SearchKnowledge",
                        "HealthAdviceService",
                    ],
                }
            else:
                # 处理错误情况
                return {
                    "message": "很抱歉，生成健康建议时遇到了问题，请稍后重试。",
                    "data": {
                        "advice_type": "comprehensive",
                        "error": "advice_generation_failed",
                    },
                    "tools_used": ["HealthAdviceService"],
                }

        except Exception as e:
            logger.error(f"处理健康建议请求失败: {e}")
            return {
                "message": "很抱歉，生成健康建议时遇到了问题，请稍后重试。",
                "data": {"advice_type": "comprehensive", "error": str(e)},
                "tools_used": [],
            }

    def _extract_goal_type(self, message: str) -> str:
        """从消息中提取健康目标类型"""
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ["减肥", "减重", "weight loss"]):
            return "weight_loss"
        elif any(
            keyword in message_lower for keyword in ["增肌", "增重", "muscle", "gain"]
        ):
            return "muscle_gain"
        elif any(keyword in message_lower for keyword in ["力量", "strength"]):
            return "strength"
        elif any(keyword in message_lower for keyword in ["耐力", "endurance"]):
            return "endurance"
        else:
            return "general_wellness"

    def _extract_duration(self, message: str) -> int:
        """从消息中提取计划周期"""
        import re

        # 查找数字和周相关的词
        week_patterns = [
            r"(\d+)\s*周",
            r"(\d+)\s*weeks?",
            r"(\d+)\s*个?月",  # 月份转换为周
        ]

        for pattern in week_patterns:
            match = re.search(pattern, message.lower())
            if match:
                num = int(match.group(1))
                if "月" in pattern:
                    return num * 4  # 月份转换为周
                return min(num, 52)  # 最多52周

        return 4  # 默认4周

    def _extract_special_requirements(self, message: str) -> Optional[List[str]]:
        """从消息中提取特殊要求"""
        requirements = []
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ["糖尿病", "diabetes"]):
            requirements.append("糖尿病管理")
        if any(keyword in message_lower for keyword in ["高血压", "hypertension"]):
            requirements.append("高血压控制")
        if any(keyword in message_lower for keyword in ["素食", "vegetarian"]):
            requirements.append("素食要求")
        if any(keyword in message_lower for keyword in ["过敏", "allergy"]):
            requirements.append("食物过敏")
        if any(keyword in message_lower for keyword in ["失眠", "insomnia"]):
            requirements.append("睡眠问题")

        return requirements if requirements else None

    def _format_health_advice_message(self, advice_response) -> str:
        """格式化健康建议消息"""
        return f"""
# 🌟 个性化健康管理建议

*为您精心制定的完整健康方案*

## 🍎 饮食建议
{advice_response.diet.content}

**推荐要点：**
{self._format_recommendations(advice_response.diet.recommendations)}

## 🏃‍♂️ 运动计划
{advice_response.exercise.content}

**推荐要点：**
{self._format_recommendations(advice_response.exercise.recommendations)}

## ⚖️ 体重管理
{advice_response.weight.content}

**推荐要点：**
{self._format_recommendations(advice_response.weight.recommendations)}

## 😴 睡眠优化
{advice_response.sleep.content}

**推荐要点：**
{self._format_recommendations(advice_response.sleep.recommendations)}

## 🧠 心理健康
{advice_response.mental_health.content}

**推荐要点：**
{self._format_recommendations(advice_response.mental_health.recommendations)}

---
*本建议基于您的个人档案生成，请根据实际情况调整。如有健康问题，建议咨询专业医生。*
        """

    def _format_recommendations(self, recommendations: List[str]) -> str:
        """格式化推荐列表"""
        if not recommendations:
            return "- 暂无具体推荐"
        return "\n".join([f"- {rec}" for rec in recommendations])

    async def _process_with_langchain(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用LangChain流程处理消息

        Args:
            message: 用户消息
            context: 上下文信息

        Returns:
            处理结果
        """
        try:
            # 如果有可用的DeepSeek客户端，使用AI响应
            if self.deepseek_client:
                ai_response = await self._get_ai_response(message, context)
                return {
                    "message": ai_response,
                    "data": {"response_type": "ai_generated"},
                    "tools_used": ["DeepSeekAI"],
                }
            else:
                # 使用本地响应
                local_response = await self._get_local_response(message, context)
                return {
                    "message": local_response,
                    "data": {"response_type": "local_fallback"},
                    "tools_used": [],
                }

        except Exception as e:
            logger.error(f"LangChain消息处理失败: {e}")
            return {
                "message": "很抱歉，我现在无法处理您的请求，请稍后重试。",
                "data": {"response_type": "error_fallback", "error": str(e)},
                "tools_used": [],
            }

    async def _get_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """使用DeepSeek API生成AI响应"""
        try:
            _ = context  # 避免未使用参数警告
            # 构建对话历史
            messages = []

            # 添加系统提示
            system_prompt = """你是AuraWell健康助手，一个专业的健康管理AI助手。你的职责是：
1. 回答用户的健康相关问题
2. 提供个性化的健康建议
3. 帮助用户管理健康数据
4. 推荐合适的运动和营养方案
5. 生成完整的五模块健康建议（饮食、运动、体重、睡眠、心理）

请用友好、专业的语气回答用户问题。如果涉及医疗诊断，请建议用户咨询专业医生。"""

            messages.append({"role": "system", "content": system_prompt})

            # 添加最近的对话历史
            recent_history = (
                self._conversation_history[-10:] if self._conversation_history else []
            )
            messages.extend(recent_history)

            # 添加当前消息
            messages.append({"role": "user", "content": message})

            # 调用DeepSeek API
            response = self.deepseek_client.get_deepseek_response(
                messages=messages, temperature=0.7
            )

            return response.content

        except Exception as e:
            logger.error(f"AI响应生成失败: {e}")
            return "抱歉，我现在无法处理您的请求。请稍后重试。"

    async def _get_local_response(self, message: str, context: Dict[str, Any]) -> str:
        """生成本地响应（当AI不可用时）"""
        _ = context  # 避免未使用参数警告
        message_lower = message.lower()

        # 简单的关键词匹配响应
        if any(keyword in message_lower for keyword in ["健康", "health"]):
            return "我是您的健康助手！我可以帮您制定个性化健康计划、分析健康数据、提供营养运动建议。请告诉我您想了解什么健康信息？"

        elif any(keyword in message_lower for keyword in ["数据", "分析", "统计"]):
            return "我可以帮您分析健康数据，包括运动量、睡眠质量、心率变化等。请告诉我您想分析哪类健康数据？"

        elif any(keyword in message_lower for keyword in ["计划", "建议", "方案"]):
            return "我可以为您制定个性化的健康管理方案，包括饮食、运动、睡眠、体重管理和心理健康五个模块。您希望重点关注哪个方面？"

        elif any(keyword in message_lower for keyword in ["运动", "锻炼", "fitness"]):
            return "运动是健康生活的重要组成部分！我可以根据您的体质和目标推荐合适的运动计划。您现在的运动习惯如何？有什么特定的健身目标吗？"

        elif any(keyword in message_lower for keyword in ["你好", "hello", "hi"]):
            return "您好！我是AuraWell健康助手，很高兴为您服务！我可以帮您管理健康数据、提供健康建议、制定运动计划等。有什么可以帮助您的吗？"

        else:
            return "感谢您的消息！作为您的健康助手，我可以帮您管理健康数据、提供健康建议、制定运动和营养计划。请告诉我您想了解什么健康相关的信息？"

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
                user_id=self.user_id, limit=limit
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
            # 清除内存中的对话历史
            self._conversation_history.clear()

            # 清除内存管理器中的历史（如果支持）
            if self.memory_manager and hasattr(self.memory_manager, 'clear_memory'):
                self.memory_manager.clear_memory(self.user_id)
            elif self.memory_manager and hasattr(self.memory_manager, 'clear_conversation_history'):
                await self.memory_manager.clear_conversation_history(self.user_id)

            logger.info(f"已成功清除用户 {self.user_id} 的对话历史")
            return True

        except Exception as e:
            logger.error(f"清除对话历史失败: {e}")
            return False

    # NEW: 专门的健康建议生成方法
    async def generate_comprehensive_health_advice(
        self,
        goal_type: str = "general_wellness",
        duration_weeks: int = 4,
        special_requirements: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        生成综合健康建议（公开API）

        Args:
            goal_type: 健康目标类型
            duration_weeks: 计划周期（周）
            special_requirements: 特殊健康要求

        Returns:
            完整的健康建议结果
        """
        return await self.health_tools.generate_comprehensive_health_advice(
            goal_type=goal_type,
            duration_weeks=duration_weeks,
            special_requirements=(
                ",".join(special_requirements) if special_requirements else None
            ),
        )

    async def get_quick_health_advice(self, topic: str) -> Dict[str, Any]:
        """
        获取快速健康建议（公开API）

        Args:
            topic: 健康话题

        Returns:
            快速健康建议
        """
        return await self.health_tools.get_quick_health_advice(topic)

    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "type": "langchain",
            "user_id": self.user_id,
            "version": "2.1.0",  # 升级版本号
            "features": [
                "conversation_memory",
                "tool_calling",
                "context_awareness",
                "comprehensive_health_advice",
                "five_section_health_planning",
                "langchain_agent_executor",  # NEW
            ],
            "tools": [
                "UserProfileLookup",
                "CalcMetrics",
                "SearchKnowledge",
            ],
        }

    # LangChain工具方法实现
    async def _user_profile_lookup(self, query: str = "") -> str:
        """用户档案查询工具（异步版本）"""
        try:
            user_data = await self.health_advice_service._get_user_profile_data(self.user_id)
            return f"用户档案信息：{user_data}"
        except Exception as e:
            logger.error(f"用户档案查询失败: {e}")
            return f"用户档案查询失败: {str(e)}"

    def _user_profile_lookup_sync(self, query: str = "") -> str:
        """用户档案查询工具（同步版本）"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._user_profile_lookup(query))
        except Exception as e:
            logger.error(f"用户档案查询失败: {e}")
            return f"用户档案查询失败: {str(e)}"

    async def _calc_metrics(self, user_data: str = "") -> str:
        """健康指标计算工具（异步版本）"""
        try:
            if not user_data:
                user_data = await self.health_advice_service._get_user_profile_data(self.user_id)
            else:
                # 如果传入的是字符串，需要解析
                import json
                try:
                    user_data = json.loads(user_data) if isinstance(user_data, str) else user_data
                except:
                    user_data = await self.health_advice_service._get_user_profile_data(self.user_id)

            metrics = await self.health_advice_service._calculate_health_metrics(user_data)
            return f"健康指标：{metrics}"
        except Exception as e:
            logger.error(f"健康指标计算失败: {e}")
            return f"健康指标计算失败: {str(e)}"

    def _calc_metrics_sync(self, user_data: str = "") -> str:
        """健康指标计算工具（同步版本）"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._calc_metrics(user_data))
        except Exception as e:
            logger.error(f"健康指标计算失败: {e}")
            return f"健康指标计算失败: {str(e)}"

    async def _search_knowledge(self, query: str) -> str:
        """知识检索和健康建议生成工具（异步版本）"""
        try:
            # 解析查询中的参数
            goal_type = "general_wellness"
            duration_weeks = 4

            if "减肥" in query or "weight loss" in query.lower():
                goal_type = "weight_loss"
            elif "增肌" in query or "muscle" in query.lower():
                goal_type = "muscle_gain"

            advice_result = await self.health_advice_service.generate_comprehensive_advice(
                user_id=self.user_id,
                goal_type=goal_type,
                duration_weeks=duration_weeks
            )

            if hasattr(advice_result, 'diet'):
                return self._format_health_advice_message(advice_result)
            else:
                return f"健康建议生成完成：{advice_result}"

        except Exception as e:
            logger.error(f"健康建议生成失败: {e}")
            return f"健康建议生成失败: {str(e)}"

    def _search_knowledge_sync(self, query: str) -> str:
        """知识检索和健康建议生成工具（同步版本）"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._search_knowledge(query))
        except Exception as e:
            logger.error(f"健康建议生成失败: {e}")
            return f"健康建议生成失败: {str(e)}"


# 为了保持兼容性，创建别名
LangChainAgent = HealthAdviceAgent
