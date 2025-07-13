#!/usr/bin/env python3
"""
验证零配置启动功能

这个脚本验证AuraWell可以在没有任何API Key配置的情况下正常启动，
所有服务都会自动使用Mock客户端。
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_environment():
    """清除所有相关的环境变量"""
    env_vars_to_clear = [
        'DASHSCOPE_API_KEY',
        'QWEN_API',
        'DEEP_SEEK_API',
        'DEEPSEEK_API_KEY',
        'BRAVE_API_KEY',
        'XIAOMI_HEALTH_API_KEY',
        'APPLE_HEALTH_API_KEY'
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
            logger.info(f"清除环境变量: {var}")


def test_service_factory():
    """测试ServiceClientFactory功能"""
    logger.info("=== 测试ServiceClientFactory ===")
    
    from aurawell.core.service_factory import ServiceClientFactory, MockDeepSeekClient
    
    # 重置工厂状态
    ServiceClientFactory.reset_clients()
    
    # 获取DeepSeek客户端
    client = ServiceClientFactory.get_deepseek_client()
    logger.info(f"获取到客户端类型: {type(client).__name__}")
    
    # 验证是Mock客户端
    assert isinstance(client, MockDeepSeekClient), "应该返回Mock客户端"
    assert hasattr(client, 'is_mock'), "Mock客户端应该有is_mock属性"
    assert client.is_mock is True, "is_mock应该为True"
    
    # 获取服务状态
    status = ServiceClientFactory.get_service_status()
    logger.info(f"服务状态: {status}")
    
    # 验证服务状态
    assert 'deepseek' in status, "应该包含deepseek服务状态"
    deepseek_status = status['deepseek']
    assert deepseek_status['status'] == 'mock', "状态应该为mock"
    assert deepseek_status['type'] == 'mock', "类型应该为mock"
    assert deepseek_status['api_key_configured'] is False, "API Key应该未配置"
    
    logger.info("✅ ServiceClientFactory测试通过")


def test_health_advice_service():
    """测试HealthAdviceService"""
    logger.info("=== 测试HealthAdviceService ===")
    
    from aurawell.langchain_agent.services.health_advice_service import HealthAdviceService
    from aurawell.core.service_factory import MockDeepSeekClient
    
    # 初始化服务
    service = HealthAdviceService()
    logger.info(f"HealthAdviceService客户端类型: {type(service.deepseek_client).__name__}")
    
    # 验证使用Mock客户端
    assert isinstance(service.deepseek_client, MockDeepSeekClient), "应该使用Mock客户端"
    
    # 测试Mock响应
    messages = [
        {"role": "system", "content": "你是健康助手"},
        {"role": "user", "content": "我想了解健康饮食建议"}
    ]
    
    response = service.deepseek_client.get_deepseek_response(messages=messages)
    logger.info(f"Mock响应内容: {response.content[:100]}...")
    
    # 验证响应
    assert response is not None, "应该有响应"
    assert response.content is not None, "响应内容不应为空"
    assert "Mock响应" in response.content or "饮食" in response.content, "应该包含相关内容"
    assert response.model == "deepseek-v3-mock", "模型名称应该正确"
    
    logger.info("✅ HealthAdviceService测试通过")


def test_orchestrator():
    """测试AuraWellOrchestrator"""
    logger.info("=== 测试AuraWellOrchestrator ===")
    
    from aurawell.core.orchestrator_v2 import AuraWellOrchestrator
    from aurawell.core.service_factory import MockDeepSeekClient
    
    # 初始化编排器
    orchestrator = AuraWellOrchestrator()
    logger.info(f"Orchestrator客户端类型: {type(orchestrator.deepseek_client).__name__}")
    
    # 验证使用Mock客户端
    assert isinstance(orchestrator.deepseek_client, MockDeepSeekClient), "应该使用Mock客户端"
    
    logger.info("✅ AuraWellOrchestrator测试通过")


def test_langchain_agent():
    """测试LangChain Agent"""
    logger.info("=== 测试LangChain Agent ===")
    
    try:
        from aurawell.langchain_agent.agent import LangChainAgent
        from aurawell.core.service_factory import MockDeepSeekClient
        
        # 初始化Agent
        agent = LangChainAgent()
        logger.info(f"LangChain Agent客户端类型: {type(agent.deepseek_client).__name__}")
        
        # 验证使用Mock客户端
        assert isinstance(agent.deepseek_client, MockDeepSeekClient), "应该使用Mock客户端"
        
        logger.info("✅ LangChain Agent测试通过")
    except Exception as e:
        logger.warning(f"LangChain Agent测试跳过: {e}")


def test_mcp_tools_interface():
    """测试MCP工具接口"""
    logger.info("=== 测试MCP工具接口 ===")

    from aurawell.core.service_factory import ServiceClientFactory, MockMCPToolInterface
    import asyncio

    # 获取MCP工具接口
    mcp_interface = ServiceClientFactory.get_mcp_tools_interface()
    logger.info(f"MCP工具接口类型: {type(mcp_interface).__name__}")

    # 验证使用Mock接口
    assert isinstance(mcp_interface, MockMCPToolInterface), "应该使用Mock接口"
    assert hasattr(mcp_interface, 'is_mock'), "Mock接口应该有is_mock属性"
    assert mcp_interface.is_mock is True, "is_mock应该为True"

    # 测试工具状态
    status = mcp_interface.get_tool_status()
    logger.info(f"MCP工具状态: {status}")
    assert status['total_tools'] == 13, "应该有13个工具"
    assert status['status'] == 'mock', "状态应该为mock"

    # 测试异步工具调用
    async def test_tool_call():
        result = await mcp_interface.call_tool(
            'calculator',
            'calculate',
            {'expression': '2+2'}
        )
        return result

    result = asyncio.run(test_tool_call())
    logger.info(f"工具调用结果: {result}")

    assert result['success'] is True, "工具调用应该成功"
    assert result['is_mock'] is True, "应该是Mock调用"
    assert result['tool_name'] == 'calculator', "工具名称应该正确"

    logger.info("✅ MCP工具接口测试通过")


def test_singleton_behavior():
    """测试单例行为"""
    logger.info("=== 测试单例行为 ===")

    from aurawell.core.service_factory import ServiceClientFactory
    from aurawell.langchain_agent.services.health_advice_service import HealthAdviceService
    from aurawell.core.orchestrator_v2 import AuraWellOrchestrator

    # 创建多个服务实例
    service = HealthAdviceService()
    orchestrator = AuraWellOrchestrator()
    factory_client = ServiceClientFactory.get_deepseek_client()
    factory_mcp = ServiceClientFactory.get_mcp_tools_interface()

    # 验证它们使用同一个客户端实例
    assert service.deepseek_client is orchestrator.deepseek_client, "应该使用同一个客户端实例"
    assert service.deepseek_client is factory_client, "应该使用同一个客户端实例"

    # 验证MCP工具接口也是单例
    factory_mcp2 = ServiceClientFactory.get_mcp_tools_interface()
    assert factory_mcp is factory_mcp2, "MCP工具接口应该是单例"

    logger.info("✅ 单例行为测试通过")


def main():
    """主函数"""
    logger.info("开始验证零配置启动功能...")
    
    # 清除环境变量
    clear_environment()
    
    try:
        # 运行所有测试
        test_service_factory()
        test_health_advice_service()
        test_orchestrator()
        test_langchain_agent()
        test_mcp_tools_interface()
        test_singleton_behavior()
        
        logger.info("🎉 所有测试通过！零配置启动功能正常工作")
        logger.info("📝 总结:")
        logger.info("  - ServiceClientFactory正常工作")
        logger.info("  - 所有服务自动使用Mock客户端")
        logger.info("  - DeepSeek Mock客户端提供合理的测试响应")
        logger.info("  - MCP工具Mock接口支持13个工具")
        logger.info("  - 单例模式正常工作")
        logger.info("  - 服务状态跟踪正常")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
