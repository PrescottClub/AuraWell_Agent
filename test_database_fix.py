#!/usr/bin/env python3
"""
快速测试数据库修复是否成功
"""

import asyncio
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurawell.database import get_database_manager
from aurawell.conversation.memory_manager import MemoryManager, ConversationHistory
from aurawell.conversation.session_manager import SessionManager, UserSession

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_tables():
    """测试数据库表是否正确创建"""
    print("=== 测试数据库表创建 ===")
    
    db_manager = get_database_manager()
    
    try:
        # 初始化数据库
        await db_manager.initialize()
        print("✅ 数据库初始化成功")
        
        # 检查表是否存在
        async with db_manager.engine.connect() as conn:
            def check_tables(sync_conn):
                from sqlalchemy import inspect
                inspector = inspect(sync_conn)
                tables = inspector.get_table_names()
                return tables
            
            tables = await conn.run_sync(check_tables)
            print(f"📋 现有表: {tables}")
            
            required_tables = ['conversation_history', 'user_sessions']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ 缺失表: {missing_tables}")
                return False
            else:
                print("✅ 所有必需的表都存在")
                return True
                
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False


async def test_memory_manager():
    """测试MemoryManager是否正常工作"""
    print("\n=== 测试MemoryManager ===")
    
    memory = MemoryManager()
    test_user_id = "test_user_fix"
    
    try:
        # 存储对话
        success = await memory.store_conversation(
            user_id=test_user_id,
            user_message="测试消息",
            ai_response="测试回复",
            intent_type="test",
            confidence=0.9
        )
        
        if success:
            print("✅ 对话存储成功")
        else:
            print("❌ 对话存储失败")
            return False
        
        # 获取对话历史
        history = await memory.get_conversation_history(test_user_id)
        
        if history['total_conversations'] > 0:
            print(f"✅ 对话历史获取成功，共 {history['total_conversations']} 条")
            return True
        else:
            print("❌ 对话历史为空")
            return False
            
    except Exception as e:
        print(f"❌ MemoryManager测试失败: {e}")
        return False


async def test_session_manager():
    """测试SessionManager是否正常工作"""
    print("\n=== 测试SessionManager ===")
    
    session_mgr = SessionManager()
    test_user_id = "test_user_session_fix"
    
    try:
        # 创建会话
        session_id = await session_mgr.create_session(test_user_id)
        print(f"✅ 会话创建成功: {session_id}")
        
        # 获取会话上下文
        context = await session_mgr.get_session_context(session_id)
        
        if context.get('exists', False):
            print("✅ 会话上下文获取成功")
            return True
        else:
            print(f"❌ 会话上下文获取失败: {context}")
            return False
            
    except Exception as e:
        print(f"❌ SessionManager测试失败: {e}")
        return False


async def test_conversation_agent_quick():
    """快速测试ConversationAgent"""
    print("\n=== 快速测试ConversationAgent ===")
    
    try:
        from aurawell.agent.conversation_agent import ConversationAgent
        
        # 创建代理（演示模式）
        agent = ConversationAgent(user_id="test_user_agent_fix", demo_mode=True)
        
        # 测试一个简单的对话
        response = await agent.a_run("你好")
        
        if response and len(response) > 0:
            print("✅ ConversationAgent响应成功")
            print(f"📝 响应: {response[:100]}...")
            return True
        else:
            print("❌ ConversationAgent响应为空")
            return False
            
    except Exception as e:
        print(f"❌ ConversationAgent测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🔧 开始数据库修复验证测试...\n")
    
    results = []
    
    # 测试数据库表
    results.append(await test_database_tables())
    
    # 测试MemoryManager
    results.append(await test_memory_manager())
    
    # 测试SessionManager
    results.append(await test_session_manager())
    
    # 快速测试ConversationAgent
    results.append(await test_conversation_agent_quick())
    
    # 统计结果
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！数据库修复成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步修复")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
