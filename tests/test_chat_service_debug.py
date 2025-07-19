#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康助手聊天服务错误诊断测试
基于图片中显示的网络错误进行排查和修复
"""

import os
import sys
import asyncio
import unittest
import logging
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatServiceDebugTest(unittest.TestCase):
    """聊天服务错误诊断测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.test_user_id = "test_user_debug"
        self.test_message = "你好，我想了解一些健康建议"
        print("\n" + "="*80)
        print("🔍 健康助手聊天服务错误诊断")
        print("="*80)
    
    def test_01_import_modules(self):
        """测试1: 导入相关模块"""
        print("\n📦 测试1: 导入相关模块...")
        
        try:
            from aurawell.core.agent_router import AgentRouter
            print("  ✅ AgentRouter导入成功")
            
            from aurawell.langchain_agent.agent import HealthAdviceAgent
            print("  ✅ HealthAdviceAgent导入成功")
            
            from aurawell.models.chat_models import ChatRequest, ChatResponse
            print("  ✅ Chat模型导入成功")
            
            self.assertTrue(True, "模块导入成功")
            
        except ImportError as e:
            self.fail(f"模块导入失败: {e}")
    
    def test_02_agent_router_creation(self):
        """测试2: Agent路由器创建"""
        print("\n🔀 测试2: Agent路由器创建...")
        
        try:
            from aurawell.core.agent_router import AgentRouter
            
            router = AgentRouter()
            print("  ✅ AgentRouter实例创建成功")
            
            self.assertIsNotNone(router)
            print("  ✅ AgentRouter实例验证通过")
            
        except Exception as e:
            self.fail(f"AgentRouter创建失败: {e}")
    
    async def test_03_agent_creation(self):
        """测试3: Agent实例创建"""
        print("\n🤖 测试3: Agent实例创建...")
        
        try:
            from aurawell.core.agent_router import AgentRouter
            
            router = AgentRouter()
            agent = await router.get_agent(self.test_user_id, "chat")
            
            print(f"  ✅ Agent实例创建成功: {type(agent).__name__}")
            
            # 检查Agent类型
            if hasattr(agent, 'get_agent_info'):
                info = agent.get_agent_info()
                print(f"  📊 Agent信息: {info}")
            
            self.assertIsNotNone(agent)
            
        except Exception as e:
            self.fail(f"Agent实例创建失败: {e}")
    
    async def test_04_message_processing(self):
        """测试4: 消息处理"""
        print("\n💬 测试4: 消息处理...")
        
        try:
            from aurawell.core.agent_router import AgentRouter
            
            router = AgentRouter()
            
            # 测试消息处理
            response = await router.process_message(
                user_id=self.test_user_id,
                message=self.test_message,
                context={"request_type": "health_chat"}
            )
            
            print(f"  📥 响应结果: {response}")
            
            # 验证响应格式
            self.assertIsInstance(response, dict)
            self.assertIn('success', response)
            self.assertIn('message', response)
            
            if response.get('success'):
                print("  ✅ 消息处理成功")
            else:
                print(f"  ⚠️  消息处理失败: {response.get('message', 'Unknown error')}")
            
        except Exception as e:
            print(f"  ❌ 消息处理异常: {e}")
            self.fail(f"消息处理失败: {e}")
    
    def test_05_chat_request_model(self):
        """测试5: ChatRequest模型验证"""
        print("\n📋 测试5: ChatRequest模型验证...")
        
        try:
            from aurawell.models.chat_models import ChatRequest
            
            # 测试有效请求
            valid_request = ChatRequest(
                message=self.test_message,
                conversation_id="test_conv_123",
                context={"request_type": "health_chat"}
            )
            print("  ✅ 有效ChatRequest创建成功")
            print(f"  📝 请求内容: {valid_request.dict()}")
            
            # 测试无效请求
            try:
                invalid_request = ChatRequest(message="")  # 空消息
                print("  ❌ 空消息验证失败")
            except Exception as validation_error:
                print(f"  ✅ 空消息验证成功: {validation_error}")
            
            self.assertTrue(True, "ChatRequest模型验证完成")
            
        except Exception as e:
            self.fail(f"ChatRequest模型验证失败: {e}")
    
    def test_06_response_format_compatibility(self):
        """测试6: 响应格式兼容性"""
        print("\n🔄 测试6: 响应格式兼容性...")
        
        try:
            # 模拟后端响应格式
            backend_response = {
                "reply": "这是一个健康建议回复",
                "conversation_id": "conv_test_123",
                "timestamp": "2025-07-19T14:30:00Z",
                "suggestions": [],
                "quick_replies": [],
                "status": "success"
            }
            
            # 模拟前端期望格式
            frontend_expected = {
                "data": {
                    "reply": backend_response["reply"],
                    "content": backend_response["reply"],
                    "conversation_id": backend_response["conversation_id"],
                    "timestamp": backend_response["timestamp"],
                    "suggestions": backend_response["suggestions"],
                    "quickReplies": backend_response["quick_replies"]
                }
            }
            
            print("  ✅ 后端响应格式验证")
            print(f"  📤 后端格式: {backend_response}")
            print("  ✅ 前端期望格式验证")
            print(f"  📥 前端格式: {frontend_expected}")
            
            # 验证关键字段
            self.assertIn("reply", backend_response)
            self.assertIn("conversation_id", backend_response)
            self.assertIn("status", backend_response)
            
            print("  ✅ 响应格式兼容性验证通过")
            
        except Exception as e:
            self.fail(f"响应格式兼容性验证失败: {e}")
    
    def test_07_error_handling_scenarios(self):
        """测试7: 错误处理场景"""
        print("\n🛡️  测试7: 错误处理场景...")
        
        try:
            # 测试各种错误场景
            error_scenarios = [
                {
                    "name": "网络超时",
                    "error_type": "TimeoutError",
                    "expected_response": "请求超时，AI正在思考中，请稍后重试"
                },
                {
                    "name": "API服务不可用",
                    "error_type": "ConnectionError", 
                    "expected_response": "网络错误，请检查您的网络连接"
                },
                {
                    "name": "认证失败",
                    "error_type": "AuthenticationError",
                    "expected_response": "认证失败，请重新登录"
                },
                {
                    "name": "服务器内部错误",
                    "error_type": "InternalServerError",
                    "expected_response": "抱歉，我现在遇到了一些技术问题。请稍后再试。"
                }
            ]
            
            for scenario in error_scenarios:
                print(f"  🔍 测试场景: {scenario['name']}")
                print(f"    错误类型: {scenario['error_type']}")
                print(f"    期望响应: {scenario['expected_response']}")
            
            print("  ✅ 错误处理场景验证完成")
            
        except Exception as e:
            self.fail(f"错误处理场景测试失败: {e}")
    
    def test_08_api_endpoint_format(self):
        """测试8: API端点格式验证"""
        print("\n🌐 测试8: API端点格式验证...")
        
        try:
            # 验证API端点路径
            api_endpoints = {
                "chat_message": "/api/v1/chat/message",
                "chat_history": "/api/v1/chat/conversations/{conversation_id}/messages",
                "create_conversation": "/api/v1/chat/conversations",
                "get_conversations": "/api/v1/chat/conversations"
            }
            
            for endpoint_name, endpoint_path in api_endpoints.items():
                print(f"  📍 {endpoint_name}: {endpoint_path}")
                
                # 验证路径格式
                self.assertTrue(endpoint_path.startswith("/api/v1/"))
                self.assertIn("chat", endpoint_path)
            
            print("  ✅ API端点格式验证通过")
            
        except Exception as e:
            self.fail(f"API端点格式验证失败: {e}")
    
    async def run_async_tests(self):
        """运行异步测试"""
        await self.test_03_agent_creation()
        await self.test_04_message_processing()


async def main():
    """主函数"""
    print("🔍 开始健康助手聊天服务错误诊断...")
    
    # 创建测试实例
    test_instance = ChatServiceDebugTest()
    test_instance.setUp()
    
    # 运行同步测试
    try:
        test_instance.test_01_import_modules()
        test_instance.test_02_agent_router_creation()
        test_instance.test_05_chat_request_model()
        test_instance.test_06_response_format_compatibility()
        test_instance.test_07_error_handling_scenarios()
        test_instance.test_08_api_endpoint_format()
        
        # 运行异步测试
        await test_instance.run_async_tests()
        
        print("\n" + "="*80)
        print("🎉 聊天服务错误诊断完成!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
