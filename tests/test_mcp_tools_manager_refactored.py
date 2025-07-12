"""
重构后MCP工具管理器测试套件
专门测试重构后的通用执行框架和新架构
"""

import pytest
import asyncio
import logging
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

# 项目导入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from aurawell.langchain_agent.mcp_tools_manager import MCPToolsManager


class TestMCPToolsManagerRefactored:
    """重构后MCP工具管理器测试类"""
    
    @pytest.fixture
    def mcp_manager(self):
        """创建MCP工具管理器实例"""
        manager = MCPToolsManager()
        return manager
    
    @pytest.fixture
    def mock_logger(self, mocker):
        """模拟日志记录器"""
        return mocker.patch('aurawell.langchain_agent.mcp_tools_manager.logger')
    
    # ============================================================================
    # 核心测试：通用执行框架 _execute_tool_with_error_handling
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_error_handling_success(self, mcp_manager, mock_logger):
        """测试通用执行框架成功场景"""
        # 准备模拟的工具执行器
        mock_executor = AsyncMock()
        mock_executor.return_value = {"result": "success", "value": 42}
        
        # 执行测试
        result = await mcp_manager._execute_tool_with_error_handling(
            tool_name="test_tool",
            action="test_action", 
            parameters={"param1": "value1"},
            tool_executor=mock_executor
        )
        
        # 验证结果结构
        assert result['success'] is True
        assert result['tool'] == "test_tool"
        assert result['action'] == "test_action"
        assert result['data'] == {"result": "success", "value": 42}
        assert 'execution_time_ms' in result
        assert isinstance(result['execution_time_ms'], float)
        
        # 验证工具执行器被正确调用
        mock_executor.assert_called_once_with("test_action", {"param1": "value1"})
        
        # 验证日志记录
        mock_logger.debug.assert_called_once()
        mock_logger.info.assert_called_once()
        assert "工具执行成功" in mock_logger.info.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_error_handling_failure(self, mcp_manager, mock_logger):
        """测试通用执行框架异常处理"""
        # 准备抛出异常的工具执行器
        mock_executor = AsyncMock()
        mock_executor.side_effect = ValueError("模拟工具执行失败")
        
        # 执行测试
        result = await mcp_manager._execute_tool_with_error_handling(
            tool_name="failing_tool",
            action="fail_action",
            parameters={"param1": "value1"},
            tool_executor=mock_executor
        )
        
        # 验证错误结果结构
        assert result['success'] is False
        assert result['tool'] == "failing_tool"
        assert result['action'] == "fail_action"
        assert result['error'] == "模拟工具执行失败"
        assert 'execution_time_ms' in result
        
        # 验证错误日志记录
        mock_logger.error.assert_called_once()
        assert "failing_tool工具调用失败" in mock_logger.error.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_error_handling_performance_tracking(self, mcp_manager):
        """测试通用执行框架的性能监控"""
        # 创建一个有延迟的工具执行器
        async def slow_executor(action, params):
            await asyncio.sleep(0.1)  # 100ms延迟
            return {"slow": "result"}
        
        # 执行测试
        result = await mcp_manager._execute_tool_with_error_handling(
            tool_name="slow_tool",
            action="slow_action",
            parameters={},
            tool_executor=slow_executor
        )
        
        # 验证执行时间被正确记录
        assert result['success'] is True
        assert result['execution_time_ms'] >= 100  # 至少100ms
        assert result['execution_time_ms'] < 200   # 但不应该太长
    
    @pytest.mark.parametrize("exception_type,expected_error", [
        (ValueError("参数错误"), "参数错误"),
        (RuntimeError("运行时错误"), "运行时错误"),
        (ConnectionError("连接失败"), "连接失败"),
        (TimeoutError("超时"), "超时")
    ])
    @pytest.mark.asyncio
    async def test_execute_tool_with_error_handling_various_exceptions(
        self, mcp_manager, exception_type, expected_error
    ):
        """参数化测试：验证不同异常类型的处理"""
        mock_executor = AsyncMock()
        mock_executor.side_effect = exception_type
        
        result = await mcp_manager._execute_tool_with_error_handling(
            tool_name="test_tool",
            action="test_action",
            parameters={},
            tool_executor=mock_executor
        )
        
        assert result['success'] is False
        assert result['error'] == expected_error
    
    # ============================================================================
    # 集成测试：重构后的工具方法
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_call_calculator_integration_with_framework(self, mcp_manager, mocker):
        """测试calculator工具与通用框架的集成"""
        # 模拟通用执行框架
        mock_framework = mocker.patch.object(
            mcp_manager, '_execute_tool_with_error_handling'
        )
        mock_framework.return_value = {
            'success': True,
            'data': {'bmi': 22.86, 'category': '正常'},
            'tool': 'calculator',
            'action': 'bmi'
        }
        
        # 执行测试
        result = await mcp_manager._call_calculator("bmi", {"weight": 70, "height": 175})
        
        # 验证通用框架被正确调用
        mock_framework.assert_called_once()
        call_args = mock_framework.call_args

        # 检查位置参数和关键字参数
        if len(call_args) > 1 and isinstance(call_args[1], dict):
            # 关键字参数形式
            assert call_args[1]['tool_name'] == 'calculator'
            assert call_args[1]['action'] == 'bmi'
            assert call_args[1]['parameters'] == {"weight": 70, "height": 175}
        else:
            # 位置参数形式
            assert call_args[0][0] == 'calculator'  # tool_name
            assert call_args[0][1] == 'bmi'         # action
            assert call_args[0][2] == {"weight": 70, "height": 175}  # parameters
        
        # 验证返回结果
        assert result['success'] is True
        assert result['data']['bmi'] == 22.86
    
    @pytest.mark.asyncio
    async def test_call_quickchart_integration_with_framework(self, mcp_manager, mocker):
        """测试quickchart工具与通用框架的集成"""
        # 模拟通用执行框架
        mock_framework = mocker.patch.object(
            mcp_manager, '_execute_tool_with_error_handling'
        )
        mock_framework.return_value = {
            'success': True,
            'data': {'chart_url': 'https://example.com/chart.png'},
            'tool': 'quickchart',
            'action': 'generate_chart'
        }
        
        # 执行测试
        chart_params = {
            "type": "line",
            "data": [1, 2, 3],
            "labels": ["A", "B", "C"]
        }
        result = await mcp_manager._call_quickchart("generate_chart", chart_params)
        
        # 验证通用框架被正确调用
        mock_framework.assert_called_once()
        call_args = mock_framework.call_args

        # 检查位置参数和关键字参数
        if len(call_args) > 1 and isinstance(call_args[1], dict):
            # 关键字参数形式
            assert call_args[1]['tool_name'] == 'quickchart'
            assert call_args[1]['action'] == 'generate_chart'
            assert call_args[1]['parameters'] == chart_params
        else:
            # 位置参数形式
            assert call_args[0][0] == 'quickchart'  # tool_name
            assert call_args[0][1] == 'generate_chart'  # action
            assert call_args[0][2] == chart_params  # parameters
        
        # 验证返回结果
        assert result['success'] is True
        assert 'chart_url' in result['data']
    
    # ============================================================================
    # 具体业务逻辑测试（重构后的分离方法）
    # ============================================================================
    
    @pytest.mark.parametrize("weight,height,expected_bmi,expected_category", [
        (70, 175, 22.86, "正常"),
        (50, 160, 19.53, "正常"),
        (90, 180, 27.78, "超重"),
        (45, 170, 15.57, "偏瘦"),
        (100, 170, 34.60, "肥胖")
    ])
    @pytest.mark.asyncio
    async def test_calculate_bmi_business_logic(
        self, mcp_manager, weight, height, expected_bmi, expected_category
    ):
        """参数化测试：BMI计算业务逻辑"""
        params = {"weight": weight, "height": height}
        
        result = await mcp_manager._calculate_bmi(params)
        
        assert abs(result['bmi'] - expected_bmi) < 0.01
        assert result['category'] == expected_category
        assert result['weight'] == weight
        assert result['height'] == height
    
    @pytest.mark.asyncio
    async def test_calculate_bmr_business_logic(self, mcp_manager):
        """测试BMR计算业务逻辑"""
        # 测试男性BMR计算
        male_params = {"weight": 70, "height": 175, "age": 30, "gender": "male"}
        male_result = await mcp_manager._calculate_bmr(male_params)
        
        # Harris-Benedict公式验证
        expected_male_bmr = 88.362 + (13.397 * 70) + (4.799 * 175) - (5.677 * 30)
        assert abs(male_result['bmr'] - expected_male_bmr) < 0.01
        assert male_result['gender'] == "male"
        
        # 测试女性BMR计算
        female_params = {"weight": 60, "height": 165, "age": 25, "gender": "female"}
        female_result = await mcp_manager._calculate_bmr(female_params)
        
        expected_female_bmr = 447.593 + (9.247 * 60) + (3.098 * 165) - (4.330 * 25)
        assert abs(female_result['bmr'] - expected_female_bmr) < 0.01
        assert female_result['gender'] == "female"
    
    @pytest.mark.asyncio
    async def test_generate_chart_business_logic(self, mcp_manager):
        """测试图表生成业务逻辑"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            # 模拟成功的HTTP响应
            mock_response = AsyncMock()
            mock_response.status = 200

            mock_session = AsyncMock()
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_session_class.return_value.__aenter__.return_value = mock_session

            params = {
                "type": "bar",
                "data": [10, 20, 30],
                "labels": ["A", "B", "C"],
                "title": "测试图表"
            }

            result = await mcp_manager._generate_chart(params)

            assert 'chart_url' in result
            assert 'config' in result
            assert result['type'] == "bar"
            assert result['config']['type'] == "bar"
            assert result['config']['data']['labels'] == ["A", "B", "C"]
    
    # ============================================================================
    # 工厂模式测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_create_simple_tool_executor_factory(self, mcp_manager):
        """测试简单工具执行器工厂方法"""
        def mock_data_generator(action, params):
            return {"action": action, "params": params, "generated": True}
        
        executor = mcp_manager._create_simple_tool_executor("test_tool", mock_data_generator)
        
        # 验证工厂方法返回可调用对象
        assert callable(executor)
        
        # 测试生成的执行器
        result = await executor("test_action", {"key": "value"})
        
        assert result["action"] == "test_action"
        assert result["params"] == {"key": "value"}
        assert result["generated"] is True
    
    # ============================================================================
    # 错误处理和边界条件测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_calculator_invalid_parameters(self, mcp_manager):
        """测试计算器无效参数处理"""
        with pytest.raises(ValueError, match="Weight and height must be positive numbers"):
            await mcp_manager._calculate_bmi({"weight": -10, "height": 0})
        
        with pytest.raises(ValueError, match="Weight, height, and age must be positive numbers"):
            await mcp_manager._calculate_bmr({"weight": 0, "height": 175, "age": -5, "gender": "male"})
    
    @pytest.mark.asyncio
    async def test_unsupported_actions(self, mcp_manager):
        """测试不支持的操作处理"""
        # 测试calculator不支持的操作
        result = await mcp_manager._call_calculator("unsupported_action", {})
        assert result['success'] is False
        assert "Unsupported calculator action" in result['error']
        
        # 测试quickchart不支持的操作
        result = await mcp_manager._call_quickchart("unsupported_action", {})
        assert result['success'] is False
        assert "Unsupported quickchart action" in result['error']
    
    # ============================================================================
    # 日志记录验证测试
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_logging_behavior_success(self, mcp_manager, mock_logger):
        """测试成功场景的日志记录行为"""
        async def success_executor(action, params):
            return {"success": True}
        
        await mcp_manager._execute_tool_with_error_handling(
            "test_tool", "test_action", {}, success_executor
        )
        
        # 验证调试日志
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert len(debug_calls) >= 1
        assert "执行工具: test_tool.test_action" in debug_calls[0][0][0]
        
        # 验证信息日志
        info_calls = [call for call in mock_logger.info.call_args_list]
        assert len(info_calls) >= 1
        assert "工具执行成功: test_tool.test_action" in info_calls[0][0][0]
    
    @pytest.mark.asyncio
    async def test_logging_behavior_failure(self, mcp_manager, mock_logger):
        """测试失败场景的日志记录行为"""
        async def failure_executor(action, params):
            raise RuntimeError("测试错误")
        
        await mcp_manager._execute_tool_with_error_handling(
            "test_tool", "test_action", {}, failure_executor
        )
        
        # 验证错误日志
        error_calls = [call for call in mock_logger.error.call_args_list]
        assert len(error_calls) >= 1
        assert "test_tool工具调用失败: 测试错误" in error_calls[0][0][0]


# ============================================================================
# 测试配置和辅助函数
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short", "--cov=aurawell.langchain_agent.mcp_tools_manager"])
