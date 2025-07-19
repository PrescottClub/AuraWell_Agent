#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具测试运行脚本
快速验证MCP工具系统的功能
"""

import asyncio
import sys
import os
from pathlib import Path
import json
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def quick_test():
    """快速测试MCP工具基本功能"""
    logger.info("🚀 开始MCP工具快速测试...")
    
    try:
        from src.aurawell.langchain_agent.mcp_tools_enhanced import EnhancedMCPTools, ToolExecutionMode
        
        # 创建增强工具实例（占位符模式）
        tools = EnhancedMCPTools(ToolExecutionMode.PLACEHOLDER)
        
        # 测试核心工具
        test_cases = [
            ("calculator", "calculate", {"expression": "2 + 3"}),
            ("time", "get_time", {}),
            ("database-sqlite", "query", {"table": "health_data"}),
            ("weather", "get_weather", {"location": "北京"}),
            ("memory", "store", {"data": {"test": "value"}})
        ]
        
        results = []
        
        for tool_name, action, params in test_cases:
            try:
                result = await tools.call_tool(tool_name, action, params)
                results.append({
                    "tool": tool_name,
                    "action": action,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "mode": result.mode_used.value
                })
                
                status = "✅" if result.success else "❌"
                logger.info(f"{status} {tool_name}: {result.execution_time:.3f}s")
                
            except Exception as e:
                logger.error(f"❌ {tool_name} 测试失败: {e}")
                results.append({
                    "tool": tool_name,
                    "action": action,
                    "success": False,
                    "error": str(e)
                })
        
        # 统计结果
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get("success", False))
        success_rate = (successful_tests / total_tests) * 100
        
        logger.info(f"🎉 快速测试完成: {successful_tests}/{total_tests} 通过 ({success_rate:.1f}%)")
        
        return {
            "success": success_rate >= 80,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ 快速测试失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def test_performance_monitor():
    """测试性能监控器"""
    logger.info("📊 测试性能监控器...")
    
    try:
        from src.aurawell.langchain_agent.mcp_performance_monitor import MCPPerformanceMonitor
        
        # 创建内存数据库监控器
        monitor = MCPPerformanceMonitor(":memory:")
        
        # 记录一些测试指标
        monitor.record_metric("test_tool", "test_action", 0.1, True, "placeholder")
        monitor.record_metric("test_tool", "test_action", 0.2, True, "placeholder")
        monitor.record_metric("test_tool", "test_action", 0.15, False, "placeholder", "test error")
        
        # 刷新到数据库
        await monitor._flush_metrics()
        
        # 获取摘要
        summary = await monitor.get_performance_summary(hours=1)
        
        logger.info(f"✅ 性能监控器测试通过")
        logger.info(f"   - 总调用: {summary['overall']['total_calls']}")
        logger.info(f"   - 成功率: {summary['overall']['success_rate']:.1f}%")
        
        await monitor.cleanup()
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ 性能监控器测试失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def test_api_endpoints():
    """测试API端点（模拟）"""
    logger.info("🌐 测试API端点...")
    
    try:
        # 这里只是验证导入是否正常
        from src.aurawell.langchain_agent.mcp_tools_manager_v2 import MCPToolsManagerV2, ToolMode
        
        manager = MCPToolsManagerV2(ToolMode.PLACEHOLDER)
        await manager.initialize()
        
        # 获取性能报告
        report = manager.get_performance_report()
        
        logger.info("✅ API端点相关组件测试通过")
        
        return {
            "success": True,
            "manager_mode": manager.tool_mode.value,
            "has_report": bool(report)
        }
        
    except Exception as e:
        logger.error(f"❌ API端点测试失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def main():
    """主测试函数"""
    logger.info("🎯 开始MCP工具系统测试...")
    
    test_results = {}
    
    # 运行各项测试
    test_results["quick_test"] = await quick_test()
    test_results["performance_monitor"] = await test_performance_monitor()
    test_results["api_endpoints"] = await test_api_endpoints()
    
    # 计算总体结果
    all_success = all(result.get("success", False) for result in test_results.values())
    
    # 输出结果
    print("\n" + "="*50)
    print("MCP工具系统测试结果")
    print("="*50)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result.get("success", False) else "❌ 失败"
        print(f"{test_name}: {status}")
        
        if not result.get("success", False) and "error" in result:
            print(f"  错误: {result['error']}")
    
    print(f"\n总体结果: {'✅ 所有测试通过' if all_success else '❌ 部分测试失败'}")
    
    # 保存详细结果到文件
    results_file = project_root / "test_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"📄 详细测试结果已保存到: {results_file}")
    
    return 0 if all_success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("🛑 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 测试运行异常: {e}")
        sys.exit(1)
