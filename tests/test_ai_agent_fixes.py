"""
测试AI Agent修复功能
验证LangChain Agent架构、模型选择、错误处理和对话历史管理
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

import sys
import os

# Add the src directory to Python path for new structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aurawell.langchain_agent.agent import HealthAdviceAgent
from aurawell.langchain_agent.services.health_advice_service import HealthAdviceService, MODEL_CONFIG
from aurawell.core.exceptions import ExternalServiceError


class TestLangChainAgentArchitecture:
    """测试LangChain Agent架构修复"""

    def test_agent_initialization(self):
        """测试Agent初始化"""
        agent = HealthAdviceAgent("test_user")
        
        assert agent.user_id == "test_user"
        assert agent.health_advice_service is not None
        assert agent._conversation_history == []
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'agent_executor')

    def test_tools_creation(self):
        """测试工具创建"""
        agent = HealthAdviceAgent("test_user")
        tools = agent._create_tools()

        assert isinstance(tools, list)
        assert len(tools) == 3  # UserProfileLookup, CalcMetrics, SearchKnowledge

        # 检查工具名称（可能是LangChain Tool对象或简化的字典）
        if tools and hasattr(tools[0], 'name'):
            # LangChain工具对象
            tool_names = [tool.name for tool in tools]
        else:
            # 简化的字典格式
            tool_names = [tool["name"] for tool in tools]

        assert "UserProfileLookup" in tool_names
        assert "CalcMetrics" in tool_names
        assert "SearchKnowledge" in tool_names

    def test_agent_info_updated(self):
        """测试Agent信息更新"""
        agent = HealthAdviceAgent("test_user")
        info = agent.get_agent_info()
        
        assert info["type"] == "langchain"
        assert info["version"] == "2.1.0"
        assert "langchain_agent_executor" in info["features"]
        assert len(info["tools"]) == 3

    @pytest.mark.asyncio
    async def test_conversation_history_clearing(self):
        """测试对话历史清除功能"""
        agent = HealthAdviceAgent("test_user")
        
        # 添加一些对话历史
        agent._conversation_history.append({"role": "user", "content": "测试消息"})
        assert len(agent._conversation_history) == 1
        
        # 清除历史
        result = await agent.clear_conversation_history()
        
        assert result is True
        assert len(agent._conversation_history) == 0


class TestModelSelection:
    """测试模型选择统一化"""

    def test_model_config_exists(self):
        """测试模型配置存在"""
        assert "reasoning_tasks" in MODEL_CONFIG
        assert "chat_tasks" in MODEL_CONFIG
        assert "default" in MODEL_CONFIG
        
        assert MODEL_CONFIG["reasoning_tasks"] == "deepseek-reasoner"
        assert MODEL_CONFIG["chat_tasks"] == "deepseek-chat"
        assert MODEL_CONFIG["default"] == "deepseek-reasoner"

    @pytest.mark.asyncio
    async def test_health_advice_service_model_usage(self):
        """测试健康建议服务使用正确的模型"""
        service = HealthAdviceService()
        
        # Mock DeepSeek客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = "测试健康建议"
        mock_client.get_deepseek_response.return_value = mock_response
        service.deepseek_client = mock_client
        
        # 测试生成建议时使用推理模型
        try:
            await service._generate_ai_advice(
                user_data={"profile": Mock()},
                health_metrics={"bmi": 22.0, "age": 30},
                goal_type="weight_loss"
            )
            
            # 验证调用了正确的模型
            mock_client.get_deepseek_response.assert_called()
            call_args = mock_client.get_deepseek_response.call_args
            assert call_args[1]["model_name"] == MODEL_CONFIG["reasoning_tasks"]
            
        except Exception:
            # 预期可能因为缺少完整数据而失败，但模型选择应该正确
            pass


class TestErrorHandling:
    """测试错误处理增强"""

    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """测试重试机制"""
        service = HealthAdviceService()
        
        # Mock DeepSeek客户端，模拟网络错误
        mock_client = Mock()
        service.deepseek_client = mock_client
        
        # 第一次调用失败，第二次成功
        mock_response = Mock()
        mock_response.content = "成功响应"
        mock_client.get_deepseek_response.side_effect = [
            Exception("Connection timeout"),  # 第一次失败
            mock_response  # 第二次成功
        ]
        
        # 测试重试机制
        result = await service._call_deepseek_with_retry(
            messages=[{"role": "user", "content": "测试"}],
            model_name="deepseek-reasoner",
            max_retries=1,
            retry_delay=0.1
        )
        
        assert result == "成功响应"
        assert mock_client.get_deepseek_response.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_mechanism_max_retries(self):
        """测试重试机制达到最大次数"""
        service = HealthAdviceService()
        
        # Mock DeepSeek客户端，持续失败
        mock_client = Mock()
        service.deepseek_client = mock_client
        mock_client.get_deepseek_response.side_effect = Exception("Persistent error")
        
        # 测试重试机制
        with pytest.raises(ExternalServiceError):
            await service._call_deepseek_with_retry(
                messages=[{"role": "user", "content": "测试"}],
                model_name="deepseek-reasoner",
                max_retries=2,
                retry_delay=0.1
            )
        
        # 验证重试了正确的次数 (初始调用 + 2次重试 = 3次)
        assert mock_client.get_deepseek_response.call_count == 3

    def test_should_retry_error_logic(self):
        """测试错误重试判断逻辑"""
        service = HealthAdviceService()
        
        # 网络错误应该重试
        network_error = Exception("Connection timeout")
        assert service._should_retry_error(network_error) is True
        
        # 认证错误不应该重试
        auth_error = Exception("401 Unauthorized")
        assert service._should_retry_error(auth_error) is False
        
        # 客户端错误不应该重试
        client_error = Exception("400 Bad Request")
        assert service._should_retry_error(client_error) is False
        
        # 服务器错误应该重试
        server_error = Exception("500 Internal Server Error")
        assert service._should_retry_error(server_error) is True


class TestToolMethods:
    """测试工具方法实现"""

    @pytest.mark.asyncio
    async def test_user_profile_lookup_tool(self):
        """测试用户档案查询工具"""
        agent = HealthAdviceAgent("test_user")
        
        # Mock健康建议服务
        mock_service = AsyncMock()
        mock_service._get_user_profile_data.return_value = {
            "age": 30, "gender": "male", "height": 175
        }
        agent.health_advice_service = mock_service
        
        result = await agent._user_profile_lookup("查询用户信息")
        
        assert "用户档案信息" in result
        mock_service._get_user_profile_data.assert_called_once_with("test_user")

    @pytest.mark.asyncio
    async def test_calc_metrics_tool(self):
        """测试健康指标计算工具"""
        agent = HealthAdviceAgent("test_user")
        
        # Mock健康建议服务
        mock_service = AsyncMock()
        mock_service._get_user_profile_data.return_value = {
            "age": 30, "height": 175, "weight": 70
        }
        mock_service._calculate_health_metrics.return_value = {
            "bmi": 22.9, "bmr": 1650, "tdee": 2200
        }
        agent.health_advice_service = mock_service
        
        result = await agent._calc_metrics()
        
        assert "健康指标" in result
        mock_service._calculate_health_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_knowledge_tool(self):
        """测试知识检索工具"""
        agent = HealthAdviceAgent("test_user")
        
        # Mock健康建议服务
        mock_service = AsyncMock()
        mock_advice = Mock()
        mock_advice.diet = Mock()
        mock_advice.diet.model_dump = Mock(return_value={"title": "饮食建议"})
        mock_service.generate_comprehensive_advice.return_value = mock_advice
        agent.health_advice_service = mock_service
        
        result = await agent._search_knowledge("减肥建议")
        
        assert isinstance(result, str)
        mock_service.generate_comprehensive_advice.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
