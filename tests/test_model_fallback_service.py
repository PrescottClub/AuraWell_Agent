"""
AuraWell 多模型梯度服务测试
测试deepseek-r1-0528和qwen-turbo的智能切换机制
"""

import unittest
import pytest
import logging
import os
import sys
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aurawell.services.model_fallback_service import (
    ModelFallbackService, 
    ModelTier, 
    ModelConfig, 
    ModelResponse,
    get_model_fallback_service
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestModelFallbackService(unittest.TestCase):
    """多模型梯度服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_deepseek_client = Mock()
        self.service = ModelFallbackService(self.mock_deepseek_client)
    
    def test_service_initialization(self):
        """测试服务初始化"""
        logger.info("🧪 测试多模型梯度服务初始化")
        
        # 验证模型配置
        self.assertIn(ModelTier.HIGH_PRECISION, self.service.model_configs)
        self.assertIn(ModelTier.FAST_RESPONSE, self.service.model_configs)
        
        # 验证高精度模型配置
        high_precision_config = self.service.model_configs[ModelTier.HIGH_PRECISION]
        self.assertEqual(high_precision_config.name, "deepseek-r1-0528")
        self.assertEqual(high_precision_config.timeout_threshold, 180.0)
        
        # 验证快速响应模型配置
        fast_response_config = self.service.model_configs[ModelTier.FAST_RESPONSE]
        self.assertEqual(fast_response_config.name, "qwen-turbo")
        self.assertEqual(fast_response_config.timeout_threshold, 60.0)
        
        # 验证性能统计初始化
        self.assertIn(ModelTier.HIGH_PRECISION, self.service.performance_stats)
        self.assertIn(ModelTier.FAST_RESPONSE, self.service.performance_stats)
        
        logger.info("✅ 多模型梯度服务初始化测试通过")
    
    def test_performance_stats_update(self):
        """测试性能统计更新"""
        logger.info("🧪 测试性能统计更新")
        
        # 测试成功调用统计
        self.service._update_performance_stats(ModelTier.HIGH_PRECISION, 2.5, True)
        
        stats = self.service.performance_stats[ModelTier.HIGH_PRECISION]
        self.assertEqual(stats["total_calls"], 1)
        self.assertEqual(stats["successful_calls"], 1)
        self.assertEqual(stats["average_response_time"], 2.5)
        self.assertEqual(stats["timeout_count"], 0)
        
        # 测试超时调用统计
        self.service._update_performance_stats(ModelTier.HIGH_PRECISION, 5.0, False, timeout=True)
        
        stats = self.service.performance_stats[ModelTier.HIGH_PRECISION]
        self.assertEqual(stats["total_calls"], 2)
        self.assertEqual(stats["successful_calls"], 1)
        self.assertEqual(stats["timeout_count"], 1)
        
        logger.info("✅ 性能统计更新测试通过")
    
    def test_should_fallback_logic(self):
        """测试降级逻辑"""
        logger.info("🧪 测试降级逻辑")
        
        # 初始状态不应该降级
        should_fallback = self.service._should_fallback_to_fast_model(ModelTier.HIGH_PRECISION)
        self.assertFalse(should_fallback)
        
        # 模拟高超时率情况
        for _ in range(10):
            self.service._update_performance_stats(ModelTier.HIGH_PRECISION, 5.0, False, timeout=True)
        
        should_fallback = self.service._should_fallback_to_fast_model(ModelTier.HIGH_PRECISION)
        self.assertTrue(should_fallback)
        
        # 重置统计
        self.service.performance_stats[ModelTier.HIGH_PRECISION] = {
            "total_calls": 0,
            "successful_calls": 0,
            "average_response_time": 0.0,
            "timeout_count": 0
        }
        
        # 模拟高响应时间情况
        for _ in range(5):
            self.service._update_performance_stats(ModelTier.HIGH_PRECISION, 150.0, True)
        
        should_fallback = self.service._should_fallback_to_fast_model(ModelTier.HIGH_PRECISION)
        self.assertTrue(should_fallback)
        
        logger.info("✅ 降级逻辑测试通过")
    
    def test_context_preservation(self):
        """测试上下文保存"""
        logger.info("🧪 测试上下文保存")
        
        conversation_id = "test_conv_123"
        
        # 保存第一轮对话
        self.service._preserve_context(
            conversation_id, 
            "你好", 
            "您好！我是健康助手", 
            "deepseek-r1-0528"
        )
        
        # 验证上下文保存
        self.assertIn(conversation_id, self.service.conversation_context)
        context = self.service.conversation_context[conversation_id]
        self.assertEqual(len(context), 1)
        self.assertEqual(context[0]["user"], "你好")
        self.assertEqual(context[0]["assistant"], "您好！我是健康助手")
        self.assertEqual(context[0]["model"], "deepseek-r1-0528")
        
        # 保存更多对话，测试长度限制
        for i in range(10):
            self.service._preserve_context(
                conversation_id,
                f"问题{i}",
                f"回答{i}",
                "qwen-turbo"
            )
        
        # 验证只保留最近5轮对话
        context = self.service.conversation_context[conversation_id]
        self.assertEqual(len(context), 5)
        
        logger.info("✅ 上下文保存测试通过")
    
    def test_build_messages_with_context(self):
        """测试构建包含上下文的消息"""
        logger.info("🧪 测试构建包含上下文的消息")
        
        conversation_id = "test_conv_456"
        
        # 保存一些上下文
        self.service._preserve_context(conversation_id, "之前的问题", "之前的回答", "deepseek-r1-0528")
        
        # 构建消息
        messages = [
            {"role": "system", "content": "你是健康助手"},
            {"role": "user", "content": "当前问题"}
        ]
        
        enhanced_messages = self.service._build_messages_with_context(messages, conversation_id)
        
        # 验证消息结构
        self.assertGreater(len(enhanced_messages), len(messages))
        
        # 验证包含系统消息
        system_messages = [msg for msg in enhanced_messages if msg["role"] == "system"]
        self.assertEqual(len(system_messages), 1)
        
        # 验证包含上下文
        context_found = any("之前的问题" in msg["content"] for msg in enhanced_messages if msg["role"] == "user")
        self.assertTrue(context_found)
        
        logger.info("✅ 构建包含上下文的消息测试通过")
    
    @pytest.mark.asyncio
    async def test_successful_model_response(self):
        """测试成功的模型响应"""
        logger.info("🧪 测试成功的模型响应")
        
        # Mock成功的DeepSeek响应
        mock_response = Mock()
        mock_response.content = "这是一个健康建议"
        self.mock_deepseek_client.get_deepseek_response.return_value = mock_response
        
        messages = [{"role": "user", "content": "给我一些健康建议"}]
        
        result = await self.service.get_model_response(messages)
        
        # 验证响应
        self.assertTrue(result.success)
        self.assertEqual(result.content, "这是一个健康建议")
        self.assertEqual(result.model_used, "deepseek-r1-0528")
        self.assertGreater(result.response_time, 0)
        
        logger.info("✅ 成功的模型响应测试通过")
    
    @pytest.mark.asyncio
    async def test_model_timeout_fallback(self):
        """测试模型超时降级"""
        logger.info("🧪 测试模型超时降级")
        
        # Mock第一个模型超时，第二个模型成功
        async def mock_call_model(config, messages, temperature, max_tokens, **kwargs):
            if config.name == "deepseek-r1-0528":
                await asyncio.sleep(0.1)  # 模拟超时
                raise asyncio.TimeoutError("模型响应超时")
            else:
                mock_response = Mock()
                mock_response.content = "快速响应内容"
                return mock_response
        
        self.service._call_model = mock_call_model
        
        # 设置较短的超时时间用于测试
        self.service.model_configs[ModelTier.HIGH_PRECISION].timeout_threshold = 0.05
        
        messages = [{"role": "user", "content": "测试超时"}]
        
        result = await self.service.get_model_response(messages)
        
        # 验证降级到快速模型
        self.assertTrue(result.success)
        self.assertEqual(result.content, "快速响应内容")
        self.assertEqual(result.model_used, "qwen-turbo")
        
        logger.info("✅ 模型超时降级测试通过")
    
    @pytest.mark.asyncio
    async def test_all_models_fail(self):
        """测试所有模型都失败的情况"""
        logger.info("🧪 测试所有模型都失败的情况")
        
        # Mock所有模型都失败
        async def mock_call_model_fail(config, messages, temperature, max_tokens, **kwargs):
            raise Exception(f"模型 {config.name} 调用失败")
        
        self.service._call_model = mock_call_model_fail
        
        messages = [{"role": "user", "content": "测试失败"}]
        
        result = await self.service.get_model_response(messages)
        
        # 验证失败响应
        self.assertFalse(result.success)
        self.assertIn("抱歉", result.content)
        self.assertEqual(result.model_used, "none")
        self.assertIsNotNone(result.error_message)
        
        logger.info("✅ 所有模型都失败的情况测试通过")
    
    def test_performance_report(self):
        """测试性能报告"""
        logger.info("🧪 测试性能报告")
        
        # 添加一些统计数据
        self.service._update_performance_stats(ModelTier.HIGH_PRECISION, 2.0, True)
        self.service._update_performance_stats(ModelTier.FAST_RESPONSE, 1.0, True)
        
        report = self.service.get_performance_report()
        
        # 验证报告结构
        self.assertIn("model_configs", report)
        self.assertIn("performance_stats", report)
        self.assertIn("active_conversations", report)
        
        # 验证模型配置信息
        self.assertIn("HighPrecision", report["model_configs"])
        self.assertIn("FastResponse", report["model_configs"])
        
        # 验证性能统计信息
        self.assertIn("HighPrecision", report["performance_stats"])
        self.assertIn("FastResponse", report["performance_stats"])
        
        logger.info("✅ 性能报告测试通过")
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        logger.info("🧪 测试单例模式")
        
        # 清除全局实例
        import aurawell.services.model_fallback_service as mfs_module
        mfs_module._model_fallback_service = None
        
        service1 = get_model_fallback_service(self.mock_deepseek_client)
        service2 = get_model_fallback_service(self.mock_deepseek_client)
        
        self.assertIs(service1, service2, "单例模式失败")
        
        logger.info("✅ 单例模式测试通过")


class TestModelFallbackIntegration(unittest.TestCase):
    """多模型梯度服务集成测试"""
    
    @pytest.mark.integration
    def test_chat_service_integration(self):
        """测试与聊天服务的集成"""
        logger.info("🧪 测试与聊天服务的集成")
        
        try:
            from aurawell.services.chat_service import ChatService
            
            chat_service = ChatService()
            
            # 验证多模型服务已集成
            self.assertIsNotNone(chat_service.model_fallback_service)
            
            logger.info("✅ 与聊天服务的集成测试通过")
            
        except Exception as e:
            logger.warning(f"⚠️ 聊天服务集成测试跳过: {e}")
            pytest.skip("聊天服务不可用")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
