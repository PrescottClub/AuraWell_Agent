#!/usr/bin/env python3
"""
测试健康工具注册表
"""

try:
    from aurawell.agent.tools_registry import HealthToolsRegistry
    
    print("创建工具注册表...")
    registry = HealthToolsRegistry()
    
    tools = registry.get_tools_schema()
    print(f"✅ 成功注册 {len(tools)} 个工具:")
    
    for i, tool in enumerate(tools, 1):
        tool_name = tool['function']['name']
        tool_desc = tool['function']['description']
        print(f"  {i}. {tool_name}: {tool_desc}")
    
    print("\n🎯 工具测试完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
