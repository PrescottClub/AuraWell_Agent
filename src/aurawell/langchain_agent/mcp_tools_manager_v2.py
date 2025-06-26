#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP智能工具管理器 v2.0 - 真实MCP集成版本
支持真实MCP工具和占位符工具的混合使用
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .mcp_tools_manager import MCPToolsManager, IntentAnalyzer, WorkflowResult
from .mcp_interface import MCPToolInterface

logger = logging.getLogger(__name__)


class ToolMode(Enum):
    """工具模式"""
    REAL_MCP = "real_mcp"        # 使用真实MCP工具
    PLACEHOLDER = "placeholder"   # 使用占位符工具
    HYBRID = "hybrid"            # 混合模式：优先真实，降级到占位符


@dataclass
class ToolCallResult:
    """工具调用结果"""
    success: bool
    result: Any
    tool_name: str
    mode_used: ToolMode
    error: Optional[str] = None
    execution_time: float = 0.0


class MCPToolsManagerV2(MCPToolsManager):
    """
    MCP智能工具管理器 v2.0
    
    新特性：
    - 支持真实MCP工具连接
    - 混合模式：真实工具优先，占位符降级
    - 改进的错误处理和重试机制
    - 工具性能监控
    """
    
    def __init__(self, tool_mode: ToolMode = ToolMode.HYBRID):
        super().__init__()
        self.tool_mode = tool_mode
        self.real_mcp_interface = None
        self.placeholder_interface = MCPToolInterface()
        self.tool_performance_stats = {}
        
        logger.info(f"🚀 初始化MCP工具管理器v2.0，模式: {tool_mode.value}")
    
    async def initialize(self):
        """初始化工具管理器"""
        if self.tool_mode in [ToolMode.REAL_MCP, ToolMode.HYBRID]:
            try:
                # 尝试初始化真实MCP接口
                from .mcp_real_interface import get_real_mcp_interface
                self.real_mcp_interface = await get_real_mcp_interface()
                logger.info("✅ 真实MCP接口初始化成功")
            except ImportError:
                logger.warning("⚠️ 真实MCP依赖未安装，请运行: pip install 'mcp[cli]'")
                if self.tool_mode == ToolMode.REAL_MCP:
                    raise RuntimeError("真实MCP模式需要安装MCP依赖")
                self.tool_mode = ToolMode.PLACEHOLDER
            except Exception as e:
                logger.warning(f"⚠️ 真实MCP接口初始化失败: {e}")
                if self.tool_mode == ToolMode.REAL_MCP:
                    raise
                self.tool_mode = ToolMode.PLACEHOLDER
        
        logger.info(f"🎯 最终工具模式: {self.tool_mode.value}")
    
    async def call_tool_smart(self, tool_name: str, action: str, parameters: Dict[str, Any]) -> ToolCallResult:
        """
        智能工具调用
        根据模式选择真实MCP工具或占位符工具
        """
        start_time = asyncio.get_event_loop().time()
        
        # 混合模式：优先尝试真实工具
        if self.tool_mode == ToolMode.HYBRID and self.real_mcp_interface:
            try:
                result = await self._call_real_mcp_tool(tool_name, action, parameters)
                execution_time = asyncio.get_event_loop().time() - start_time
                self._update_performance_stats(tool_name, True, execution_time)
                return ToolCallResult(
                    success=True,
                    result=result,
                    tool_name=tool_name,
                    mode_used=ToolMode.REAL_MCP,
                    execution_time=execution_time
                )
            except Exception as e:
                logger.warning(f"⚠️ 真实MCP工具调用失败，降级到占位符: {e}")
                # 降级到占位符
                result = await self._call_placeholder_tool(tool_name, action, parameters)
                execution_time = asyncio.get_event_loop().time() - start_time
                return ToolCallResult(
                    success=True,
                    result=result,
                    tool_name=tool_name,
                    mode_used=ToolMode.PLACEHOLDER,
                    execution_time=execution_time
                )
        
        # 真实MCP模式
        elif self.tool_mode == ToolMode.REAL_MCP:
            try:
                result = await self._call_real_mcp_tool(tool_name, action, parameters)
                execution_time = asyncio.get_event_loop().time() - start_time
                self._update_performance_stats(tool_name, True, execution_time)
                return ToolCallResult(
                    success=True,
                    result=result,
                    tool_name=tool_name,
                    mode_used=ToolMode.REAL_MCP,
                    execution_time=execution_time
                )
            except Exception as e:
                execution_time = asyncio.get_event_loop().time() - start_time
                self._update_performance_stats(tool_name, False, execution_time)
                return ToolCallResult(
                    success=False,
                    result=None,
                    tool_name=tool_name,
                    mode_used=ToolMode.REAL_MCP,
                    error=str(e),
                    execution_time=execution_time
                )
        
        # 占位符模式
        else:
            try:
                result = await self._call_placeholder_tool(tool_name, action, parameters)
                execution_time = asyncio.get_event_loop().time() - start_time
                return ToolCallResult(
                    success=True,
                    result=result,
                    tool_name=tool_name,
                    mode_used=ToolMode.PLACEHOLDER,
                    execution_time=execution_time
                )
            except Exception as e:
                execution_time = asyncio.get_event_loop().time() - start_time
                return ToolCallResult(
                    success=False,
                    result=None,
                    tool_name=tool_name,
                    mode_used=ToolMode.PLACEHOLDER,
                    error=str(e),
                    execution_time=execution_time
                )
    
    async def _call_real_mcp_tool(self, tool_name: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用真实MCP工具"""
        if not self.real_mcp_interface:
            raise RuntimeError("真实MCP接口未初始化")
        
        # 映射工具名称到真实MCP方法
        tool_mapping = {
            "database_sqlite": self._call_real_database,
            "calculator": self._call_real_calculator,
            "brave_search": self._call_real_search,
            "filesystem": self._call_real_filesystem,
            "time": self._call_real_time,
        }
        
        if tool_name in tool_mapping:
            return await tool_mapping[tool_name](action, parameters)
        else:
            # 尝试通用工具调用
            return await self.real_mcp_interface.call_tool(action, parameters)
    
    async def _call_placeholder_tool(self, tool_name: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用占位符工具"""
        result = await self.placeholder_interface.call_tool(tool_name, action, parameters, timeout=10.0)
        return result.data
    
    # 真实MCP工具映射方法
    
    async def _call_real_database(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用真实数据库工具"""
        if action == "query":
            return await self.real_mcp_interface.database_query(parameters.get("sql", ""))
        else:
            raise ValueError(f"不支持的数据库操作: {action}")
    
    async def _call_real_calculator(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用真实计算器工具"""
        if action == "calculate":
            return await self.real_mcp_interface.calculator_calculate(parameters.get("expression", ""))
        else:
            raise ValueError(f"不支持的计算器操作: {action}")
    
    async def _call_real_search(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用真实搜索工具"""
        if action == "search":
            return await self.real_mcp_interface.brave_search(
                parameters.get("query", ""),
                parameters.get("count", 5)
            )
        else:
            raise ValueError(f"不支持的搜索操作: {action}")
    
    async def _call_real_filesystem(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用真实文件系统工具"""
        if action == "read_file":
            return await self.real_mcp_interface.filesystem_read(parameters.get("path", ""))
        elif action == "write_file":
            return await self.real_mcp_interface.filesystem_write(
                parameters.get("path", ""),
                parameters.get("content", "")
            )
        else:
            raise ValueError(f"不支持的文件系统操作: {action}")
    
    async def _call_real_time(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用真实时间工具"""
        if action == "get_time":
            return await self.real_mcp_interface.get_current_time()
        else:
            raise ValueError(f"不支持的时间操作: {action}")
    
    def _update_performance_stats(self, tool_name: str, success: bool, execution_time: float):
        """更新工具性能统计"""
        if tool_name not in self.tool_performance_stats:
            self.tool_performance_stats[tool_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_execution_time": 0.0,
                "average_execution_time": 0.0
            }
        
        stats = self.tool_performance_stats[tool_name]
        stats["total_calls"] += 1
        stats["total_execution_time"] += execution_time
        stats["average_execution_time"] = stats["total_execution_time"] / stats["total_calls"]
        
        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
    
    async def execute_workflow_v2(self, workflow_name: str, user_input: str, context: Dict[str, Any]) -> WorkflowResult:
        """
        执行智能工作流 v2.0
        支持真实MCP工具和性能监控
        """
        logger.info(f"🔄 执行工作流 v2.0: {workflow_name}")
        
        # 获取工作流配置
        workflow_config = self.workflows.get(workflow_name)
        if not workflow_config:
            return WorkflowResult(
                success=False,
                workflow_name=workflow_name,
                results={},
                execution_summary="工作流配置不存在"
            )
        
        results = {}
        execution_summary = []
        
        # 执行工作流步骤
        for step in workflow_config["tools"]:
            tool_name = step["tool"]
            action = step["action"]
            parameters = step.get("parameters", {})
            
            # 参数化处理
            if "user_input" in parameters and parameters["user_input"] == "{{user_input}}":
                parameters["user_input"] = user_input
            
            try:
                # 使用智能工具调用
                result = await self.call_tool_smart(tool_name, action, parameters)
                
                results[f"{tool_name}_{action}"] = result.result
                execution_summary.append(
                    f"✅ {tool_name}.{action} ({result.mode_used.value}) - {result.execution_time:.2f}s"
                )
                
                if not result.success:
                    logger.warning(f"⚠️ 工具调用失败但继续执行: {result.error}")
                
            except Exception as e:
                error_msg = f"❌ {tool_name}.{action} 失败: {e}"
                execution_summary.append(error_msg)
                logger.error(error_msg)
        
        return WorkflowResult(
            success=True,
            workflow_name=workflow_name,
            results=results,
            execution_summary="\n".join(execution_summary),
            metadata={
                "tool_mode": self.tool_mode.value,
                "total_steps": len(workflow_config["tools"]),
                "completed_steps": len(results)
            }
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取工具性能报告"""
        return {
            "tool_mode": self.tool_mode.value,
            "performance_stats": self.tool_performance_stats,
            "summary": {
                "total_tools_used": len(self.tool_performance_stats),
                "total_calls": sum(stats["total_calls"] for stats in self.tool_performance_stats.values()),
                "overall_success_rate": (
                    sum(stats["successful_calls"] for stats in self.tool_performance_stats.values()) /
                    max(sum(stats["total_calls"] for stats in self.tool_performance_stats.values()), 1)
                ) * 100
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "tool_mode": self.tool_mode.value,
            "placeholder_interface": "available",
            "real_mcp_interface": "not_available"
        }
        
        # 检查真实MCP接口
        if self.real_mcp_interface:
            try:
                tools = await self.real_mcp_interface.list_available_tools()
                health_status["real_mcp_interface"] = "available"
                health_status["real_mcp_tools_count"] = len(tools)
            except Exception as e:
                health_status["real_mcp_interface"] = f"error: {e}"
        
        return health_status
    
    async def cleanup(self):
        """清理资源"""
        if self.real_mcp_interface:
            await self.real_mcp_interface.cleanup()
        logger.info("🧹 MCP工具管理器v2.0资源清理完成")


# 全局实例
_mcp_tools_manager_v2 = None


async def get_mcp_tools_manager_v2(tool_mode: ToolMode = ToolMode.HYBRID) -> MCPToolsManagerV2:
    """获取全局MCP工具管理器v2.0实例"""
    global _mcp_tools_manager_v2
    if _mcp_tools_manager_v2 is None:
        _mcp_tools_manager_v2 = MCPToolsManagerV2(tool_mode)
        await _mcp_tools_manager_v2.initialize()
    return _mcp_tools_manager_v2 