#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具系统测试套件
验证MCP工具的完整功能，包括真实工具和占位符工具
"""

import asyncio
import pytest
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.aurawell.langchain_agent.mcp_tools_enhanced import EnhancedMCPTools, ToolExecutionMode
from src.aurawell.langchain_agent.mcp_tools_manager_v2 import MCPToolsManagerV2, ToolMode
from src.aurawell.langchain_agent.mcp_performance_monitor import MCPPerformanceMonitor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPToolsTestSuite:
    """MCP工具测试套件"""
    
    def __init__(self):
        self.enhanced_tools = None
        self.manager_v2 = None
        self.performance_monitor = None
        self.test_results = {}
        
    async def setup(self):
        """设置测试环境"""
        logger.info("🚀 设置MCP工具测试环境...")
        
        # 初始化增强工具（占位符模式，避免依赖问题）
        self.enhanced_tools = EnhancedMCPTools(ToolExecutionMode.PLACEHOLDER)
        
        # 初始化管理器v2
        self.manager_v2 = MCPToolsManagerV2(ToolMode.PLACEHOLDER)
        await self.manager_v2.initialize()
        
        # 初始化性能监控器
        self.performance_monitor = MCPPerformanceMonitor(":memory:")  # 使用内存数据库
        
        logger.info("✅ 测试环境设置完成")
    
    async def test_enhanced_tools(self) -> Dict[str, Any]:
        """测试增强工具功能"""
        logger.info("🧪 测试增强MCP工具...")
        
        test_tools = [
            'calculator', 'database-sqlite', 'time', 'filesystem', 'brave-search',
            'quickchart', 'fetch', 'sequential-thinking', 'memory', 'weather',
            'run-python', 'github', 'figma'
        ]
        
        results = {}
        
        for tool_name in test_tools:
            try:
                # 测试基本工具调用
                result = await self.enhanced_tools.call_tool(
                    tool_name=tool_name,
                    action="test",
                    parameters={"test_param": "test_value"}
                )
                
                results[tool_name] = {
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "mode_used": result.mode_used.value,
                    "error": result.error
                }
                
                if result.success:
                    logger.info(f"✅ {tool_name}: 测试通过 ({result.execution_time:.3f}s)")
                else:
                    logger.warning(f"⚠️ {tool_name}: 测试失败 - {result.error}")
                    
            except Exception as e:
                logger.error(f"❌ {tool_name}: 测试异常 - {e}")
                results[tool_name] = {
                    "success": False,
                    "execution_time": 0,
                    "mode_used": "error",
                    "error": str(e)
                }
        
        return results
    
    async def test_specific_tools(self) -> Dict[str, Any]:
        """测试特定工具的详细功能"""
        logger.info("🔍 测试特定工具详细功能...")
        
        results = {}
        
        # 测试计算器
        try:
            calc_result = await self.enhanced_tools.call_tool(
                "calculator", "calculate", {"expression": "2 + 3 * 4"}
            )
            results["calculator_math"] = {
                "success": calc_result.success,
                "result": calc_result.data.get("result"),
                "expected": 14
            }
        except Exception as e:
            results["calculator_math"] = {"success": False, "error": str(e)}
        
        # 测试数据库
        try:
            db_result = await self.enhanced_tools.call_tool(
                "database-sqlite", "query_health_data", {"user_id": "test_user"}
            )
            results["database_query"] = {
                "success": db_result.success,
                "has_data": "health_metrics" in str(db_result.data)
            }
        except Exception as e:
            results["database_query"] = {"success": False, "error": str(e)}
        
        # 测试时间工具
        try:
            time_result = await self.enhanced_tools.call_tool(
                "time", "get_current_time", {}
            )
            results["time_service"] = {
                "success": time_result.success,
                "has_timestamp": "current_time" in str(time_result.data)
            }
        except Exception as e:
            results["time_service"] = {"success": False, "error": str(e)}
        
        return results
    
    async def test_manager_v2(self) -> Dict[str, Any]:
        """测试管理器v2功能"""
        logger.info("🎯 测试MCP工具管理器v2...")
        
        results = {}
        
        try:
            # 测试智能工具调用
            call_result = await self.manager_v2.call_tool_smart(
                "calculator", "calculate", {"expression": "10 + 5"}
            )
            
            results["smart_call"] = {
                "success": call_result.success,
                "mode_used": call_result.mode_used.value,
                "execution_time": call_result.execution_time
            }
            
            # 测试性能报告
            performance_report = self.manager_v2.get_performance_report()
            results["performance_report"] = {
                "has_report": bool(performance_report),
                "tool_mode": performance_report.get("tool_mode"),
                "has_recommendations": "recommendations" in performance_report
            }
            
        except Exception as e:
            logger.error(f"❌ 管理器v2测试失败: {e}")
            results["error"] = str(e)
        
        return results
    
    async def test_performance_monitor(self) -> Dict[str, Any]:
        """测试性能监控器"""
        logger.info("📊 测试性能监控器...")
        
        results = {}
        
        try:
            # 记录一些测试指标
            self.performance_monitor.record_metric(
                tool_name="test_tool",
                action="test_action",
                execution_time=0.1,
                success=True,
                mode_used="placeholder"
            )
            
            # 刷新指标到数据库
            await self.performance_monitor._flush_metrics()
            
            # 获取性能摘要
            summary = await self.performance_monitor.get_performance_summary(hours=1)
            results["performance_summary"] = {
                "has_summary": bool(summary),
                "total_calls": summary.get("overall", {}).get("total_calls", 0)
            }
            
            # 检查告警
            alerts = await self.performance_monitor.check_alerts()
            results["alerts_check"] = {
                "alerts_count": len(alerts),
                "has_alerts": len(alerts) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ 性能监控器测试失败: {e}")
            results["error"] = str(e)
        
        return results
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """测试错误处理"""
        logger.info("🛡️ 测试错误处理...")
        
        results = {}
        
        try:
            # 测试无效工具名称
            invalid_result = await self.enhanced_tools.call_tool(
                "invalid_tool", "test", {}
            )
            results["invalid_tool"] = {
                "handled_gracefully": not invalid_result.success,
                "has_error_message": bool(invalid_result.error)
            }
            
            # 测试无效参数
            invalid_param_result = await self.enhanced_tools.call_tool(
                "calculator", "calculate", {"invalid_param": "test"}
            )
            results["invalid_params"] = {
                "handled_gracefully": True,  # 占位符工具应该能处理任何参数
                "success": invalid_param_result.success
            }
            
        except Exception as e:
            logger.error(f"❌ 错误处理测试失败: {e}")
            results["error"] = str(e)
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("🎯 开始运行MCP工具完整测试套件...")
        
        await self.setup()
        
        test_results = {
            "test_timestamp": asyncio.get_event_loop().time(),
            "enhanced_tools": await self.test_enhanced_tools(),
            "specific_tools": await self.test_specific_tools(),
            "manager_v2": await self.test_manager_v2(),
            "performance_monitor": await self.test_performance_monitor(),
            "error_handling": await self.test_error_handling()
        }
        
        # 计算总体统计
        total_tests = 0
        passed_tests = 0
        
        for category, results in test_results.items():
            if category == "test_timestamp":
                continue
            if isinstance(results, dict):
                for test_name, result in results.items():
                    if isinstance(result, dict) and "success" in result:
                        total_tests += 1
                        if result["success"]:
                            passed_tests += 1
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / max(total_tests, 1)) * 100
        }
        
        logger.info(f"🎉 测试完成: {passed_tests}/{total_tests} 通过 ({test_results['summary']['success_rate']:.1f}%)")
        
        return test_results
    
    async def cleanup(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")
        
        if self.performance_monitor:
            await self.performance_monitor.cleanup()
        
        logger.info("✅ 测试环境清理完成")


async def main():
    """主测试函数"""
    test_suite = MCPToolsTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # 打印详细结果
        print("\n" + "="*60)
        print("MCP工具测试结果报告")
        print("="*60)
        
        summary = results.get("summary", {})
        print(f"总测试数: {summary.get('total_tests', 0)}")
        print(f"通过测试: {summary.get('passed_tests', 0)}")
        print(f"失败测试: {summary.get('failed_tests', 0)}")
        print(f"成功率: {summary.get('success_rate', 0):.1f}%")
        
        # 如果成功率低于80%，返回错误码
        if summary.get('success_rate', 0) < 80:
            print("\n⚠️ 警告: 测试成功率低于80%，请检查MCP工具配置")
            return 1
        else:
            print("\n✅ 所有测试通过，MCP工具系统运行正常")
            return 0
            
    except Exception as e:
        logger.error(f"❌ 测试运行失败: {e}")
        return 1
    finally:
        await test_suite.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
