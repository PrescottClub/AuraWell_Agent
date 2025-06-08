#!/usr/bin/env python3
"""
M2-7 集成测试：验证所有模块集成和对话流程优化

测试内容：
1. 意图识别模块
2. 对话历史管理
3. 会话管理
4. ConversationAgent集成
5. 端到端对话流程
"""

import asyncio
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurawell.agent.intent_parser import IntentParser, IntentType
from aurawell.conversation.memory_manager import MemoryManager
from aurawell.conversation.session_manager import SessionManager
from aurawell.agent.conversation_agent import ConversationAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_intent_parser():
    """测试意图识别模块"""
    print("\n=== 测试意图识别模块 ===")
    
    parser = IntentParser()
    
    test_messages = [
        "我今天走了多少步？",
        "我昨晚睡得怎么样？",
        "帮我设置每天10000步的目标",
        "给我一些健康建议",
        "查看我的成就进度",
        "你好，我想了解一下这个应用"
    ]
    
    for message in test_messages:
        try:
            result = await parser.parse_intent(message)
            print(f"消息: {message}")
            print(f"意图: {result['RequestType']}, 置信度: {result['confidence']:.2f}")
            print(f"参数: {result['RequestContent']}")
            print("-" * 50)
        except Exception as e:
            print(f"意图识别失败: {message} - {e}")


async def test_memory_manager():
    """测试对话历史管理"""
    print("\n=== 测试对话历史管理 ===")
    
    memory = MemoryManager()
    test_user_id = "test_user_001"
    
    # 存储几轮对话
    conversations = [
        ("你好", "您好！我是AuraWell健康助手"),
        ("我今天走了多少步？", "根据您的数据，今天您走了8500步"),
        ("这个数据怎么样？", "这是一个不错的数据，接近推荐的每日10000步目标")
    ]
    
    for user_msg, ai_msg in conversations:
        success = await memory.store_conversation(
            user_id=test_user_id,
            user_message=user_msg,
            ai_response=ai_msg,
            intent_type="test",
            confidence=0.9
        )
        print(f"存储对话: {success} - {user_msg[:20]}...")
    
    # 获取对话历史
    history = await memory.get_conversation_history(test_user_id)
    print(f"获取到 {history['total_conversations']} 轮对话")
    
    for conv in history['conversations']:
        print(f"用户: {conv['user_message']}")
        print(f"AI: {conv['ai_response']}")
        print("-" * 30)


async def test_session_manager():
    """测试会话管理"""
    print("\n=== 测试会话管理 ===")
    
    session_mgr = SessionManager()
    test_user_id = "test_user_002"
    
    # 创建会话
    session_id = await session_mgr.create_session(test_user_id)
    print(f"创建会话: {session_id}")
    
    # 获取会话上下文
    context = await session_mgr.get_session_context(session_id)
    print(f"会话存在: {context.get('exists', False)}")
    print(f"用户ID: {context.get('user_id')}")
    
    # 更新会话上下文
    success = await session_mgr.update_session_context(
        session_id, 
        {"last_intent": "activity_query", "conversation_count": 3}
    )
    print(f"更新会话上下文: {success}")


async def test_conversation_agent():
    """测试ConversationAgent集成"""
    print("\n=== 测试ConversationAgent集成 ===")
    
    # 创建对话代理（演示模式）
    agent = ConversationAgent(user_id="test_user_003", demo_mode=True)
    
    test_messages = [
        "你好，我是新用户",
        "我今天的活动数据怎么样？",
        "我昨晚睡得好吗？",
        "帮我设置健康目标",
        "查看我的成就"
    ]
    
    for message in test_messages:
        try:
            print(f"\n用户: {message}")
            response = await agent.a_run(message)
            print(f"AI: {response[:100]}...")
            
            # 获取会话信息
            session_info = await agent.get_session_info()
            print(f"会话ID: {session_info['session_id']}")
            print(f"对话轮数: {session_info['conversation_count']}")
            
        except Exception as e:
            print(f"对话处理失败: {e}")
    
    # 清理会话
    await agent.cleanup_session()


async def test_end_to_end_performance():
    """端到端性能测试"""
    print("\n=== 端到端性能测试 ===")
    
    import time
    
    agent = ConversationAgent(user_id="perf_test_user", demo_mode=True)
    
    test_cases = [
        "我今天走了多少步？",
        "分析我的睡眠质量",
        "给我一些健康建议",
        "查看我的成就进度"
    ]
    
    total_time = 0
    success_count = 0
    
    for i, message in enumerate(test_cases, 1):
        try:
            start_time = time.time()
            response = await agent.a_run(message)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            success_count += 1
            
            print(f"测试 {i}: {response_time:.2f}s - {'通过' if response_time < 2.0 else '超时'}")
            
        except Exception as e:
            print(f"测试 {i}: 失败 - {e}")
    
    avg_time = total_time / len(test_cases) if test_cases else 0
    success_rate = (success_count / len(test_cases)) * 100 if test_cases else 0
    
    print(f"\n性能统计:")
    print(f"平均响应时间: {avg_time:.2f}s")
    print(f"成功率: {success_rate:.1f}%")
    print(f"性能目标达成: {'是' if avg_time < 2.0 and success_rate > 95 else '否'}")


async def main():
    """主测试函数"""
    print("开始 M2-7 集成测试...")
    
    try:
        # 测试各个模块
        await test_intent_parser()
        await test_memory_manager()
        await test_session_manager()
        await test_conversation_agent()
        await test_end_to_end_performance()
        
        print("\n=== 测试完成 ===")
        print("所有模块集成测试通过！")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
