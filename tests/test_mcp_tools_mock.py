"""
测试MCP工具Mock功能
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys
import logging

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aurawell.core.service_factory import (
    ServiceClientFactory, 
    MockMCPToolInterface, 
    get_mcp_tools_interface,
    MCPToolProtocol
)

# 配置测试日志
logging.basicConfig(level=logging.INFO)


class TestMockMCPToolInterface:
    """测试MockMCPToolInterface功能"""
    
    def test_mock_interface_initialization(self):
        """测试Mock接口初始化"""
        interface = MockMCPToolInterface()
        assert interface.is_mock is True
        assert len(interface.available_tools) == 13
        
        # 验证包含所有预期工具
        expected_tools = [
            'database-sqlite', 'calculator', 'quickchart', 'brave-search',
            'fetch', 'sequential-thinking', 'memory', 'weather', 'time',
            'run-python', 'github', 'filesystem', 'figma'
        ]
        for tool in expected_tools:
            assert tool in interface.available_tools
    
    @pytest.mark.asyncio
    async def test_mock_database_tool(self):
        """测试Mock数据库工具"""
        interface = MockMCPToolInterface()
        
        # 测试查询操作
        result = await interface.call_tool(
            'database-sqlite', 
            'query', 
            {'sql': 'SELECT * FROM users'}
        )
        
        assert result['success'] is True
        assert result['is_mock'] is True
        assert result['tool_name'] == 'database-sqlite'
        assert 'data' in result
        assert isinstance(result['data'], list)
        assert len(result['data']) == 2  # Mock返回2条记录
    
    @pytest.mark.asyncio
    async def test_mock_calculator_tool(self):
        """测试Mock计算器工具"""
        interface = MockMCPToolInterface()
        
        result = await interface.call_tool(
            'calculator', 
            'calculate', 
            {'expression': '2+2'}
        )
        
        assert result['success'] is True
        assert result['is_mock'] is True
        assert result['data']['result'] == 4.0
        assert result['data']['expression'] == '2+2'
    
    @pytest.mark.asyncio
    async def test_mock_search_tool(self):
        """测试Mock搜索工具"""
        interface = MockMCPToolInterface()
        
        result = await interface.call_tool(
            'brave-search', 
            'search', 
            {'query': 'health tips', 'count': 5}
        )
        
        assert result['success'] is True
        assert result['is_mock'] is True
        assert 'results' in result['data']
        assert len(result['data']['results']) == 2  # Mock返回2个结果
        assert result['data']['query'] == 'health tips'
    
    @pytest.mark.asyncio
    async def test_mock_weather_tool(self):
        """测试Mock天气工具"""
        interface = MockMCPToolInterface()
        
        result = await interface.call_tool(
            'weather', 
            'get_weather', 
            {'location': '上海'}
        )
        
        assert result['success'] is True
        assert result['is_mock'] is True
        assert result['data']['location'] == '上海'
        assert 'temperature' in result['data']
        assert 'weather' in result['data']
    
    @pytest.mark.asyncio
    async def test_mock_memory_tool(self):
        """测试Mock记忆工具"""
        interface = MockMCPToolInterface()
        
        # 测试存储
        store_result = await interface.call_tool(
            'memory', 
            'store', 
            {'content': 'test memory'}
        )
        
        assert store_result['success'] is True
        assert store_result['data']['stored'] is True
        
        # 测试检索
        retrieve_result = await interface.call_tool(
            'memory', 
            'retrieve', 
            {'query': 'test'}
        )
        
        assert retrieve_result['success'] is True
        assert 'memories' in retrieve_result['data']
    
    @pytest.mark.asyncio
    async def test_unknown_tool_error(self):
        """测试未知工具错误处理"""
        interface = MockMCPToolInterface()
        
        result = await interface.call_tool(
            'unknown-tool', 
            'action', 
            {}
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert '未知工具' in result['error']
    
    def test_tool_status(self):
        """测试工具状态"""
        interface = MockMCPToolInterface()
        status = interface.get_tool_status()
        
        assert status['total_tools'] == 13
        assert status['status'] == 'mock'
        assert status['all_tools_available'] is True
        assert status['is_mock'] is True


class TestServiceFactoryMCPIntegration:
    """测试ServiceFactory与MCP工具集成"""
    
    def setup_method(self):
        """每个测试前重置工厂状态"""
        ServiceClientFactory.reset_clients()
    
    def test_factory_with_no_mcp_api_keys(self):
        """测试没有MCP API Key时使用Mock接口"""
        with patch.dict(os.environ, {}, clear=True):
            interface = ServiceClientFactory.get_mcp_tools_interface()
            
            # 验证返回Mock接口
            assert isinstance(interface, MockMCPToolInterface)
            assert hasattr(interface, 'is_mock')
            assert interface.is_mock is True
            
            # 验证服务状态
            status = ServiceClientFactory.get_service_status()
            assert 'mcp_tools' in status
            assert status['mcp_tools']['status'] == 'mock'
            assert status['mcp_tools']['type'] == 'mock'
    
    def test_factory_with_mcp_api_keys_success(self):
        """测试有MCP API Key且初始化成功时使用真实接口"""
        # 模拟真实接口导入和初始化成功
        with patch('aurawell.langchain_agent.mcp_interface.MCPToolInterface') as mock_mcp_class:
            mock_interface = MagicMock()
            mock_mcp_class.return_value = mock_interface

            with patch.dict(os.environ, {'BRAVE_API_KEY': 'test-brave-key'}):
                interface = ServiceClientFactory.get_mcp_tools_interface()

                # 验证返回真实接口
                assert interface == mock_interface

                # 验证服务状态
                status = ServiceClientFactory.get_service_status()
                assert status['mcp_tools']['status'] == 'live'
                assert status['mcp_tools']['type'] == 'real'

    def test_factory_with_mcp_api_keys_failure(self):
        """测试有MCP API Key但初始化失败时回退到Mock接口"""
        # 模拟真实接口初始化失败
        with patch('aurawell.langchain_agent.mcp_interface.MCPToolInterface') as mock_mcp_class:
            mock_mcp_class.side_effect = Exception("MCP初始化失败")

            with patch.dict(os.environ, {'BRAVE_API_KEY': 'invalid-key'}):
                interface = ServiceClientFactory.get_mcp_tools_interface()

                # 验证回退到Mock接口
                assert isinstance(interface, MockMCPToolInterface)

                # 验证服务状态
                status = ServiceClientFactory.get_service_status()
                assert status['mcp_tools']['status'] == 'mock'
                assert status['mcp_tools']['type'] == 'fallback'
                assert 'error' in status['mcp_tools']
    
    def test_mcp_singleton_behavior(self):
        """测试MCP接口单例行为"""
        with patch.dict(os.environ, {}, clear=True):
            interface1 = ServiceClientFactory.get_mcp_tools_interface()
            interface2 = ServiceClientFactory.get_mcp_tools_interface()
            
            # 验证返回同一个实例
            assert interface1 is interface2
    
    def test_convenience_function(self):
        """测试便捷函数"""
        with patch.dict(os.environ, {}, clear=True):
            interface = get_mcp_tools_interface()
            assert isinstance(interface, MockMCPToolInterface)
    
    def test_protocol_compliance(self):
        """测试协议兼容性"""
        interface = MockMCPToolInterface()
        assert isinstance(interface, MCPToolProtocol)
    
    @pytest.mark.asyncio
    async def test_integrated_tool_call(self):
        """测试集成工具调用"""
        with patch.dict(os.environ, {}, clear=True):
            interface = ServiceClientFactory.get_mcp_tools_interface()
            
            # 测试工具调用
            result = await interface.call_tool(
                'calculator', 
                'calculate', 
                {'expression': '10*5'}
            )
            
            assert result['success'] is True
            assert result['is_mock'] is True
            assert result['tool_name'] == 'calculator'


if __name__ == "__main__":
    # 运行MCP工具测试
    pytest.main([__file__, "-v"])
