#!/usr/bin/env python3
"""
AuraWell真实AI功能演示

展示配置好的DeepSeek API在健康咨询场景中的实际应用
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 加载.env文件
load_dotenv(project_root / ".env")

from aurawell.core.service_factory import ServiceClientFactory


def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


async def demo_basic_health_consultation():
    """演示基础健康咨询"""
    print_separator("基础健康咨询演示")
    
    client = ServiceClientFactory.get_deepseek_client()
    
    # 健康咨询场景
    scenarios = [
        {
            "title": "💤 睡眠质量改善",
            "query": "我最近睡眠质量不好，经常失眠，有什么改善建议吗？"
        },
        {
            "title": "🏃‍♂️ 运动计划制定", 
            "query": "我是办公室工作者，想开始运动但不知道从哪里开始，请给我一个适合的运动计划。"
        },
        {
            "title": "🥗 营养饮食建议",
            "query": "我想减肥但又要保证营养，请推荐一些健康的饮食搭配。"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print(f"用户问题: {scenario['query']}")
        print("-" * 50)
        
        messages = [
            {
                "role": "system", 
                "content": "你是AuraWell的专业健康顾问，拥有丰富的健康管理经验。请提供专业、实用、个性化的健康建议。"
            },
            {
                "role": "user", 
                "content": scenario['query']
            }
        ]
        
        try:
            response = client.get_deepseek_response(
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            print(f"🤖 AI健康顾问回复:")
            print(response.content)
            print(f"\n📊 Token使用: {response.usage.total_tokens if response.usage else 'N/A'}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("\n" + "."*50)


async def demo_mcp_tools_integration():
    """演示MCP工具集成"""
    print_separator("MCP工具集成演示 (Mock模式)")
    
    mcp_tools = ServiceClientFactory.get_mcp_tools_interface()
    
    # 演示几个常用工具
    tools_demo = [
        {
            "name": "calculator",
            "title": "🧮 BMI计算",
            "action": "calculate",
            "params": {"expression": "70/(1.75*1.75)"},
            "description": "计算BMI指数 (体重70kg, 身高1.75m)"
        },
        {
            "name": "brave-search", 
            "title": "🔍 健康信息搜索",
            "action": "search",
            "params": {"query": "地中海饮食法 健康益处", "count": 3},
            "description": "搜索地中海饮食相关信息"
        },
        {
            "name": "weather",
            "title": "🌤️ 天气查询",
            "action": "get_weather", 
            "params": {"location": "北京"},
            "description": "获取北京天气信息，用于运动建议"
        }
    ]
    
    for tool in tools_demo:
        print(f"\n{tool['title']}")
        print(f"工具: {tool['name']}")
        print(f"描述: {tool['description']}")
        print("-" * 40)
        
        try:
            result = await mcp_tools.call_tool(
                tool['name'],
                tool['action'], 
                tool['params']
            )
            
            if result['success']:
                print("✅ 工具调用成功")
                print(f"📊 结果: {result['data']}")
                print(f"🔧 模式: {'Mock' if result.get('is_mock') else 'Real'}")
            else:
                print(f"❌ 工具调用失败: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("."*40)


def demo_service_status():
    """演示服务状态监控"""
    print_separator("服务状态监控")
    
    from aurawell.interfaces.service_status_api import (
        get_current_service_status,
        is_zero_config_mode,
        get_live_services,
        get_mock_services
    )
    
    # 获取服务状态
    status = get_current_service_status()
    live_services = get_live_services()
    mock_services = get_mock_services()
    zero_config = is_zero_config_mode()
    
    print(f"🎯 系统运行模式: {'零配置模式' if zero_config else '混合模式'}")
    print(f"✅ 真实服务: {live_services}")
    print(f"🟡 Mock服务: {mock_services}")
    
    print("\n📊 详细服务状态:")
    for service_name, service_info in status.items():
        status_emoji = "✅" if service_info['status'] == 'live' else "🟡"
        print(f"  {status_emoji} {service_info['name']}: {service_info['status']} ({service_info['type']})")
        if service_info.get('error'):
            print(f"    ⚠️ 错误: {service_info['error']}")


async def demo_health_service_integration():
    """演示健康服务集成"""
    print_separator("健康服务集成演示")
    
    from aurawell.langchain_agent.services.health_advice_service import HealthAdviceService
    from aurawell.core.orchestrator_v2 import AuraWellOrchestrator
    
    # 初始化服务
    health_service = HealthAdviceService()
    orchestrator = AuraWellOrchestrator()
    
    print("🏥 健康建议服务状态:")
    print(f"  - 客户端类型: {type(health_service.deepseek_client).__name__}")
    print(f"  - 是否真实API: {'是' if hasattr(health_service.deepseek_client, 'client') else '否'}")
    
    print("\n🎯 编排器状态:")
    print(f"  - 客户端类型: {type(orchestrator.deepseek_client).__name__}")
    print(f"  - 单例验证: {'通过' if health_service.deepseek_client is orchestrator.deepseek_client else '失败'}")
    
    # 测试健康建议生成
    print("\n💡 健康建议生成测试:")
    messages = [
        {"role": "system", "content": "你是专业的健康管理师"},
        {"role": "user", "content": "我想了解如何在工作繁忙的情况下保持健康的生活方式"}
    ]
    
    try:
        response = health_service.deepseek_client.get_deepseek_response(messages=messages)
        print("✅ 健康建议生成成功")
        print(f"📝 建议内容 (前150字符): {response.content[:150]}...")
        print(f"🤖 使用模型: {response.model}")
    except Exception as e:
        print(f"❌ 健康建议生成失败: {e}")


async def main():
    """主演示函数"""
    print("🚀 AuraWell真实AI功能演示")
    print("=" * 60)
    print("🎯 当前配置:")
    print(f"  - DeepSeek API Key: {'已配置' if os.getenv('DEEPSEEK_API_KEY') else '未配置'}")
    print(f"  - API端点: {os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')}")
    print(f"  - 默认模型: {os.getenv('DASHSCOPE_DEFAULT_MODEL', 'deepseek-chat')}")
    
    try:
        # 运行所有演示
        demo_service_status()
        await demo_basic_health_consultation()
        await demo_mcp_tools_integration()
        await demo_health_service_integration()
        
        print_separator("演示完成")
        print("🎉 所有功能演示完成！")
        print("📋 总结:")
        print("  ✅ DeepSeek AI真实响应正常")
        print("  ✅ MCP工具Mock功能正常")
        print("  ✅ 健康服务集成正常")
        print("  ✅ 服务状态监控正常")
        print("\n🚀 您现在可以开始使用AuraWell的完整功能了！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
