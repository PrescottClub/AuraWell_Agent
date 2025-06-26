#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的MCP智能工具系统测试
专注于验证框架的基本功能
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


async def test_imports():
    """测试基本导入"""
    print("🔍 测试模块导入...")
    
    try:
        from aurawell.langchain_agent.agent import HealthAdviceAgent
        print("✅ HealthAdviceAgent 导入成功")
    except ImportError as e:
        print(f"❌ HealthAdviceAgent 导入失败: {e}")
        return False
    
    try:
        from aurawell.langchain_agent.mcp_tools_manager import MCPToolsManager
        print("✅ MCPToolsManager 导入成功")
    except ImportError as e:
        print(f"❌ MCPToolsManager 导入失败: {e}")
        return False
    
    try:
        from aurawell.langchain_agent.mcp_interface import MCPInterface
        print("✅ MCPInterface 导入成功")
    except ImportError as e:
        print(f"❌ MCPInterface 导入失败: {e}")
        return False
    
    return True


async def test_basic_initialization():
    """测试基本初始化"""
    print("\n🚀 测试基本初始化...")
    
    try:
        from aurawell.langchain_agent.agent import HealthAdviceAgent
        from aurawell.langchain_agent.mcp_tools_manager import MCPToolsManager
        
        # 测试Agent初始化
        agent = HealthAdviceAgent(user_id="test_user")
        print("✅ HealthAdviceAgent 初始化成功")
        
        # 测试MCP工具管理器初始化
        mcp_tools = MCPToolsManager()
        print("✅ MCPToolsManager 初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_basic_response():
    """测试Agent基本响应"""
    print("\n💬 测试Agent基本响应...")
    
    try:
        from aurawell.langchain_agent.agent import HealthAdviceAgent
        
        agent = HealthAdviceAgent(user_id="test_user")
        
        # 简单的测试消息
        test_message = "你好，我想了解一些健康建议"
        
        print(f"📝 测试消息: {test_message}")
        
        # 测试process_message方法
        response = await agent.process_message(
            message=test_message,
            context={}
        )
        
        print("✅ Agent响应成功")
        print(f"📄 响应类型: {type(response)}")
        
        if isinstance(response, dict):
            print(f"📝 响应内容预览: {str(response)[:200]}...")
        else:
            print(f"📝 响应内容: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent响应测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_tools_manager():
    """测试MCP工具管理器基本功能"""
    print("\n🛠️ 测试MCP工具管理器...")
    
    try:
        from aurawell.langchain_agent.mcp_tools_manager import MCPToolsManager
        
        mcp_tools = MCPToolsManager()
        
        # 测试意图分析器
        if hasattr(mcp_tools, 'intent_analyzer'):
            print("✅ 意图分析器存在")
            
            # 测试意图分析
            test_query = "我想分析我的健康数据"
            if hasattr(mcp_tools.intent_analyzer, 'analyze_intent'):
                intent = mcp_tools.intent_analyzer.analyze_intent(test_query)
                print(f"📊 意图分析结果: {intent}")
            else:
                print("⚠️ analyze_intent方法不存在")
        else:
            print("⚠️ 意图分析器不存在")
        
        # 检查工具接口
        if hasattr(mcp_tools, 'mcp_interface'):
            print("✅ MCP接口存在")
        else:
            print("⚠️ MCP接口不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP工具管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 开始MCP智能工具系统简化测试")
    print("=" * 60)
    
    success = True
    
    # 1. 测试导入
    if not await test_imports():
        success = False
    
    # 2. 测试初始化
    if not await test_basic_initialization():
        success = False
    
    # 3. 测试Agent响应
    if not await test_agent_basic_response():
        success = False
    
    # 4. 测试MCP工具管理器
    if not await test_mcp_tools_manager():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有基本测试通过！MCP框架基本功能正常")
    else:
        print("⚠️ 部分测试失败，需要进一步调试")
    
    return success


if __name__ == "__main__":
    asyncio.run(main()) 