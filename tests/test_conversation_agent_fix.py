#!/usr/bin/env python3
"""
测试ConversationAgent的修复
验证生产模式和演示模式的正确行为
"""

import asyncio
import os
import sys
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aurawell.agent.conversation_agent import ConversationAgent


async def test_demo_mode():
    """测试演示模式"""
    print("🧪 测试演示模式...")
    
    # 创建演示模式的agent
    agent = ConversationAgent(user_id="test_user", demo_mode=True)
    
    # 测试活动数据查询
    response = await agent.a_run("我的活动数据怎么样？")
    print(f"演示模式响应: {response[:100]}...")
    
    assert "演示模式" in response, "演示模式应该包含'演示模式'字样"
    assert "活动数据分析" in response, "应该包含活动数据分析"
    
    print("✅ 演示模式测试通过")


async def test_production_mode_with_mock():
    """测试生产模式（使用mock API）"""
    print("🧪 测试生产模式（模拟API）...")

    # 模拟有API密钥的环境
    with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test_key'}):
        # 模拟DeepSeek客户端
        mock_client = Mock()
        mock_client.chat_completion.return_value = "这是来自真实AI的响应"

        # 创建生产模式的agent
        agent = ConversationAgent(user_id="test_user", demo_mode=False)
        agent.client = mock_client  # 替换为mock客户端

        # 测试API调用
        response = await agent.a_run("你好")
        print(f"生产模式响应: {response}")

        # 验证返回的是真实API响应，而不是演示响应
        assert response == "这是来自真实AI的响应", "生产模式应该返回真实API响应"
        assert "演示模式" not in response, "生产模式不应该包含'演示模式'字样"

        # 验证API被调用
        mock_client.chat_completion.assert_called_once()

    print("✅ 生产模式测试通过")


async def test_production_mode_fallback():
    """测试生产模式API失败时的降级"""
    print("🧪 测试生产模式API失败降级...")

    # 模拟有API密钥的环境
    with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test_key'}):
        # 模拟API失败的客户端
        mock_client = Mock()
        mock_client.chat_completion.side_effect = Exception("API调用失败")

        # 创建生产模式的agent
        agent = ConversationAgent(user_id="test_user", demo_mode=False)
        agent.client = mock_client

        # 测试API失败时的降级
        response = await agent.a_run("活动数据")
        print(f"降级响应: {response[:100]}...")

        # 验证包含错误信息和降级到演示模式
        assert "AI服务暂时不可用" in response, "应该包含AI服务不可用信息"
        assert "演示模式" in response, "失败时应该降级到演示模式"

    print("✅ 生产模式降级测试通过")


async def test_mode_detection():
    """测试模式检测逻辑"""
    print("🧪 测试模式检测...")
    
    # 测试无API密钥时自动切换到演示模式
    with patch.dict(os.environ, {}, clear=True):
        agent = ConversationAgent(user_id="test_user")
        assert agent.demo_mode == True, "无API密钥时应该自动切换到演示模式"
    
    # 测试有API密钥时的生产模式
    with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test_key'}):
        agent = ConversationAgent(user_id="test_user")
        assert agent.demo_mode == False, "有API密钥时应该使用生产模式"
    
    # 测试强制演示模式
    agent = ConversationAgent(user_id="test_user", demo_mode=True)
    assert agent.demo_mode == True, "强制演示模式应该生效"
    
    print("✅ 模式检测测试通过")


async def main():
    """运行所有测试"""
    print("🚀 开始ConversationAgent修复验证测试\n")
    
    try:
        await test_demo_mode()
        print()
        
        await test_production_mode_with_mock()
        print()
        
        await test_production_mode_fallback()
        print()
        
        await test_mode_detection()
        print()
        
        print("🎉 所有测试通过！ConversationAgent修复验证成功")
        print("\n修复总结:")
        print("✅ 生产模式现在正确返回真实API响应")
        print("✅ 演示模式正常工作")
        print("✅ API失败时正确降级到演示模式")
        print("✅ 模式检测逻辑正确")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
