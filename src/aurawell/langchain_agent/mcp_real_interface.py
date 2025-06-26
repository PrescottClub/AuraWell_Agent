#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实MCP工具接口实现
使用官方MCP Python SDK连接真实的MCP服务器
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """MCP服务器配置"""
    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    timeout: float = 30.0


class RealMCPInterface:
    """
    真实MCP工具接口
    连接实际的MCP服务器并提供工具调用功能
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.available_tools: Dict[str, Any] = {}
        self._initialized = False
        
        # 配置内置MCP服务器
        self._setup_default_servers()
    
    def _setup_default_servers(self):
        """配置默认的MCP服务器"""
        
        # 计算器服务器（使用官方示例）
        self.servers["calculator"] = MCPServerConfig(
            name="calculator",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-math"],
            env=None
        )
        
        # 搜索服务器（需要API密钥）
        self.servers["brave_search"] = MCPServerConfig(
            name="brave_search", 
            command="npx",
            args=["-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": "your_brave_api_key_here"}
        )
        
        # 文件系统服务器
        self.servers["filesystem"] = MCPServerConfig(
            name="filesystem",
            command="npx", 
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            env=None
        )
        
        # 时间服务器
        self.servers["time"] = MCPServerConfig(
            name="time",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-time"],
            env=None
        )
        
        # SQLite数据库服务器
        self.servers["sqlite"] = MCPServerConfig(
            name="sqlite",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "./aurawell.db"],
            env=None
        )
    
    async def initialize(self):
        """初始化所有MCP服务器连接"""
        if self._initialized:
            return
            
        logger.info("🚀 初始化真实MCP服务器连接...")
        
        successful_connections = 0
        
        for server_name, config in self.servers.items():
            try:
                await self._connect_to_server(server_name, config)
                successful_connections += 1
                logger.info(f"✅ 成功连接到MCP服务器: {server_name}")
            except Exception as e:
                logger.warning(f"⚠️ 连接MCP服务器失败 {server_name}: {e}")
                # 继续尝试其他服务器
        
        logger.info(f"🎉 MCP服务器初始化完成: {successful_connections}/{len(self.servers)} 服务器可用")
        self._initialized = True
    
    async def _connect_to_server(self, server_name: str, config: MCPServerConfig):
        """连接到单个MCP服务器"""
        server_params = StdioServerParameters(
            command=config.command,
            args=config.args,
            env=config.env
        )
        
        # 启动服务器并建立连接
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport
        
        # 创建客户端会话
        session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        
        # 初始化会话
        await asyncio.wait_for(session.initialize(), timeout=config.timeout)
        
        # 获取可用工具
        tools_response = await session.list_tools()
        
        # 存储会话和工具信息
        self.sessions[server_name] = session
        for tool in tools_response.tools:
            tool_key = f"{server_name}.{tool.name}"
            self.available_tools[tool_key] = {
                "server": server_name,
                "tool": tool,
                "session": session
            }
    
    async def list_available_tools(self) -> Dict[str, Any]:
        """列出所有可用的MCP工具"""
        if not self._initialized:
            await self.initialize()
        
        tools_summary = {}
        for tool_key, tool_info in self.available_tools.items():
            tool = tool_info["tool"]
            tools_summary[tool_key] = {
                "name": tool.name,
                "description": tool.description,
                "server": tool_info["server"],
                "input_schema": tool.inputSchema
            }
        
        return tools_summary
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        if not self._initialized:
            await self.initialize()
        
        # 查找工具
        tool_info = None
        for tool_key, info in self.available_tools.items():
            if tool_key.endswith(f".{tool_name}") or info["tool"].name == tool_name:
                tool_info = info
                break
        
        if not tool_info:
            raise ValueError(f"工具未找到: {tool_name}")
        
        session = tool_info["session"]
        actual_tool_name = tool_info["tool"].name
        
        try:
            # 调用真实的MCP工具
            result = await session.call_tool(actual_tool_name, arguments)
            
            return {
                "success": True,
                "result": result.content,
                "tool_name": actual_tool_name,
                "server": tool_info["server"]
            }
            
        except Exception as e:
            logger.error(f"MCP工具调用失败 {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": actual_tool_name,
                "server": tool_info["server"]
            }
    
    # 具体工具方法 - 映射到真实MCP工具
    
    async def calculator_calculate(self, expression: str) -> Dict[str, Any]:
        """使用真实的MCP数学服务器进行计算"""
        return await self.call_tool("calculate", {"expression": expression})
    
    async def database_query(self, query: str) -> Dict[str, Any]:
        """使用真实的MCP SQLite服务器查询数据库"""
        return await self.call_tool("query", {"sql": query})
    
    async def brave_search(self, query: str, count: int = 5) -> Dict[str, Any]:
        """使用真实的Brave搜索MCP服务器"""
        return await self.call_tool("search", {"query": query, "count": count})
    
    async def filesystem_read(self, path: str) -> Dict[str, Any]:
        """使用真实的文件系统MCP服务器读取文件"""
        return await self.call_tool("read_file", {"path": path})
    
    async def filesystem_write(self, path: str, content: str) -> Dict[str, Any]:
        """使用真实的文件系统MCP服务器写入文件"""
        return await self.call_tool("write_file", {"path": path, "content": content})
    
    async def get_current_time(self) -> Dict[str, Any]:
        """使用真实的时间MCP服务器获取当前时间"""
        return await self.call_tool("get_time", {})
    
    async def cleanup(self):
        """清理所有MCP连接"""
        logger.info("🧹 清理MCP服务器连接...")
        await self.exit_stack.aclose()
        self.sessions.clear()
        self.available_tools.clear()
        self._initialized = False


# 全局实例
_real_mcp_interface = None


async def get_real_mcp_interface() -> RealMCPInterface:
    """获取全局真实MCP接口实例"""
    global _real_mcp_interface
    if _real_mcp_interface is None:
        _real_mcp_interface = RealMCPInterface()
        await _real_mcp_interface.initialize()
    return _real_mcp_interface


async def test_real_mcp_connection():
    """测试真实MCP连接"""
    print("🧪 测试真实MCP连接...")
    
    interface = await get_real_mcp_interface()
    
    # 列出可用工具
    tools = await interface.list_available_tools()
    print(f"📋 可用工具: {list(tools.keys())}")
    
    # 测试计算器
    try:
        calc_result = await interface.calculator_calculate("2 + 3 * 4")
        print(f"🧮 计算结果: {calc_result}")
    except Exception as e:
        print(f"❌ 计算器测试失败: {e}")
    
    # 测试时间
    try:
        time_result = await interface.get_current_time()
        print(f"⏰ 当前时间: {time_result}")
    except Exception as e:
        print(f"❌ 时间测试失败: {e}")
    
    await interface.cleanup()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_real_mcp_connection()) 