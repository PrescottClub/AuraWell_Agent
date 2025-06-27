"""
AuraWell 多模型梯度服务
实现deepseek-r1-0528和qwen-turbo的智能切换机制
"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """模型级别枚举"""
    HIGH_PRECISION = "HighPrecision"
    FAST_RESPONSE = "FastResponse"


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    tier: ModelTier
    timeout_threshold: float  # 超时阈值（秒）
    max_retries: int = 3


@dataclass
class ModelResponse:
    """模型响应结果"""
    content: str
    model_used: str
    response_time: float
    success: bool
    error_message: Optional[str] = None


class ModelFallbackService:
    """
    多模型梯度服务
    实现模型间的智能切换和降级机制
    """
    
    def __init__(self, deepseek_client=None):
        """
        初始化多模型服务
        
        Args:
            deepseek_client: DeepSeek客户端实例
        """
        self.deepseek_client = deepseek_client
        
        # 模型配置字典
        self.model_configs = {
            ModelTier.HIGH_PRECISION: ModelConfig(
                name="deepseek-r1-0528",
                tier=ModelTier.HIGH_PRECISION,
                timeout_threshold=180.0,  # 3分钟超时阈值
                max_retries=2
            ),
            ModelTier.FAST_RESPONSE: ModelConfig(
                name="qwen-turbo",
                tier=ModelTier.FAST_RESPONSE,
                timeout_threshold=60.0,   # 1分钟超时阈值
                max_retries=3
            )
        }
        
        # 性能统计
        self.performance_stats = {
            ModelTier.HIGH_PRECISION: {
                "total_calls": 0,
                "successful_calls": 0,
                "average_response_time": 0.0,
                "timeout_count": 0
            },
            ModelTier.FAST_RESPONSE: {
                "total_calls": 0,
                "successful_calls": 0,
                "average_response_time": 0.0,
                "timeout_count": 0
            }
        }
        
        # 上下文管理
        self.conversation_context = {}
        
        logger.info("多模型梯度服务初始化完成")
    
    def _update_performance_stats(self, tier: ModelTier, response_time: float, success: bool, timeout: bool = False):
        """更新性能统计"""
        stats = self.performance_stats[tier]
        stats["total_calls"] += 1
        
        if success:
            stats["successful_calls"] += 1
            # 更新平均响应时间
            if stats["successful_calls"] == 1:
                stats["average_response_time"] = response_time
            else:
                stats["average_response_time"] = (
                    (stats["average_response_time"] * (stats["successful_calls"] - 1) + response_time) 
                    / stats["successful_calls"]
                )
        
        if timeout:
            stats["timeout_count"] += 1
    
    def _should_fallback_to_fast_model(self, tier: ModelTier) -> bool:
        """
        判断是否应该降级到快速模型
        
        Args:
            tier: 当前模型级别
            
        Returns:
            bool: 是否应该降级
        """
        if tier == ModelTier.FAST_RESPONSE:
            return False  # 已经是最快的模型了
        
        stats = self.performance_stats[ModelTier.HIGH_PRECISION]
        
        # 如果高精度模型超时次数过多，建议降级
        if stats["total_calls"] > 0:
            timeout_rate = stats["timeout_count"] / stats["total_calls"]
            if timeout_rate > 0.3:  # 超时率超过30%
                logger.warning(f"高精度模型超时率过高({timeout_rate:.2%})，建议降级")
                return True
        
        # 如果平均响应时间过长，建议降级
        if stats["average_response_time"] > 120.0:  # 平均响应时间超过2分钟
            logger.warning(f"高精度模型平均响应时间过长({stats['average_response_time']:.1f}s)，建议降级")
            return True
        
        return False
    
    def _preserve_context(self, conversation_id: str, user_message: str, ai_response: str, model_used: str):
        """
        保存对话上下文
        
        Args:
            conversation_id: 对话ID
            user_message: 用户消息
            ai_response: AI回复
            model_used: 使用的模型
        """
        if conversation_id not in self.conversation_context:
            self.conversation_context[conversation_id] = []
        
        # 保留最近的对话历史（最多5轮）
        context = self.conversation_context[conversation_id]
        context.append({
            "user": user_message,
            "assistant": ai_response,
            "model": model_used,
            "timestamp": time.time()
        })
        
        # 只保留最近5轮对话
        if len(context) > 5:
            context.pop(0)
    
    def _build_messages_with_context(self, messages: List[Dict[str, str]], conversation_id: Optional[str] = None) -> List[Dict[str, str]]:
        """
        构建包含上下文的消息列表
        
        Args:
            messages: 原始消息列表
            conversation_id: 对话ID
            
        Returns:
            List[Dict[str, str]]: 包含上下文的消息列表
        """
        if not conversation_id or conversation_id not in self.conversation_context:
            return messages
        
        context = self.conversation_context[conversation_id]
        if not context:
            return messages
        
        # 构建包含上下文的消息
        context_messages = []
        
        # 添加系统消息（如果有）
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        context_messages.extend(system_messages)
        
        # 添加最近的对话历史
        for ctx in context[-2:]:  # 只添加最近2轮对话作为上下文
            context_messages.append({"role": "user", "content": ctx["user"]})
            context_messages.append({"role": "assistant", "content": ctx["assistant"]})
        
        # 添加当前用户消息
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        context_messages.extend(user_messages)
        
        return context_messages
    
    async def get_model_response(
        self,
        messages: List[Dict[str, str]],
        conversation_id: Optional[str] = None,
        preferred_tier: ModelTier = ModelTier.HIGH_PRECISION,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> ModelResponse:
        """
        获取模型响应，支持自动降级
        
        Args:
            messages: 消息列表
            conversation_id: 对话ID，用于上下文管理
            preferred_tier: 首选模型级别
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            ModelResponse: 模型响应结果
        """
        if not self.deepseek_client:
            return ModelResponse(
                content="AI服务暂时不可用",
                model_used="none",
                response_time=0.0,
                success=False,
                error_message="DeepSeek客户端未初始化"
            )
        
        # 构建包含上下文的消息
        enhanced_messages = self._build_messages_with_context(messages, conversation_id)
        
        # 确定要尝试的模型顺序
        models_to_try = []
        
        # 检查是否应该直接降级
        if preferred_tier == ModelTier.HIGH_PRECISION and self._should_fallback_to_fast_model(preferred_tier):
            logger.info("基于性能统计，直接使用快速响应模型")
            models_to_try = [ModelTier.FAST_RESPONSE]
        else:
            if preferred_tier == ModelTier.HIGH_PRECISION:
                models_to_try = [ModelTier.HIGH_PRECISION, ModelTier.FAST_RESPONSE]
            else:
                models_to_try = [ModelTier.FAST_RESPONSE]
        
        last_error = None
        
        for tier in models_to_try:
            config = self.model_configs[tier]
            logger.info(f"尝试使用模型: {config.name} (级别: {tier.value})")
            
            start_time = time.time()
            timeout_occurred = False
            
            try:
                # 设置超时
                response = await asyncio.wait_for(
                    self._call_model(config, enhanced_messages, temperature, max_tokens, **kwargs),
                    timeout=config.timeout_threshold
                )
                
                response_time = time.time() - start_time
                
                if response and hasattr(response, 'content') and response.content:
                    # 更新性能统计
                    self._update_performance_stats(tier, response_time, True)
                    
                    # 保存上下文
                    if conversation_id and len(messages) > 0:
                        user_message = next((msg["content"] for msg in messages if msg.get("role") == "user"), "")
                        if user_message:
                            self._preserve_context(conversation_id, user_message, response.content, config.name)
                    
                    logger.info(f"模型 {config.name} 响应成功，耗时: {response_time:.2f}s")
                    
                    return ModelResponse(
                        content=response.content,
                        model_used=config.name,
                        response_time=response_time,
                        success=True
                    )
                else:
                    raise Exception("模型返回空响应")
                    
            except asyncio.TimeoutError:
                timeout_occurred = True
                response_time = time.time() - start_time
                error_msg = f"模型 {config.name} 响应超时 (>{config.timeout_threshold}s)"
                logger.warning(error_msg)
                last_error = error_msg
                
                # 更新性能统计
                self._update_performance_stats(tier, response_time, False, timeout=True)
                
            except Exception as e:
                response_time = time.time() - start_time
                error_msg = f"模型 {config.name} 调用失败: {str(e)}"
                logger.error(error_msg)
                last_error = error_msg
                
                # 更新性能统计
                self._update_performance_stats(tier, response_time, False)
        
        # 所有模型都失败了
        logger.error("所有模型都无法响应")
        return ModelResponse(
            content="抱歉，AI服务暂时不可用，请稍后再试。",
            model_used="none",
            response_time=0.0,
            success=False,
            error_message=last_error
        )
    
    async def _call_model(self, config: ModelConfig, messages: List[Dict[str, str]], temperature: float, max_tokens: int, **kwargs):
        """
        调用具体的模型
        
        Args:
            config: 模型配置
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            模型响应
        """
        return self.deepseek_client.get_deepseek_response(
            messages=messages,
            model_name=config.name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            "model_configs": {tier.value: {
                "name": config.name,
                "timeout_threshold": config.timeout_threshold,
                "max_retries": config.max_retries
            } for tier, config in self.model_configs.items()},
            "performance_stats": {tier.value: stats for tier, stats in self.performance_stats.items()},
            "active_conversations": len(self.conversation_context)
        }


# 全局服务实例
_model_fallback_service = None


def get_model_fallback_service(deepseek_client=None) -> ModelFallbackService:
    """获取多模型梯度服务实例（单例模式）"""
    global _model_fallback_service
    if _model_fallback_service is None:
        _model_fallback_service = ModelFallbackService(deepseek_client)
    return _model_fallback_service
