#!/usr/bin/env python3
"""
测试 DeepSeek-V3 模型调用功能
验证模型是否可以被正确调用和响应
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


class TestDeepSeekV3Model:
    """DeepSeek-V3 模型测试类"""
    
    @pytest.fixture
    def mock_env_vars(self):
        """模拟环境变量"""
        with patch.dict(os.environ, {
            'DEEPSEEK_SERIES_V3': 'deepseek-v3',
            'QWEN_API': 'test-api-key',
            'DASHSCOPE_API_KEY': 'test-api-key',
            'DASHSCOPE_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        }):
            yield
    
    @pytest.fixture
    def deepseek_client(self, mock_env_vars):
        """创建DeepSeek客户端实例"""
        return DeepSeekClient()
    
    def test_environment_variable_loading(self, mock_env_vars):
        """测试环境变量是否正确加载"""
        assert os.getenv("DEEPSEEK_SERIES_V3") == "deepseek-v3"
        assert os.getenv("QWEN_API") == "test-api-key"
        assert os.getenv("DASHSCOPE_BASE_URL") == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    def test_deepseek_client_initialization(self, deepseek_client):
        """测试DeepSeek客户端初始化"""
        assert deepseek_client is not None
        assert deepseek_client.api_key == "test-api-key"
        assert deepseek_client.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
        assert deepseek_client.client is not None
    
    @patch('src.aurawell.core.deepseek_client.OpenAI')
    def test_deepseek_v3_model_call(self, mock_openai, deepseek_client):
        """测试DeepSeek-V3模型调用"""
        # 模拟OpenAI客户端响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这是一个测试响应"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "deepseek-v3"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_instance
        
        # 重新创建客户端以使用模拟的OpenAI
        client = DeepSeekClient()
        
        # 测试消息
        messages = [
            {"role": "system", "content": "你是一个健康助手"},
            {"role": "user", "content": "请介绍健康饮食"}
        ]
        
        # 调用模型
        response = client.get_deepseek_response(
            messages=messages,
            model_name="deepseek-v3",
            temperature=0.7,
            max_tokens=512
        )
        
        # 验证响应
        assert response is not None
        assert response.content == "这是一个测试响应"
        assert response.model == "deepseek-v3"
        assert response.finish_reason == "stop"
        
        # 验证API调用参数
        mock_openai_instance.chat.completions.create.assert_called_once()
        call_args = mock_openai_instance.chat.completions.create.call_args
        assert call_args[1]['model'] == 'deepseek-v3'
        assert call_args[1]['messages'] == messages
        assert call_args[1]['temperature'] == 0.7
        assert call_args[1]['max_tokens'] == 512
    
    def test_model_fallback_service_configuration(self, mock_env_vars):
        """测试多模型梯度服务配置"""
        # 创建模拟的DeepSeek客户端
        mock_client = MagicMock()
        
        # 获取多模型服务
        service = get_model_fallback_service(mock_client)
        
        # 验证模型配置
        assert service is not None
        assert len(service.model_configs) == 2
        
        # 验证高精度模型配置
        high_precision_config = service.model_configs[ModelTier.HIGH_PRECISION]
        assert high_precision_config.name == "deepseek-v3"
        assert high_precision_config.timeout_threshold == 180.0

        # 验证快速响应模型配置
        fast_response_config = service.model_configs[ModelTier.FAST_RESPONSE]
        assert fast_response_config.name == "qwen-turbo"
        assert fast_response_config.timeout_threshold == 60.0
    
    @patch('src.aurawell.core.deepseek_client.OpenAI')
    def test_error_handling(self, mock_openai, deepseek_client):
        """测试错误处理"""
        # 模拟API错误
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.side_effect = Exception("API调用失败")
        mock_openai.return_value = mock_openai_instance
        
        client = DeepSeekClient()
        
        messages = [{"role": "user", "content": "测试消息"}]
        
        # 验证异常被正确抛出
        with pytest.raises(Exception) as exc_info:
            client.get_deepseek_response(messages=messages, model_name="deepseek-v3")
        
        assert "API调用失败" in str(exc_info.value)
    
    def test_model_name_from_environment(self, mock_env_vars):
        """测试从环境变量读取模型名称"""
        from src.aurawell.services.model_fallback_service import ModelFallbackService
        
        # 创建服务实例
        service = ModelFallbackService()
        
        # 验证模型名称来自环境变量
        high_precision_model = service.model_configs[ModelTier.HIGH_PRECISION].name
        fast_response_model = service.model_configs[ModelTier.FAST_RESPONSE].name
        
        assert high_precision_model == os.getenv("DEEPSEEK_SERIES_V3", "deepseek-v3")
        assert fast_response_model == os.getenv("QWEN_FAST", "qwen-turbo")
    
    @pytest.mark.asyncio
    async def test_async_model_call(self, mock_env_vars):
        """测试异步模型调用"""
        with patch('src.aurawell.core.deepseek_client.OpenAI') as mock_openai:
            # 模拟异步响应
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "异步测试响应"
            mock_response.choices[0].finish_reason = "stop"
            mock_response.model = "deepseek-v3"
            
            mock_openai_instance = MagicMock()
            mock_openai_instance.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_openai_instance
            
            client = DeepSeekClient()
            
            # 模拟异步调用
            async def async_call():
                return client.get_deepseek_response(
                    messages=[{"role": "user", "content": "异步测试"}],
                    model_name="deepseek-v3"
                )
            
            response = await async_call()
            assert response.content == "异步测试响应"
    
    def test_model_configuration_validation(self, mock_env_vars):
        """测试模型配置验证"""
        # 测试无效的环境变量
        with patch.dict(os.environ, {'DEEPSEEK_SERIES_V3': ''}):
            from src.aurawell.services.model_fallback_service import ModelFallbackService
            service = ModelFallbackService()
            
            # 应该使用默认值
            config = service.model_configs[ModelTier.HIGH_PRECISION]
            assert config.name == "deepseek-v3"  # 默认值
    
    def test_integration_with_health_advice_service(self, mock_env_vars):
        """测试与健康建议服务的集成"""
        from src.aurawell.langchain_agent.services.health_advice_service import MODEL_CONFIG
        
        # 验证健康建议服务使用正确的模型配置
        assert MODEL_CONFIG["reasoning_tasks"] == os.getenv("DEEPSEEK_SERIES_V3", "deepseek-v3")
        assert MODEL_CONFIG["chat_tasks"] == os.getenv("DEEPSEEK_SERIES_V3", "deepseek-v3")
        assert MODEL_CONFIG["default"] == os.getenv("DEEPSEEK_SERIES_V3", "deepseek-v3")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
