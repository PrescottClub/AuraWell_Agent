"""
Health Advice Service - Core AI Service for Personalized Health Recommendations

Integrates the three main tool chains:
1. UserProfileLookup (via UserRepository)
2. CalcMetrics (via health_calculations utilities)
3. SearchKnowledge (via DeepSeek client and memory)

Generates comprehensive health advice with five modules:
饮食 (Diet), 运动 (Exercise), 体重 (Weight), 睡眠 (Sleep), 心理 (Mental Health)
"""

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator

# Core imports
from ...database import get_database_manager
from ...repositories.user_repository import UserRepository
from ...repositories.health_data_repository import HealthDataRepository
from ...core.deepseek_client import DeepSeekClient
from ...utils.health_calculations import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    get_bmi_category,
    calculate_ideal_weight_range,
    calculate_calorie_goal,
)

# from ...models.user_profile import UserProfile  # Not used in current implementation
from ...models.enums import Gender, ActivityLevel, HealthGoal, BMICategory

# Service imports
from .parsers import FiveSectionParser, HealthAdviceResponse
from ...core.exceptions import (
    AurawellException,
    ExternalServiceError,
    BusinessLogicError,
    NotFoundError,
)

logger = logging.getLogger(__name__)

# 模型选择配置
MODEL_CONFIG = {
    "reasoning_tasks": "deepseek-reasoner",  # 复杂推理任务
    "chat_tasks": "deepseek-chat",          # 简单对话任务
    "default": "deepseek-reasoner"          # 默认使用推理模型
}


