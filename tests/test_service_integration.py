"""
测试ServiceClientFactory与现有服务的集成
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import sys
import logging

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aurawell.core.service_factory import ServiceClientFactory, MockDeepSeekClient
from aurawell.langchain_agent.services.health_advice_service import HealthAdviceService
from aurawell.core.orchestrator_v2 import AuraWellOrchestrator

# 配置测试日志
logging.basicConfig(level=logging.INFO)


class TestServiceIntegration:
    """测试服务集成功能"""
    
    def setup_method(self):
        """每个测试前重置工厂状态"""
        ServiceClientFactory.reset_clients()
    
    def test_health_advice_service_with_mock_client(self):
        """测试HealthAdviceService使用Mock客户端"""
        with patch.dict(os.environ, {}, clear=True):
            # 初始化服务
            service = HealthAdviceService()
            
            # 验证使用了Mock客户端
            assert service.deepseek_client is not None
            assert isinstance(service.deepseek_client, MockDeepSeekClient)
            assert hasattr(service.deepseek_client, 'is_mock')
            assert service.deepseek_client.is_mock is True
    
    @patch('aurawell.core.service_factory.DeepSeekClient')
    def test_health_advice_service_with_real_client(self, mock_deepseek_class):
        """测试HealthAdviceService使用真实客户端"""
        # 模拟真实客户端
        mock_client = MagicMock()
        mock_deepseek_class.return_value = mock_client
        
        with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'test-api-key'}):
            # 初始化服务
            service = HealthAdviceService()
            
            # 验证使用了真实客户端
            assert service.deepseek_client is not None
            assert service.deepseek_client == mock_client
            
            # 验证工厂被正确调用
            mock_deepseek_class.assert_called_once_with(api_key='test-api-key')
    
    def test_orchestrator_with_mock_client(self):
        """测试AuraWellOrchestrator使用Mock客户端"""
        with patch.dict(os.environ, {}, clear=True):
            # 初始化编排器
            orchestrator = AuraWellOrchestrator()
            
            # 验证使用了Mock客户端
            assert orchestrator.deepseek_client is not None
            assert isinstance(orchestrator.deepseek_client, MockDeepSeekClient)
    
    @patch('aurawell.core.service_factory.DeepSeekClient')
    def test_orchestrator_with_real_client(self, mock_deepseek_class):
        """测试AuraWellOrchestrator使用真实客户端"""
        # 模拟真实客户端
        mock_client = MagicMock()
        mock_deepseek_class.return_value = mock_client
        
        with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'test-api-key'}):
            # 初始化编排器
            orchestrator = AuraWellOrchestrator()
            
            # 验证使用了真实客户端
            assert orchestrator.deepseek_client is not None
            assert orchestrator.deepseek_client == mock_client
    
    def test_multiple_services_share_same_client(self):
        """测试多个服务共享同一个客户端实例"""
        with patch.dict(os.environ, {}, clear=True):
            # 初始化多个服务
            service1 = HealthAdviceService()
            orchestrator = AuraWellOrchestrator()
            
            # 验证它们使用同一个客户端实例（单例模式）
            assert service1.deepseek_client is orchestrator.deepseek_client
    
    def test_service_status_tracking_integration(self):
        """测试服务状态跟踪集成"""
        with patch.dict(os.environ, {}, clear=True):
            # 初始化服务触发客户端创建
            service = HealthAdviceService()
            
            # 获取服务状态
            status = ServiceClientFactory.get_service_status()
            
            # 验证状态信息
            assert 'deepseek' in status
            assert status['deepseek']['status'] == 'mock'
            assert status['deepseek']['type'] == 'mock'
            assert status['deepseek']['api_key_configured'] is False
    
    @patch('aurawell.core.service_factory.DeepSeekClient')
    def test_fallback_behavior_integration(self, mock_deepseek_class):
        """测试回退行为集成"""
        # 模拟真实客户端初始化失败
        mock_deepseek_class.side_effect = Exception("API初始化失败")
        
        with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'invalid-key'}):
            # 初始化服务
            service = HealthAdviceService()
            
            # 验证回退到Mock客户端
            assert service.deepseek_client is not None
            assert isinstance(service.deepseek_client, MockDeepSeekClient)
            
            # 验证服务状态反映了回退情况
            status = ServiceClientFactory.get_service_status()
            assert status['deepseek']['status'] == 'mock'
            assert status['deepseek']['type'] == 'fallback'
            assert 'error' in status['deepseek']
    
    def test_mock_client_response_integration(self):
        """测试Mock客户端响应集成"""
        with patch.dict(os.environ, {}, clear=True):
            # 初始化服务
            service = HealthAdviceService()
            
            # 测试Mock客户端响应
            messages = [
                {"role": "system", "content": "你是健康助手"},
                {"role": "user", "content": "我想了解健康饮食建议"}
            ]
            
            response = service.deepseek_client.get_deepseek_response(messages=messages)
            
            # 验证Mock响应
            assert response is not None
            assert response.content is not None
            assert "Mock响应" in response.content or "饮食" in response.content
            assert response.model == "deepseek-v3-mock"
    
    def test_environment_variable_priority_integration(self):
        """测试环境变量优先级集成"""
        with patch.dict(os.environ, {
            'DASHSCOPE_API_KEY': 'dashscope-key',
            'QWEN_API': 'qwen-key',
            'DEEP_SEEK_API': 'deepseek-key'
        }):
            with patch('aurawell.core.service_factory.DeepSeekClient') as mock_class:
                # 初始化服务
                service = HealthAdviceService()
                
                # 验证使用了正确的API Key优先级
                mock_class.assert_called_once_with(api_key='dashscope-key')


class TestServiceFactoryImports:
    """测试服务工厂导入功能"""

    def setup_method(self):
        """每个测试前重置工厂状态"""
        ServiceClientFactory.reset_clients()

    def test_core_module_imports(self):
        """测试核心模块导入"""
        from aurawell.core import ServiceClientFactory, get_deepseek_client

        # 验证导入成功
        assert ServiceClientFactory is not None
        assert get_deepseek_client is not None
        assert callable(get_deepseek_client)

    def test_convenience_function_works(self):
        """测试便捷函数工作正常"""
        from aurawell.core import get_deepseek_client

        with patch.dict(os.environ, {}, clear=True):
            client = get_deepseek_client()
            assert isinstance(client, MockDeepSeekClient)


if __name__ == "__main__":
    # 运行集成测试
    pytest.main([__file__, "-v"])
