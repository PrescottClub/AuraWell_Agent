"""
测试服务状态API功能
"""

import os
import pytest
from unittest.mock import patch
import sys
import logging

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aurawell.core.service_factory import ServiceClientFactory
from aurawell.interfaces.service_status_api import (
    get_current_service_status,
    is_zero_config_mode,
    get_live_services,
    get_mock_services
)

# 配置测试日志
logging.basicConfig(level=logging.INFO)


class TestServiceStatusAPI:
    """测试服务状态API功能"""
    
    def setup_method(self):
        """每个测试前重置工厂状态"""
        ServiceClientFactory.reset_clients()
    
    def test_get_current_service_status(self):
        """测试获取当前服务状态"""
        with patch.dict(os.environ, {}, clear=True):
            # 触发服务初始化
            ServiceClientFactory.get_deepseek_client()
            ServiceClientFactory.get_mcp_tools_interface()
            
            status = get_current_service_status()
            
            # 验证状态结构
            assert isinstance(status, dict)
            assert 'deepseek' in status
            assert 'mcp_tools' in status
            
            # 验证DeepSeek状态
            deepseek_status = status['deepseek']
            assert deepseek_status['name'] == 'DeepSeek AI'
            assert deepseek_status['status'] == 'mock'
            assert deepseek_status['type'] == 'mock'
            assert deepseek_status['api_key_configured'] is False
            
            # 验证MCP工具状态
            mcp_status = status['mcp_tools']
            assert mcp_status['name'] == 'MCP Tools'
            assert mcp_status['status'] == 'mock'
            assert mcp_status['type'] == 'mock'
    
    def test_is_zero_config_mode(self):
        """测试零配置模式检测"""
        with patch.dict(os.environ, {}, clear=True):
            # 触发服务初始化
            ServiceClientFactory.get_deepseek_client()
            ServiceClientFactory.get_mcp_tools_interface()
            
            # 验证零配置模式
            assert is_zero_config_mode() is True
    
    def test_is_not_zero_config_mode(self):
        """测试非零配置模式检测"""
        with patch('aurawell.core.service_factory.DeepSeekClient') as mock_deepseek:
            mock_deepseek.return_value = mock_deepseek
            
            with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'test-key'}):
                # 触发服务初始化
                ServiceClientFactory.get_deepseek_client()
                ServiceClientFactory.get_mcp_tools_interface()
                
                # 验证非零配置模式
                assert is_zero_config_mode() is False
    
    def test_get_live_services(self):
        """测试获取真实服务列表"""
        with patch('aurawell.core.service_factory.DeepSeekClient') as mock_deepseek:
            mock_deepseek.return_value = mock_deepseek
            
            with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'test-key'}):
                # 触发服务初始化
                ServiceClientFactory.get_deepseek_client()
                ServiceClientFactory.get_mcp_tools_interface()
                
                live_services = get_live_services()
                
                # 验证真实服务列表
                assert 'deepseek' in live_services
                assert 'mcp_tools' not in live_services  # MCP工具仍然是Mock
    
    def test_get_mock_services(self):
        """测试获取Mock服务列表"""
        with patch.dict(os.environ, {}, clear=True):
            # 触发服务初始化
            ServiceClientFactory.get_deepseek_client()
            ServiceClientFactory.get_mcp_tools_interface()
            
            mock_services = get_mock_services()
            
            # 验证Mock服务列表
            assert 'deepseek' in mock_services
            assert 'mcp_tools' in mock_services
            assert len(mock_services) == 2
    
    def test_mixed_service_configuration(self):
        """测试混合服务配置"""
        with patch('aurawell.core.service_factory.DeepSeekClient') as mock_deepseek:
            mock_deepseek.return_value = mock_deepseek
            
            with patch.dict(os.environ, {
                'DASHSCOPE_API_KEY': 'test-deepseek-key',
                # MCP工具没有API Key，应该使用Mock
            }):
                # 触发服务初始化
                ServiceClientFactory.get_deepseek_client()
                ServiceClientFactory.get_mcp_tools_interface()
                
                status = get_current_service_status()
                live_services = get_live_services()
                mock_services = get_mock_services()
                
                # 验证混合配置
                assert not is_zero_config_mode()
                assert 'deepseek' in live_services
                assert 'mcp_tools' in mock_services
                assert status['deepseek']['status'] == 'live'
                assert status['mcp_tools']['status'] == 'mock'
    
    def test_service_status_after_reset(self):
        """测试重置后的服务状态"""
        with patch.dict(os.environ, {}, clear=True):
            # 初始化服务
            ServiceClientFactory.get_deepseek_client()
            ServiceClientFactory.get_mcp_tools_interface()
            
            # 验证初始状态
            initial_status = get_current_service_status()
            assert len(initial_status) == 2
            
            # 重置服务
            ServiceClientFactory.reset_clients()
            
            # 重新初始化
            ServiceClientFactory.get_deepseek_client()
            ServiceClientFactory.get_mcp_tools_interface()
            
            # 验证重置后状态
            reset_status = get_current_service_status()
            assert len(reset_status) == 2
            assert reset_status['deepseek']['status'] == 'mock'
            assert reset_status['mcp_tools']['status'] == 'mock'
    
    def test_service_status_with_api_key_priority(self):
        """测试API Key优先级"""
        with patch('aurawell.core.service_factory.DeepSeekClient') as mock_deepseek:
            mock_deepseek.return_value = mock_deepseek
            
            with patch.dict(os.environ, {
                'DASHSCOPE_API_KEY': 'dashscope-key',
                'QWEN_API': 'qwen-key',
                'DEEP_SEEK_API': 'deepseek-key'
            }):
                # 触发服务初始化
                ServiceClientFactory.get_deepseek_client()
                
                # 验证使用了正确的API Key优先级
                mock_deepseek.assert_called_once_with(api_key='dashscope-key')
                
                status = get_current_service_status()
                assert status['deepseek']['status'] == 'live'
    
    def test_service_status_error_handling(self):
        """测试服务状态错误处理"""
        with patch('aurawell.core.service_factory.DeepSeekClient') as mock_deepseek:
            # 模拟初始化失败
            mock_deepseek.side_effect = Exception("API初始化失败")
            
            with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'invalid-key'}):
                # 触发服务初始化
                ServiceClientFactory.get_deepseek_client()
                
                status = get_current_service_status()
                
                # 验证错误处理
                assert status['deepseek']['status'] == 'mock'
                assert status['deepseek']['type'] == 'fallback'
                assert 'error' in status['deepseek']
                assert 'API初始化失败' in status['deepseek']['error']


