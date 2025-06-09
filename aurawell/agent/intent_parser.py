"""
用户意图识别模块

通过DeepSeek API分析用户请求并输出结构化意图信息。
"""

import json
import logging
import hashlib
import time
from typing import Dict, Any
from enum import Enum

from ..core.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """用户意图类型枚举"""
    ACTIVITY_QUERY = "activity_query"           # 活动数据查询
    SLEEP_ANALYSIS = "sleep_analysis"           # 睡眠分析
    GOAL_SETTING = "goal_setting"               # 目标设置
    HEALTH_INSIGHTS = "health_insights"         # 健康洞察
    ACHIEVEMENT_CHECK = "achievement_check"     # 成就检查
    NUTRITION_ANALYSIS = "nutrition_analysis"   # 营养分析
    EXERCISE_PLAN = "exercise_plan"             # 运动计划
    HEALTH_REPORT = "health_report"             # 健康报告
    WEIGHT_TRACKING = "weight_tracking"         # 体重跟踪
    GENERAL_CHAT = "general_chat"               # 一般对话


class IntentParser:
    """
    智能用户意图识别系统

    通过DeepSeek API分析用户请求并输出结构化意图信息。
    """

    def __init__(self, fast_mode: bool = False):
        """
        初始化意图解析器

        Args:
            fast_mode: 快速模式，使用本地规则而不是API调用
        """
        self.fast_mode = fast_mode
        self.deepseek_client = DeepSeekClient() if not fast_mode else None
        self.intent_examples = self._load_intent_examples()

        # 缓存机制
        self.intent_cache = {}  # 意图识别结果缓存
        self.cache_ttl = 300  # 缓存5分钟
        self.max_cache_size = 1000  # 最大缓存条目数

    async def parse_intent(self, user_request: str) -> Dict[str, Any]:
        """
        解析用户意图（带缓存优化）

        Args:
            user_request: 用户请求字符串

        Returns:
            {
                "RequestType": "activity_query|sleep_analysis|goal_setting|...",
                "RequestContent": {...},  # 符合工具调用格式
                "confidence": 0.95
            }
        """
        try:
            # 检查缓存
            cache_key = self._get_cache_key(user_request)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Intent retrieved from cache: %s", cached_result['RequestType'])
                return cached_result

            # 构建意图识别prompt
            prompt = self._build_intent_prompt(user_request)

            # 调用DeepSeek API
            messages = [{"role": "user", "content": prompt}]
            deepseek_response = self.deepseek_client.get_deepseek_response(
                messages=messages,
                model_name="deepseek-chat",
                temperature=0.3
            )
            response = deepseek_response.content

            # 解析响应
            intent_result = self._parse_response(response)

            # 验证和标准化结果
            validated_result = self._validate_intent_result(intent_result)

            # 存储到缓存
            self._store_to_cache(cache_key, validated_result)

            logger.info("Intent parsed: %s (confidence: %.2f)",
                       validated_result['RequestType'], validated_result['confidence'])
            return validated_result

        except Exception as e:
            logger.error("Intent parsing failed: %s", str(e))
            # 返回默认的一般对话意图
            return {
                "RequestType": IntentType.GENERAL_CHAT.value,
                "RequestContent": {"message": user_request},
                "confidence": 0.1
            }

    def _build_intent_prompt(self, user_request: str) -> str:
        """构建意图识别的prompt"""
        prompt = f"""
你是AuraWell健康助手的意图识别专家。请分析用户的请求，识别其意图类型并提取相关参数。

支持的意图类型：
1. activity_query - 查询活动数据（步数、距离、卡路里等）
2. sleep_analysis - 睡眠分析和查询
3. goal_setting - 设置健康目标
4. health_insights - 获取健康洞察和建议
5. achievement_check - 检查成就进度
6. nutrition_analysis - 营养分析
7. exercise_plan - 生成运动计划
8. health_report - 生成健康报告
9. weight_tracking - 体重跟踪和管理
10. general_chat - 一般对话

用户请求："{user_request}"

请以JSON格式返回结果：
{{
    "RequestType": "意图类型",
    "RequestContent": {{
        "参数名": "参数值"
    }},
    "confidence": 0.95
}}

示例：
用户："我今天走了多少步？"
返回：
{{
    "RequestType": "activity_query",
    "RequestContent": {{
        "query_type": "steps",
        "time_period": "today"
    }},
    "confidence": 0.95
}}

请只返回JSON，不要其他内容。
"""
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析DeepSeek API响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response[start_idx:end_idx]
                    return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass

            # 如果都失败，返回默认结果
            logger.warning("Failed to parse intent response: %s", response)
            return {
                "RequestType": IntentType.GENERAL_CHAT.value,
                "RequestContent": {},
                "confidence": 0.1
            }

    def _validate_intent_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证和标准化意图识别结果"""
        # 验证RequestType
        request_type = result.get("RequestType", IntentType.GENERAL_CHAT.value)
        valid_types = [intent.value for intent in IntentType]
        if request_type not in valid_types:
            request_type = IntentType.GENERAL_CHAT.value

        # 验证confidence
        confidence = result.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.5

        # 验证RequestContent
        request_content = result.get("RequestContent", {})
        if not isinstance(request_content, dict):
            request_content = {}

        return {
            "RequestType": request_type,
            "RequestContent": request_content,
            "confidence": confidence
        }

    def _get_cache_key(self, user_request: str) -> str:
        """生成缓存键"""
        # 标准化用户请求（去除空格、转小写）
        normalized_request = user_request.strip().lower()
        # 使用MD5哈希生成缓存键
        return hashlib.md5(normalized_request.encode('utf-8')).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Dict[str, Any]:
        """从缓存获取结果"""
        if cache_key not in self.intent_cache:
            return None

        cache_entry = self.intent_cache[cache_key]
        current_time = time.time()

        # 检查是否过期
        if current_time - cache_entry['timestamp'] > self.cache_ttl:
            del self.intent_cache[cache_key]
            return None

        return cache_entry['result']

    def _store_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """存储结果到缓存"""
        # 如果缓存已满，删除最旧的条目
        if len(self.intent_cache) >= self.max_cache_size:
            oldest_key = min(self.intent_cache.keys(),
                           key=lambda k: self.intent_cache[k]['timestamp'])
            del self.intent_cache[oldest_key]

        # 存储新结果
        self.intent_cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }

    def _load_intent_examples(self) -> Dict[str, list]:
        """加载意图识别示例（用于提高准确性）"""
        return {
            IntentType.ACTIVITY_QUERY.value: [
                "我今天走了多少步？",
                "查看我的运动数据",
                "最近一周的活动情况"
            ],
            IntentType.SLEEP_ANALYSIS.value: [
                "我昨晚睡得怎么样？",
                "分析我的睡眠质量",
                "查看睡眠报告"
            ],
            IntentType.GOAL_SETTING.value: [
                "我想设置每天走10000步的目标",
                "帮我制定健康目标",
                "更新我的运动目标"
            ],
            IntentType.HEALTH_INSIGHTS.value: [
                "给我一些健康建议",
                "分析我的健康状况",
                "有什么改善建议吗？"
            ],
            IntentType.ACHIEVEMENT_CHECK.value: [
                "我获得了哪些成就？",
                "查看我的进度",
                "成就系统"
            ]
        }