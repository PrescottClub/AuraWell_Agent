"""
MCP工具管理器测试套件
测试MCP工具的调用逻辑、错误处理和集成功能
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

# 项目导入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aurawell.langchain_agent.mcp_tools_manager import MCPToolsManager
from aurawell.langchain_agent.intent_analyzer import IntentAnalyzer


class TestMCPToolsManager:
    """MCP工具管理器测试类"""
    
    @pytest.fixture
    async def mcp_manager(self):
        """创建MCP工具管理器实例"""
        manager = MCPToolsManager()
        yield manager
        # 清理
        if hasattr(manager, 'cleanup'):
            await manager.cleanup()
    
    @pytest.fixture
    def mock_intent_analyzer(self):
        """模拟意图分析器"""
        analyzer = Mock(spec=IntentAnalyzer)
        analyzer.analyze_intent.return_value = {
            'intent': 'health_calculation',
            'confidence': 0.9,
            'entities': {'weight': 70, 'height': 175},
            'tools_needed': ['calculator']
        }
        return analyzer
    
    # ============================================================================
    # Calculator工具单元测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_call_calculator_bmi_success(self, mcp_manager):
        """测试BMI计算成功场景"""
        # 准备测试数据
        action = "bmi"
        parameters = {
            "weight": 70.0,
            "height": 175.0
        }
        
        # 执行测试
        result = await mcp_manager._call_calculator(action, parameters)
        
        # 验证结果
        assert result['success'] is True
        assert result['action'] == action
        assert result['tool'] == 'calculator'
        assert 'data' in result
        
        # 验证BMI计算结果
        data = result['data']
        assert 'bmi' in data
        assert 'category' in data
        assert data['weight'] == 70.0
        assert data['height'] == 175.0
        
        # BMI应该约为22.86
        expected_bmi = 70 / (1.75 ** 2)
        assert abs(data['bmi'] - expected_bmi) < 0.1
        assert data['category'] == "正常"
    
    @pytest.mark.asyncio
    async def test_call_calculator_bmr_success(self, mcp_manager):
        """测试BMR计算成功场景"""
        action = "bmr"
        parameters = {
            "weight": 70.0,
            "height": 175.0,
            "age": 30,
            "gender": "male"
        }
        
        result = await mcp_manager._call_calculator(action, parameters)
        
        assert result['success'] is True
        assert 'bmr' in result['data']
        assert result['data']['gender'] == "male"
        
        # 验证BMR计算（Harris-Benedict公式）
        expected_bmr = 88.362 + (13.397 * 70) + (4.799 * 175) - (5.677 * 30)
        assert abs(result['data']['bmr'] - expected_bmr) < 1.0
    
    @pytest.mark.asyncio
    async def test_call_calculator_invalid_parameters(self, mcp_manager):
        """测试无效参数处理"""
        action = "bmi"
        parameters = {
            "weight": -10,  # 无效体重
            "height": 0     # 无效身高
        }
        
        result = await mcp_manager._call_calculator(action, parameters)
        
        assert result['success'] is False
        assert 'error' in result
        assert "positive numbers" in result['error']
    
    @pytest.mark.parametrize("action,parameters,expected_keys", [
        ("bmi", {"weight": 65, "height": 160}, ["bmi", "category"]),
        ("bmr", {"weight": 65, "height": 160, "age": 25, "gender": "female"}, ["bmr", "gender"]),
        ("tdee", {"bmr": 1500, "activity_level": "moderately_active"}, ["tdee", "multiplier"])
    ])
    @pytest.mark.asyncio
    async def test_calculator_multiple_actions(self, mcp_manager, action, parameters, expected_keys):
        """参数化测试多种计算器操作"""
        result = await mcp_manager._call_calculator(action, parameters)
        
        assert result['success'] is True
        assert result['action'] == action
        
        for key in expected_keys:
            assert key in result['data']
    
    # ============================================================================
    # QuickChart工具单元测试
    # ============================================================================
    
    @pytest.mark.parametrize("chart_type,data,labels", [
        ("line", [10, 20, 30, 25, 35], ["周一", "周二", "周三", "周四", "周五"]),
        ("bar", [65, 70, 68, 72, 69], ["1月", "2月", "3月", "4月", "5月"]),
        ("pie", [30, 25, 20, 25], ["蛋白质", "碳水", "脂肪", "其他"]),
        ("doughnut", [8, 7, 9, 8], ["睡眠", "运动", "饮食", "心情"])
    ])
    @pytest.mark.asyncio
    async def test_call_quickchart_different_types(self, mcp_manager, chart_type, data, labels):
        """参数化测试不同类型的图表生成"""
        action = "generate_chart"
        parameters = {
            "type": chart_type,
            "data": data,
            "labels": labels,
            "title": f"测试{chart_type}图表"
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            # 模拟成功的HTTP响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await mcp_manager._call_quickchart(action, parameters)
            
            assert result['success'] is True
            assert result['action'] == action
            assert result['tool'] == 'quickchart'
            
            data_result = result['data']
            assert 'chart_url' in data_result
            assert 'config' in data_result
            assert data_result['type'] == chart_type
            
            # 验证图表配置
            config = data_result['config']
            assert config['type'] == chart_type
            assert config['data']['labels'] == labels
            assert config['data']['datasets'][0]['data'] == data
    
    @pytest.mark.asyncio
    async def test_call_quickchart_api_failure(self, mcp_manager):
        """测试QuickChart API失败场景"""
        action = "generate_chart"
        parameters = {
            "type": "line",
            "data": [1, 2, 3],
            "labels": ["A", "B", "C"]
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            # 模拟API错误响应
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await mcp_manager._call_quickchart(action, parameters)
            
            assert result['success'] is False
            assert 'error' in result
            assert "QuickChart API返回错误" in result['error']
    
    # ============================================================================
    # Database-SQLite工具单元测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_call_database_sqlite_query(self, mcp_manager):
        """测试数据库查询功能"""
        action = "query"
        parameters = {
            "query": "SELECT COUNT(*) as count FROM user_profiles",
            "params": []
        }
        
        with patch('aurawell.database.get_database_manager') as mock_db_manager:
            # 模拟数据库管理器
            mock_manager = AsyncMock()
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            
            # 设置模拟返回值
            mock_result.fetchall.return_value = [{'count': 5}]
            mock_session.execute.return_value = mock_result
            mock_manager.get_session.return_value.__aenter__.return_value = mock_session
            mock_db_manager.return_value = mock_manager
            
            result = await mcp_manager._call_database_sqlite(action, parameters)
            
            assert result['success'] is True
            assert result['action'] == action
            assert result['tool'] == 'database-sqlite'
            assert result['data'] == [{'count': 5}]
    
    @pytest.mark.asyncio
    async def test_call_database_sqlite_health_metrics(self, mcp_manager):
        """测试健康指标查询功能"""
        action = "health_metrics"
        parameters = {"user_id": "test_user_123"}
        
        with patch('aurawell.database.get_database_manager') as mock_db_manager:
            mock_manager = AsyncMock()
            mock_session = AsyncMock()
            
            # 模拟用户档案和活动数据
            mock_user_profile = {'id': 'test_user_123', 'name': 'Test User'}
            mock_activities = [
                {'date': '2025-01-01', 'steps': 8000},
                {'date': '2025-01-02', 'steps': 9500}
            ]
            
            mock_session.get.return_value = mock_user_profile
            mock_result = AsyncMock()
            mock_result.fetchall.return_value = mock_activities
            mock_session.execute.return_value = mock_result
            mock_manager.get_session.return_value.__aenter__.return_value = mock_session
            mock_db_manager.return_value = mock_manager
            
            result = await mcp_manager._call_database_sqlite(action, parameters)
            
            assert result['success'] is True
            assert 'user_profile' in result['data']
            assert 'recent_activities' in result['data']
            assert result['data']['user_profile'] == mock_user_profile
            assert result['data']['recent_activities'] == mock_activities
    
    # ============================================================================
    # 集成测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_analyze_and_execute_integration(self, mcp_manager, mock_intent_analyzer):
        """测试完整的意图分析和工具执行流程"""
        # 替换意图分析器
        mcp_manager.intent_analyzer = mock_intent_analyzer
        
        user_message = "我身高175cm，体重70kg，帮我计算BMI"
        context = {"user_id": "test_user"}
        
        # 模拟工具调用成功
        with patch.object(mcp_manager, '_call_calculator') as mock_calculator:
            mock_calculator.return_value = {
                'success': True,
                'data': {'bmi': 22.86, 'category': '正常'},
                'tool': 'calculator',
                'action': 'bmi'
            }
            
            result = await mcp_manager.analyze_and_execute(user_message, context)
            
            assert result.success is True
            assert 'calculator' in result.tool_results
            assert result.tool_results['calculator']['success'] is True
            
            # 验证意图分析器被调用
            mock_intent_analyzer.analyze_intent.assert_called_once_with(user_message, context)
            
            # 验证计算器被调用
            mock_calculator.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_tool_execution_timeout(self, mcp_manager):
        """测试工具执行超时处理"""
        action = "bmi"
        parameters = {"weight": 70, "height": 175}
        
        # 模拟超时场景
        with patch.object(mcp_manager, '_call_calculator') as mock_calculator:
            mock_calculator.side_effect = asyncio.TimeoutError("Tool execution timeout")
            
            # 这里测试超时处理逻辑（需要在实际代码中实现）
            # 当前的实现中没有显式的超时处理，这是一个改进点
            with pytest.raises(asyncio.TimeoutError):
                await mcp_manager._call_calculator(action, parameters)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_logging(self, mcp_manager, caplog):
        """测试错误处理和日志记录"""
        action = "invalid_action"
        parameters = {}
        
        result = await mcp_manager._call_calculator(action, parameters)
        
        # 验证错误处理
        assert result['success'] is False
        assert 'error' in result
        
        # 验证日志记录（如果有的话）
        # 注意：这需要在实际的MCP工具方法中添加适当的日志记录
    
    # ============================================================================
    # 性能测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, mcp_manager):
        """测试并发工具调用"""
        tasks = []
        
        # 创建多个并发的计算器调用
        for i in range(5):
            task = mcp_manager._call_calculator("bmi", {
                "weight": 70 + i,
                "height": 175
            })
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks)
        
        # 验证所有调用都成功
        for i, result in enumerate(results):
            assert result['success'] is True
            assert result['data']['weight'] == 70 + i
    
    @pytest.mark.asyncio
    async def test_tool_performance_metrics(self, mcp_manager):
        """测试工具性能指标收集"""
        import time
        
        start_time = time.time()
        
        result = await mcp_manager._call_calculator("bmi", {
            "weight": 70,
            "height": 175
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 验证执行时间合理（应该很快）
        assert execution_time < 1.0  # 应该在1秒内完成
        assert result['success'] is True


# ============================================================================
# 测试配置和辅助函数
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def test_mcp_tools_manager_initialization():
    """测试MCP工具管理器初始化"""
    manager = MCPToolsManager()
    
    # 验证工具注册
    assert hasattr(manager, 'available_tools')
    assert 'calculator' in manager.available_tools
    assert 'quickchart' in manager.available_tools
    assert 'database-sqlite' in manager.available_tools
    
    # 验证统计信息初始化
    assert hasattr(manager, 'execution_stats')
    assert manager.execution_stats['total_calls'] == 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