class TestServiceStatusHelpers:
    """测试服务状态辅助函数"""
    
    def setup_method(self):
        """每个测试前重置工厂状态"""
        ServiceClientFactory.reset_clients()
    
    def test_zero_config_detection(self):
        """测试零配置检测"""
        with patch.dict(os.environ, {}, clear=True):
            # 初始化服务
            ServiceClientFactory.get_deepseek_client()
            ServiceClientFactory.get_mcp_tools_interface()
            
            # 验证零配置检测
            assert is_zero_config_mode() is True
            assert len(get_live_services()) == 0
            assert len(get_mock_services()) == 2
    
    def test_partial_config_detection(self):
        """测试部分配置检测"""
        with patch('aurawell.langchain_agent.mcp_interface.MCPToolInterface') as mock_mcp:
            mock_mcp.return_value = mock_mcp
            
            with patch.dict(os.environ, {'BRAVE_API_KEY': 'test-brave-key'}):
                # 初始化服务
                ServiceClientFactory.get_deepseek_client()
                ServiceClientFactory.get_mcp_tools_interface()
                
                # 验证部分配置检测
                assert is_zero_config_mode() is False
                live_services = get_live_services()
                mock_services = get_mock_services()
                
                assert 'mcp_tools' in live_services
                assert 'deepseek' in mock_services


if __name__ == "__main__":
    # 运行服务状态API测试
    pytest.main([__file__, "-v"])
