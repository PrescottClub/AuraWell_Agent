"""
测试ServiceClientFactory功能
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import sys
import logging

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aurawell.core.service_factory import (
    ServiceClientFactory, 
    MockDeepSeekClient, 
    get_deepseek_client,
    AIClientProtocol
)
from aurawell.core.deepseek_client import DeepSeekResponse

# 配置测试日志
logging.basicConfig(level=logging.INFO)


class TestMockDeepSeekClient:
    """测试MockDeepSeekClient功能"""
    
    def test_mock_client_initialization(self):
        """测试Mock客户端初始化"""
        client = MockDeepSeekClient()
        assert client.is_mock is True
    
    def test_mock_response_generation(self):
        """测试Mock响应生成"""
        client = MockDeepSeekClient()
        
        messages = [
            {"role": "system", "content": "你是健康助手"},
            {"role": "user", "content": "我想了解健康饮食"}
        ]
        
        response = client.get_deepseek_response(messages=messages)
        
        # 验证响应结构
        assert isinstance(response, DeepSeekResponse)
        assert response.content is not None
        assert "饮食" in response.content or "Mock响应" in response.content
        assert response.model == "deepseek-v3-mock"
        assert response.finish_reason == "stop"
        assert response.usage is None  # Mock模式不计算token
    
    def test_mock_tool_calls(self):
        """测试Mock工具调用"""
        client = MockDeepSeekClient()
        
        tools = [
            {
                "function": {
                    "name": "get_health_data",
                    "description": "获取健康数据"
                }
            }
        ]
        
        messages = [{"role": "user", "content": "获取我的健康数据"}]
        
        response = client.get_deepseek_response(
            messages=messages, 
            tools=tools
        )
        
        # 验证工具调用
        assert response.tool_calls is not None
        assert len(response.tool_calls) > 0
        assert response.tool_calls[0]["type"] == "function"
        assert "get_health_data" in response.tool_calls[0]["function"]["name"]
    
    @pytest.mark.asyncio
    async def test_mock_streaming_response(self):
        """测试Mock流式响应"""
        client = MockDeepSeekClient()
        
        messages = [{"role": "user", "content": "健康建议"}]
        
        response_chunks = []
        async for chunk in client.get_streaming_response(messages=messages):
            response_chunks.append(chunk)
        
        # 验证流式响应
        assert len(response_chunks) > 0
        full_response = "".join(response_chunks)
        assert "Mock响应" in full_response or "健康" in full_response


class TestServiceClientFactory:
    """测试ServiceClientFactory功能"""
    
    def setup_method(self):
        """每个测试前重置工厂状态"""
        ServiceClientFactory.reset_clients()
    
    def test_factory_with_no_api_key(self):
        """测试没有API Key时使用Mock客户端"""
        with patch.dict(os.environ, {}, clear=True):
            client = ServiceClientFactory.get_deepseek_client()
            
            # 验证返回Mock客户端
            assert isinstance(client, MockDeepSeekClient)
            assert hasattr(client, 'is_mock')
            assert client.is_mock is True
            
            # 验证服务状态
            status = ServiceClientFactory.get_service_status()
            assert 'deepseek' in status
            assert status['deepseek']['status'] == 'mock'
            assert status['deepseek']['type'] == 'mock'
            assert status['deepseek']['api_key_configured'] is False
    
    @patch('aurawell.core.service_factory.DeepSeekClient')
    def test_factory_with_api_key_success(self, mock_deepseek_class):
        """测试有API Key且初始化成功时使用真实客户端"""
        # 模拟真实客户端
        mock_client = MagicMock()
        mock_deepseek_class.return_value = mock_client
        
        with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'test-api-key'}):
            client = ServiceClientFactory.get_deepseek_client()
            
            # 验证返回真实客户端
            assert client == mock_client
            mock_deepseek_class.assert_called_once_with(api_key='test-api-key')
            
            # 验证服务状态
            status = ServiceClientFactory.get_service_status()
            assert status['deepseek']['status'] == 'live'
            assert status['deepseek']['type'] == 'real'
            assert status['deepseek']['api_key_configured'] is True
    
    @patch('aurawell.core.service_factory.DeepSeekClient')
    def test_factory_with_api_key_failure(self, mock_deepseek_class):
        """测试有API Key但初始化失败时回退到Mock客户端"""
        # 模拟真实客户端初始化失败
        mock_deepseek_class.side_effect = Exception("API初始化失败")
        
        with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'invalid-key'}):
            client = ServiceClientFactory.get_deepseek_client()
            
            # 验证回退到Mock客户端
            assert isinstance(client, MockDeepSeekClient)
            
            # 验证服务状态
            status = ServiceClientFactory.get_service_status()
            assert status['deepseek']['status'] == 'mock'
            assert status['deepseek']['type'] == 'fallback'
            assert status['deepseek']['api_key_configured'] is True
            assert 'error' in status['deepseek']
    
    def test_factory_singleton_behavior(self):
        """测试工厂单例行为"""
        with patch.dict(os.environ, {}, clear=True):
            client1 = ServiceClientFactory.get_deepseek_client()
            client2 = ServiceClientFactory.get_deepseek_client()
            
            # 验证返回同一个实例
            assert client1 is client2
    
    def test_multiple_api_key_sources(self):
        """测试多个API Key来源的优先级"""
        with patch.dict(os.environ, {
            'DASHSCOPE_API_KEY': 'dashscope-key',
            'QWEN_API': 'qwen-key',
            'DEEP_SEEK_API': 'deepseek-key'
        }):
            # 应该优先使用DASHSCOPE_API_KEY
            with patch('aurawell.core.service_factory.DeepSeekClient') as mock_class:
                ServiceClientFactory.get_deepseek_client()
                mock_class.assert_called_once_with(api_key='dashscope-key')
    
    def test_service_status_tracking(self):
        """测试服务状态跟踪"""
        with patch.dict(os.environ, {}, clear=True):
            # 获取客户端触发状态更新
            ServiceClientFactory.get_deepseek_client()
            
            status = ServiceClientFactory.get_service_status()
            
            # 验证状态信息完整性
            assert 'deepseek' in status
            deepseek_status = status['deepseek']
            
            required_fields = ['name', 'status', 'type', 'api_key_configured', 'last_updated']
            for field in required_fields:
                assert field in deepseek_status
            
            assert deepseek_status['name'] == 'DeepSeek AI'
    
    def test_convenience_function(self):
        """测试便捷函数"""
        with patch.dict(os.environ, {}, clear=True):
            client = get_deepseek_client()
            assert isinstance(client, MockDeepSeekClient)


class TestAIClientProtocol:
    """测试AI客户端协议"""
    
    def test_mock_client_implements_protocol(self):
        """测试Mock客户端实现了协议"""
        client = MockDeepSeekClient()
        assert isinstance(client, AIClientProtocol)
    
    def test_protocol_methods_exist(self):
        """测试协议方法存在"""
        client = MockDeepSeekClient()
        
        # 验证必需方法存在
        assert hasattr(client, 'get_deepseek_response')
        assert hasattr(client, 'get_streaming_response')
        assert callable(client.get_deepseek_response)
        assert callable(client.get_streaming_response)


if __name__ == "__main__":
    # 运行基本测试
    pytest.main([__file__, "-v"])
