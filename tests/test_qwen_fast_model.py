#!/usr/bin/env python3
"""
测试 QWEN_FAST 模型调用功能
验证同节点下的QWEN_FAST对应的模型是否可以被正确调用
"""

import pytest
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.aurawell.core.deepseek_client import DeepSeekClient
from src.aurawell.services.model_fallback_service import get_model_fallback_service, ModelTier


class TestQwenFastModel:
    """QWEN_FAST 模型测试类"""
    
    @pytest.fixture
    def mock_env_vars(self):
        """模拟环境变量"""
        with patch.dict(os.environ, {
            'QWEN_FAST': 'qwen-turbo',
            'DEEPSEEK_SERIES_V3': 'deepseek-v3',
            'QWEN_API': 'test-api-key',
            'DASHSCOPE_API_KEY': 'test-api-key',
            'DASHSCOPE_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        }):
            yield
    
    @pytest.fixture
    def deepseek_client(self, mock_env_vars):
        """创建DeepSeek客户端实例（用于调用QWEN模型）"""
        return DeepSeekClient()
    
    def test_qwen_fast_environment_variable(self, mock_env_vars):
        """测试QWEN_FAST环境变量是否正确设置"""
        assert os.getenv("QWEN_FAST") == "qwen-turbo"
    
    def test_model_fallback_service_qwen_configuration(self, mock_env_vars):
        """测试多模型梯度服务中QWEN_FAST模型配置"""
        mock_client = MagicMock()
        service = get_model_fallback_service(mock_client)
        
        # 验证快速响应模型配置
        fast_response_config = service.model_configs[ModelTier.FAST_RESPONSE]
        assert fast_response_config.name == "qwen-turbo"
        assert fast_response_config.tier == ModelTier.FAST_RESPONSE
        assert fast_response_config.timeout_threshold == 60.0
        assert fast_response_config.max_retries == 3
    
    @patch('src.aurawell.core.deepseek_client.OpenAI')
    def test_qwen_turbo_model_call(self, mock_openai, deepseek_client):
        """测试QWEN-Turbo模型调用"""
        # 模拟OpenAI客户端响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这是QWEN-Turbo的快速响应"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "qwen-turbo"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 8
        mock_response.usage.completion_tokens = 15
        mock_response.usage.total_tokens = 23
        
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_instance
        
        # 重新创建客户端以使用模拟的OpenAI
        client = DeepSeekClient()
        
        # 测试消息
        messages = [
            {"role": "system", "content": "你是一个快速响应的健康助手"},
            {"role": "user", "content": "快速告诉我今天的运动建议"}
        ]
        
        # 调用QWEN-Turbo模型
        response = client.get_deepseek_response(
            messages=messages,
            model_name="qwen-turbo",
            temperature=0.5,
            max_tokens=256
        )
        
        # 验证响应
        assert response is not None
        assert response.content == "这是QWEN-Turbo的快速响应"
        assert response.model == "qwen-turbo"
        assert response.finish_reason == "stop"
        
        # 验证API调用参数
        mock_openai_instance.chat.completions.create.assert_called_once()
        call_args = mock_openai_instance.chat.completions.create.call_args
        assert call_args[1]['model'] == 'qwen-turbo'
        assert call_args[1]['messages'] == messages
        assert call_args[1]['temperature'] == 0.5
        assert call_args[1]['max_tokens'] == 256
    
    @patch('src.aurawell.services.model_fallback_service.ModelFallbackService')
    def test_model_fallback_to_qwen(self, mock_service_class, mock_env_vars):
        """测试模型降级到QWEN_FAST的场景"""
        # 模拟服务实例
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        # 模拟高精度模型失败，降级到快速响应模型
        mock_service.get_response.return_value = {
            "content": "降级到QWEN-Turbo的响应",
            "model_used": "qwen-turbo",
            "response_time": 2.5,
            "success": True
        }
        
        service = mock_service_class()
        response = service.get_response("测试查询", prefer_fast=True)
        
        assert response["model_used"] == "qwen-turbo"
        assert response["success"] is True
        assert response["response_time"] < 60.0  # 应该在快速响应阈值内
    
    def test_qwen_fast_timeout_configuration(self, mock_env_vars):
        """测试QWEN_FAST模型的超时配置"""
        from src.aurawell.services.model_fallback_service import ModelFallbackService
        
        service = ModelFallbackService()
        fast_config = service.model_configs[ModelTier.FAST_RESPONSE]
        
        # QWEN_FAST应该有较短的超时时间
        assert fast_config.timeout_threshold == 60.0  # 1分钟
        assert fast_config.max_retries == 3
        assert fast_config.name == os.getenv("QWEN_FAST", "qwen-turbo")
    
    @patch('src.aurawell.core.deepseek_client.OpenAI')
    def test_qwen_fast_performance_characteristics(self, mock_openai, deepseek_client):
        """测试QWEN_FAST模型的性能特征"""
        # 模拟快速响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "快速简洁的回答"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "qwen-turbo"
        
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_instance
        
        client = DeepSeekClient()
        
        # 测试快速查询
        messages = [{"role": "user", "content": "简单问题"}]
        
        response = client.get_deepseek_response(
            messages=messages,
            model_name="qwen-turbo",
            temperature=0.3,  # 较低的温度以获得更确定的回答
            max_tokens=128    # 较少的token以获得快速响应
        )
        
        assert response.content == "快速简洁的回答"
        
        # 验证调用参数适合快速响应
        call_args = mock_openai_instance.chat.completions.create.call_args
        assert call_args[1]['temperature'] == 0.3
        assert call_args[1]['max_tokens'] == 128
    
    def test_qwen_fast_vs_deepseek_v3_configuration(self, mock_env_vars):
        """测试QWEN_FAST与DeepSeek-V3的配置差异"""
        from src.aurawell.services.model_fallback_service import ModelFallbackService
        
        service = ModelFallbackService()
        
        high_precision_config = service.model_configs[ModelTier.HIGH_PRECISION]
        fast_response_config = service.model_configs[ModelTier.FAST_RESPONSE]
        
        # 验证配置差异
        assert high_precision_config.name == "deepseek-v3"
        assert fast_response_config.name == "qwen-turbo"
        
        # 超时阈值差异
        assert high_precision_config.timeout_threshold > fast_response_config.timeout_threshold
        assert high_precision_config.timeout_threshold == 180.0  # 3分钟
        assert fast_response_config.timeout_threshold == 60.0    # 1分钟
        
        # 重试次数差异
        assert high_precision_config.max_retries == 2
        assert fast_response_config.max_retries == 3
    
    @pytest.mark.asyncio
    async def test_qwen_fast_concurrent_calls(self, mock_env_vars):
        """测试QWEN_FAST模型的并发调用能力"""
        with patch('src.aurawell.core.deepseek_client.OpenAI') as mock_openai:
            # 模拟多个快速响应
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "并发响应"
            mock_response.choices[0].finish_reason = "stop"
            mock_response.model = "qwen-turbo"
            
            mock_openai_instance = MagicMock()
            mock_openai_instance.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_openai_instance
            
            client = DeepSeekClient()
            
            # 并发调用
            async def make_call(query_id):
                return client.get_deepseek_response(
                    messages=[{"role": "user", "content": f"查询{query_id}"}],
                    model_name="qwen-turbo"
                )
            
            # 同时发起多个请求
            tasks = [make_call(i) for i in range(3)]
            responses = await asyncio.gather(*tasks)
            
            # 验证所有响应
            assert len(responses) == 3
            for response in responses:
                assert response.content == "并发响应"
                assert response.model == "qwen-turbo"
    
    def test_qwen_fast_error_recovery(self, mock_env_vars):
        """测试QWEN_FAST模型的错误恢复机制"""
        with patch('src.aurawell.core.deepseek_client.OpenAI') as mock_openai:
            # 模拟第一次调用失败，第二次成功
            mock_openai_instance = MagicMock()
            mock_openai_instance.chat.completions.create.side_effect = [
                Exception("网络错误"),  # 第一次失败
                MagicMock(choices=[MagicMock(message=MagicMock(content="恢复成功"), finish_reason="stop")], model="qwen-turbo")  # 第二次成功
            ]
            mock_openai.return_value = mock_openai_instance
            
            client = DeepSeekClient()
            
            # 第一次调用应该失败
            with pytest.raises(Exception):
                client.get_deepseek_response(
                    messages=[{"role": "user", "content": "测试"}],
                    model_name="qwen-turbo"
                )
            
            # 第二次调用应该成功
            response = client.get_deepseek_response(
                messages=[{"role": "user", "content": "测试"}],
                model_name="qwen-turbo"
            )
            assert response.content == "恢复成功"
    
    def test_environment_variable_fallback(self):
        """测试环境变量回退机制"""
        # 测试没有设置QWEN_FAST时的默认值
        with patch.dict(os.environ, {}, clear=True):
            from src.aurawell.services.model_fallback_service import ModelFallbackService
            service = ModelFallbackService()
            
            fast_config = service.model_configs[ModelTier.FAST_RESPONSE]
            assert fast_config.name == "qwen-turbo"  # 应该使用默认值


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