class HealthAdviceService:
    """
    Core service for generating comprehensive health advice using LangChain framework.

    Integrates three main tool chains:
    - UserProfileLookup: User data retrieval and profiling
    - CalcMetrics: Health metrics calculation (BMI, BMR, TDEE, etc.)
    - SearchKnowledge: AI-powered knowledge retrieval and reasoning
    """

    def __init__(self):
        """Initialize the health advice service"""
        self.parser = FiveSectionParser()
        self.deepseek_client = None
        self.logger = logger

        # Initialize DeepSeek client
        try:
            self.deepseek_client = DeepSeekClient()
            self.logger.info("HealthAdviceService initialized with DeepSeek client")
        except Exception as e:
            self.logger.warning(
                f"DeepSeek client not available: {e}. Using fallback mode."
            )

    async def generate_comprehensive_advice(
        self,
        user_id: str,
        goal_type: Optional[str] = None,
        duration_weeks: int = 4,
        special_requirements: Optional[List[str]] = None,
    ) -> HealthAdviceResponse:
        """
        Generate comprehensive health advice for a user

        Args:
            user_id: User identifier
            goal_type: Specific health goal (weight_loss, muscle_gain, etc.)
            duration_weeks: Planning duration in weeks
            special_requirements: Special health requirements or constraints

        Returns:
            HealthAdviceResponse: Structured health advice with all five modules
        """
        try:
            self.logger.info(
                f"Generating comprehensive health advice for user: {user_id}"
            )

            # Step 1: UserProfileLookup - Get user data
            user_data = await self._get_user_profile_data(user_id)

            # Step 2: CalcMetrics - Calculate health metrics
            health_metrics = await self._calculate_health_metrics(user_data)

            # Step 3: SearchKnowledge - AI-powered advice generation
            advice_content = await self._generate_ai_advice(
                user_data,
                health_metrics,
                goal_type,
                duration_weeks,
                special_requirements,
            )

            # Step 4: Parse and validate output structure
            parsed_advice = await self._parse_and_validate_advice(
                advice_content, user_id, user_data, health_metrics
            )

            self.logger.info(
                f"Successfully generated health advice for user: {user_id}"
            )
            return parsed_advice

        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            self.logger.error(f"Error generating health advice for user {user_id}: {e}")
            raise BusinessLogicError(f"Failed to generate health advice: {str(e)}")

    async def get_streaming_advice(self, advice_request) -> AsyncGenerator[str, None]:
        """
        Generate streaming health advice for WebSocket connections

        Args:
            advice_request: HealthAdviceRequest object containing user query and context

        Yields:
            str: Token chunks from the AI response
        """
        try:
            # Extract user_id from advice_request (could be user_id or active_member_id)
            user_id = getattr(advice_request, "user_id", None) or getattr(
                advice_request, "active_member_id", "unknown_user"
            )
            self.logger.info(f"Generating streaming health advice for user: {user_id}")

            # Get user data and health metrics
            user_data = await self._get_user_profile_data(user_id)
            health_metrics = await self._calculate_health_metrics(user_data)

            # Build AI prompt based on user query
            prompt = self._build_streaming_prompt(
                advice_request, user_data, health_metrics
            )

            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt},
            ]

            # Stream response from DeepSeek
            if self.deepseek_client:
                async for token in self.deepseek_client.get_streaming_response(
                    messages=messages,
                    model_name="deepseek-reasoner",
                    temperature=0.3,
                    max_tokens=2048,
                ):
                    yield token
            else:
                # Fallback for when DeepSeek is not available
                fallback_response = await self._generate_fallback_streaming_response(
                    advice_request
                )
                for token in fallback_response:
                    yield token

        except Exception as e:
            self.logger.error(f"Error generating streaming advice: {e}")
            yield f"抱歉，生成健康建议时发生错误：{str(e)}"

    async def _get_user_profile_data(self, user_id: str) -> Dict[str, Any]:
        """
        Tool Chain 1: UserProfileLookup
        Retrieve comprehensive user profile data
        """
        try:
            db_manager = get_database_manager()
            async with db_manager.get_session() as session:
                user_repo = UserRepository(session)
                health_repo = HealthDataRepository(session)

                # Get user profile
                user_profile = await user_repo.get_user_by_id(user_id)
                if not user_profile:
                    raise NotFoundError(
                        f"User {user_id} not found", resource_type="user"
                    )

                # Get recent activity data
                end_date = date.today()
                start_date = end_date - timedelta(days=30)

                activity_data = await health_repo.get_activity_summaries(
                    user_id=user_id, start_date=start_date, end_date=end_date
                )

                # Get recent sleep data
                sleep_data = await health_repo.get_sleep_sessions(
                    user_id=user_id, start_date=start_date, end_date=end_date
                )

                return {
                    "profile": user_profile,
                    "activity_data": activity_data or [],
                    "sleep_data": sleep_data or [],
                    "user_id": user_id,
                }

        except Exception as e:
            self.logger.error(f"Error retrieving user profile data: {e}")
            # Return mock data for testing
            return {
                "profile": self._get_mock_user_profile(user_id),
                "activity_data": [],
                "sleep_data": [],
                "user_id": user_id,
            }

    async def _calculate_health_metrics(
        self, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tool Chain 2: CalcMetrics
        Calculate comprehensive health metrics
        """
        try:
            profile = user_data["profile"]

            metrics = {}

            # Basic metrics
            if hasattr(profile, "weight_kg") and hasattr(profile, "height_cm"):
                weight = profile.weight_kg or 70.0  # Default weight
                height = profile.height_cm or 170.0  # Default height
                age = profile.age or 30  # Default age
                gender = getattr(profile, "gender", Gender.MALE)
                activity_level = getattr(
                    profile, "activity_level", ActivityLevel.MODERATELY_ACTIVE
                )

                # BMI calculation
                bmi = calculate_bmi(weight, height)
                bmi_category = get_bmi_category(bmi)

                # BMR and TDEE calculation
                bmr = calculate_bmr(weight, height, age, gender)
                tdee = calculate_tdee(bmr, activity_level)

                # Ideal weight range
                ideal_weight_min, ideal_weight_max = calculate_ideal_weight_range(
                    height, gender
                )

                metrics = {
                    "bmi": round(bmi, 1),
                    "bmi_category": bmi_category,
                    "bmr": round(bmr, 0),
                    "tdee": round(tdee, 0),
                    "current_weight": weight,
                    "height": height,
                    "ideal_weight_range": (ideal_weight_min, ideal_weight_max),
                    "age": age,
                    "gender": gender.value if hasattr(gender, "value") else str(gender),
                    "activity_level": (
                        activity_level.value
                        if hasattr(activity_level, "value")
                        else str(activity_level)
                    ),
                }

                # Calculate calorie goals for different objectives
                for goal in [
                    HealthGoal.WEIGHT_LOSS,
                    HealthGoal.WEIGHT_GAIN,
                    HealthGoal.GENERAL_WELLNESS,
                ]:
                    goal_calories = calculate_calorie_goal(tdee, goal)
                    metrics[f"calories_{goal.value.lower()}"] = goal_calories

            else:
                # Mock metrics for testing
                metrics = {
                    "bmi": 22.5,
                    "bmi_category": BMICategory.NORMAL,
                    "bmr": 1650,
                    "tdee": 2200,
                    "current_weight": 70.0,
                    "height": 170.0,
                    "ideal_weight_range": (53.5, 72.3),
                    "age": 30,
                    "gender": "male",
                    "activity_level": "moderately_active",
                }

            self.logger.info(f"Calculated health metrics: {metrics}")
            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating health metrics: {e}")
            return {}

    async def _generate_ai_advice(
        self,
        user_data: Dict[str, Any],
        health_metrics: Dict[str, Any],
        goal_type: Optional[str],
        duration_weeks: int,
        special_requirements: Optional[List[str]],
    ) -> str:
        """
        Tool Chain 3: SearchKnowledge
        Use DeepSeek AI to generate personalized health advice
        """
        try:
            if not self.deepseek_client:
                self.logger.warning(
                    "DeepSeek client not available, using local advice generation"
                )
                return await self._generate_local_advice(
                    user_data, health_metrics, goal_type
                )

            # Construct comprehensive prompt
            prompt = self._build_health_advice_prompt(
                user_data,
                health_metrics,
                goal_type,
                duration_weeks,
                special_requirements,
            )

            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt},
            ]

            # 使用重试机制调用API
            response_content = await self._call_deepseek_with_retry(
                messages=messages,
                model_name=MODEL_CONFIG["reasoning_tasks"],
                temperature=0.3,
                max_tokens=2048,
            )

            return response_content

        except ExternalServiceError:
            # Re-raise external service errors
            raise
        except Exception as e:
            self.logger.error(f"Error generating AI advice: {e}")
            # Fallback to local advice generation
            try:
                return await self._generate_local_advice(
                    user_data, health_metrics, goal_type
                )
            except Exception as fallback_error:
                self.logger.error(
                    f"Fallback advice generation also failed: {fallback_error}"
                )
                raise ExternalServiceError(
                    f"AI advice generation failed: {str(e)}", service_name="deepseek"
                )

    def _build_health_advice_prompt(
        self,
        user_data: Dict[str, Any],
        health_metrics: Dict[str, Any],
        goal_type: Optional[str],
        duration_weeks: int,
        special_requirements: Optional[List[str]],
    ) -> str:
        """Build comprehensive prompt for health advice generation"""

        # Note: profile is available but not directly used in current prompt template
        # profile = user_data.get("profile", {})

        prompt = f"""
请基于以下用户信息，生成一份完整的个性化健康管理建议。必须包含以下五个模块，每个模块都要详细且实用：

用户基本信息：
- 年龄：{health_metrics.get('age', '未知')}岁
- 性别：{health_metrics.get('gender', '未知')}
- 身高：{health_metrics.get('height', 0)}cm
- 体重：{health_metrics.get('current_weight', 0)}kg
- BMI：{health_metrics.get('bmi', 0)} ({health_metrics.get('bmi_category', '未知')})
- 基础代谢率：{health_metrics.get('bmr', 0)}卡路里/天
- 总消耗：{health_metrics.get('tdee', 0)}卡路里/天
- 活动水平：{health_metrics.get('activity_level', '中等活跃')}

健康目标：{goal_type or '整体健康改善'}
计划周期：{duration_weeks}周
特殊要求：{', '.join(special_requirements) if special_requirements else '无'}

请严格按照以下格式生成建议，确保每个模块都完整：

### 饮食
[基于用户BMI {health_metrics.get('bmi', 0)}和TDEE {health_metrics.get('tdee', 0)}卡路里的个性化营养建议]
- 每日热量目标及分配
- 三大营养素比例推荐
- 推荐食材类型
- 饮食时间安排
- 注意事项

### 运动
[基于用户体质和健康目标的运动方案]
- 适合的运动类型
- 运动强度和频次
- 每周运动计划
- 进阶方案
- 安全注意事项

### 体重
[科学的体重管理计划]
- 当前体重分析
- 合理目标体重：{health_metrics.get('ideal_weight_range', (0, 0))[0]}-{health_metrics.get('ideal_weight_range', (0, 0))[1]}kg
- 每周预期变化
- 监测方法
- 激励策略

### 睡眠
[睡眠质量改善建议]
- 睡眠时长建议
- 作息时间规划
- 睡前准备工作
- 环境优化
- 睡眠监测

### 心理
[心理健康支持建议]
- 压力管理技巧
- 情绪调节方法
- 动机维持策略
- 自我奖励机制
- 寻求支持的方式

请确保建议科学、实用、个性化，语言温和鼓励。每个模块都要有具体的行动指导。
"""
        return prompt

    def _get_system_prompt(self) -> str:
        """Get system prompt for health advice generation"""
        return """
你是AuraWell的专业健康管理AI助手，具备以下专业能力：

1. 营养学知识：了解宏量营养素、微量营养素、热量平衡等原理
2. 运动科学：掌握不同运动类型的效果、强度控制、安全要点
3. 体重管理：基于科学原理制定合理的体重目标和实现路径
4. 睡眠医学：了解睡眠周期、影响因素、改善方法
5. 心理健康：掌握动机激励、压力管理、情绪调节技巧

生成建议时请遵循：
- 基于循证医学，引用权威健康机构建议
- 个性化定制，考虑用户具体情况
- 安全第一，提醒潜在风险
- 循序渐进，制定可执行的阶段性目标
- 鼓励性语言，增强用户信心

重要：不提供医疗诊断，建议用户就医疗问题咨询专业医生。
"""

    async def _parse_and_validate_advice(
        self,
        advice_content: str,
        user_id: str,
        user_data: Dict[str, Any],
        health_metrics: Dict[str, Any],
    ) -> HealthAdviceResponse:
        """Parse and validate the generated advice content"""
        try:
            # Check if all sections are present
            if not self.parser.is_complete(advice_content):
                missing_sections = self.parser.get_missing_sections(advice_content)
                self.logger.warning(f"Missing sections: {missing_sections}")

                # Generate completion for missing sections
                completion_prompt = self.parser.generate_completion_prompt(
                    missing_sections,
                    {
                        "age": health_metrics.get("age"),
                        "gender": health_metrics.get("gender"),
                        "bmi": health_metrics.get("bmi"),
                        "health_goal": "整体健康",
                    },
                )

                # Try to complete missing sections
                if self.deepseek_client:
                    try:
                        completion = self.deepseek_client.get_deepseek_response(
                            messages=[{"role": "user", "content": completion_prompt}],
                            model_name=MODEL_CONFIG["reasoning_tasks"],  # 使用推理模型补全建议
                            temperature=0.3,
                        )
                        advice_content += "\n\n" + completion.content
                    except Exception as e:
                        self.logger.error(f"Error completing missing sections: {e}")

            # Parse sections
            parsed_sections = self.parser.parse_sections(advice_content)

            # Format structured response
            structured_response = self.parser.format_structured_response(
                parsed_sections, user_id
            )

            return structured_response

        except Exception as e:
            self.logger.error(f"Error parsing advice content: {e}")
            return await self._generate_fallback_advice(user_id, str(e))

    async def _generate_local_advice(
        self,
        user_data: Dict[str, Any],
        health_metrics: Dict[str, Any],
        goal_type: Optional[str],
    ) -> str:
        """Generate local fallback advice when DeepSeek is not available"""

        bmi = health_metrics.get("bmi", 22.5)
        tdee = health_metrics.get("tdee", 2200)

        advice = f"""
### 饮食
基于您的BMI {bmi}和每日总消耗{tdee}卡路里，建议您：
- 每日热量摄入：{int(tdee * 0.9 if goal_type == 'weight_loss' else tdee)}卡路里
- 蛋白质：占总热量的25-30%，有助于肌肉维护和饱腹感
- 碳水化合物：占总热量的45-50%，选择全谷物和蔬菜
- 脂肪：占总热量的20-25%，优选不饱和脂肪
- 建议多吃新鲜蔬果、瘦肉、鱼类、豆类
- 少食加工食品、高糖饮料、油炸食物

### 运动
根据您的体质状况，推荐以下运动方案：
- 有氧运动：每周150分钟中等强度，如快走、游泳、骑行
- 力量训练：每周2-3次，涵盖主要肌肉群
- 柔韧性训练：每日5-10分钟拉伸或瑜伽
- 循序渐进，从低强度开始，逐步增加
- 注意运动前热身，运动后拉伸

### 体重
科学的体重管理建议：
- 当前BMI：{bmi}，属于{health_metrics.get('bmi_category', '正常')}范围
- 建议每周体重变化控制在0.5-1公斤
- 通过合理饮食和运动创造热量缺口
- 每日监测体重，记录变化趋势
- 关注身体成分变化，不仅仅是体重数字

### 睡眠
优质睡眠对健康至关重要：
- 建议每晚7-9小时高质量睡眠
- 规律作息时间，固定睡眠和起床时间
- 睡前1小时避免电子设备
- 保持卧室凉爽、安静、黑暗
- 建立睡前放松仪式，如阅读、冥想

### 心理
保持积极心态，持续动力：
- 设定明确、可达成的阶段性目标
- 记录每日进步，庆祝小成就
- 寻找健康伙伴，互相支持鼓励
- 学习压力管理技巧，如深呼吸、冥想
- 遇到挫折时保持耐心，健康是长期投资
"""

        return advice

    async def _generate_fallback_advice(
        self, user_id: str, error_msg: str
    ) -> HealthAdviceResponse:
        """Generate fallback advice when all else fails"""

        fallback_sections = {
            "diet": {
                "title": "饮食建议",
                "content": "均衡饮食是健康的基础。建议多吃蔬菜水果，适量蛋白质，控制油盐糖摄入。",
                "recommendations": ["多吃蔬菜水果", "选择瘦肉蛋白", "控制油盐糖"],
            },
            "exercise": {
                "title": "运动计划",
                "content": "规律运动有益健康。建议每周至少150分钟中等强度运动。",
                "recommendations": [
                    "每周3-5次有氧运动",
                    "适量力量训练",
                    "注意运动安全",
                ],
            },
            "weight": {
                "title": "体重管理",
                "content": "健康体重管理需要综合饮食和运动。设定合理目标，持续监测。",
                "recommendations": ["合理设定目标", "定期监测体重", "保持耐心"],
            },
            "sleep": {
                "title": "睡眠优化",
                "content": "充足优质睡眠对健康重要。建议每晚7-9小时，规律作息。",
                "recommendations": ["保证睡眠时长", "规律作息时间", "优化睡眠环境"],
            },
            "mental_health": {
                "title": "心理健康",
                "content": "积极心态有助于健康目标达成。学会压力管理，保持动力。",
                "recommendations": ["保持积极心态", "学会压力管理", "寻求社会支持"],
            },
        }

        from .parsers import HealthAdviceSection

        sections = {}
        for key, section_data in fallback_sections.items():
            sections[key] = HealthAdviceSection(
                title=section_data["title"],
                content=section_data["content"],
                recommendations=section_data["recommendations"],
            )

        return self.parser.format_structured_response(sections, user_id)

    def _get_mock_user_profile(self, user_id: str) -> Any:
        """Generate mock user profile for testing"""

        class MockProfile:
            def __init__(self):
                self.user_id = user_id
                self.age = 30
                self.gender = Gender.MALE
                self.height_cm = 175.0
                self.weight_kg = 70.0
                self.activity_level = ActivityLevel.MODERATELY_ACTIVE

        return MockProfile()

    async def generate_quick_advice(self, user_id: str, topic: str) -> str:
        """
        Generate quick advice for specific health topics

        Args:
            user_id: User identifier
            topic: Specific health topic (diet, exercise, sleep, etc.)

        Returns:
            Quick health advice for the topic
        """
        try:
            user_data = await self._get_user_profile_data(user_id)
            health_metrics = await self._calculate_health_metrics(user_data)

            topic_prompts = {
                "diet": f"基于BMI {health_metrics.get('bmi', 22)}，提供今日饮食建议",
                "exercise": "根据活动水平，推荐适合的运动方案",
                "weight": f"当前体重{health_metrics.get('current_weight', 70)}kg的管理建议",
                "sleep": "改善睡眠质量的实用技巧",
                "mental": "保持积极心态和动力的方法",
            }

            prompt = topic_prompts.get(topic, f"关于{topic}的健康建议")

            if self.deepseek_client:
                response = self.deepseek_client.get_deepseek_response(
                    messages=[{"role": "user", "content": prompt}],
                    model_name=MODEL_CONFIG["chat_tasks"],  # 快速建议使用对话模型
                    temperature=0.3,
                    max_tokens=512,
                )
                return response.content
            else:
                return f"关于{topic}的健康建议：请保持均衡的生活方式，如需详细建议请使用完整的健康分析功能。"

        except Exception as e:
            self.logger.error(f"Error generating quick advice: {e}")
            return f"暂时无法生成{topic}建议，请稍后重试。"

    def _build_streaming_prompt(
        self, advice_request, user_data: Dict[str, Any], health_metrics: Dict[str, Any]
    ) -> str:
        """Build prompt for streaming health advice"""
        profile = user_data["profile"]

        prompt = f"""
用户咨询：{advice_request.user_query}

用户健康档案：
- 年龄：{getattr(profile, 'age', '未知')}岁
- 性别：{getattr(profile, 'gender', '未知')}
- 身高：{health_metrics.get('height', '未知')}cm
- 体重：{health_metrics.get('current_weight', '未知')}kg
- BMI：{health_metrics.get('bmi', '未知')} ({health_metrics.get('bmi_category', '未知')})
- 基础代谢率：{health_metrics.get('bmr', '未知')}卡路里/天
- 每日消耗：{health_metrics.get('tdee', '未知')}卡路里/天
- 活动水平：{health_metrics.get('activity_level', '未知')}

上下文信息：{advice_request.context if hasattr(advice_request, 'context') and advice_request.context else '无'}

请基于用户的具体问题和健康档案，提供个性化的健康建议。回答要专业、友好，并包含具体的行动建议。
"""
        return prompt

    async def _generate_fallback_streaming_response(self, advice_request) -> List[str]:
        """Generate fallback streaming response when DeepSeek is not available"""
        base_response = f"感谢您的咨询：{advice_request.user_query}\n\n由于AI服务暂时不可用，建议您：\n1. 咨询专业医生获取个性化建议\n2. 保持均衡饮食和适量运动\n3. 确保充足的睡眠和休息\n4. 定期监测健康指标\n\n祝您身体健康！"

        # Split into chunks for streaming effect
        words = base_response.split()
        chunks = []
        current_chunk = ""

        for word in words:
            if len(current_chunk + word + " ") < 20:  # Chunk size
                current_chunk += word + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = word + " "

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    async def _call_deepseek_with_retry(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> str:
        """
        调用DeepSeek API并实现重试机制

        Args:
            messages: 消息列表
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）

        Returns:
            API响应内容

        Raises:
            ExternalServiceError: API调用失败
        """
        import asyncio
        from aurawell.core.exceptions import ExternalServiceError

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = self.deepseek_client.get_deepseek_response(
                    messages=messages,
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                if response and hasattr(response, 'content'):
                    return response.content
                else:
                    raise ExternalServiceError("DeepSeek API返回空响应")

            except Exception as e:
                last_error = e
                error_type = type(e).__name__

                # 记录错误详情
                self.logger.warning(
                    f"DeepSeek API调用失败 (尝试 {attempt + 1}/{max_retries + 1}): "
                    f"{error_type} - {str(e)}"
                )

                # 判断是否应该重试
                if attempt < max_retries:
                    if self._should_retry_error(e):
                        # 指数退避延迟
                        delay = retry_delay * (2 ** attempt)
                        self.logger.info(f"等待 {delay:.1f} 秒后重试...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # 不可重试的错误，直接抛出
                        self.logger.error(f"遇到不可重试的错误: {error_type}")
                        break

        # 所有重试都失败了
        error_msg = f"DeepSeek API调用失败，已重试{max_retries}次: {str(last_error)}"
        self.logger.error(error_msg)
        raise ExternalServiceError(error_msg, service_name="deepseek")

    def _should_retry_error(self, error: Exception) -> bool:
        """
        判断错误是否应该重试

        Args:
            error: 异常对象

        Returns:
            是否应该重试
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        # 网络相关错误 - 应该重试
        network_errors = [
            'timeout', 'connection', 'network', 'socket',
            'connectionerror', 'timeouterror', 'httperror'
        ]

        # API限流错误 - 应该重试
        rate_limit_errors = [
            'rate limit', 'too many requests', '429', 'quota'
        ]

        # 服务器错误 - 应该重试
        server_errors = [
            '500', '502', '503', '504', 'internal server error',
            'bad gateway', 'service unavailable', 'gateway timeout'
        ]

        # 认证错误 - 不应该重试
        auth_errors = [
            '401', '403', 'unauthorized', 'forbidden',
            'invalid api key', 'authentication'
        ]

        # 客户端错误 - 不应该重试
        client_errors = [
            '400', 'bad request', 'invalid request',
            'validation error', 'malformed'
        ]

        # 检查是否为不可重试的错误
        for pattern in auth_errors + client_errors:
            if pattern in error_str:
                return False

        # 检查是否为可重试的错误
        for pattern in network_errors + rate_limit_errors + server_errors:
            if pattern in error_str:
                return True

        # 默认情况下，对于未知错误进行重试
        return True
