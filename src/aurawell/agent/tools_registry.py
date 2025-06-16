"""
简化的HealthToolsRegistry - 保持API兼容性
现在主要功能由LangChain Agent提供，这里只保留基本接口
"""
from typing import List, Dict, Callable, Any
import logging

logger = logging.getLogger(__name__)


class HealthToolsRegistry:
    """
    简化的健康工具注册中心
    保持API兼容性，实际功能由LangChain Agent提供
    """
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[dict] = []
        logger.info("HealthToolsRegistry initialized (compatibility mode)")
    
    def register_tool(self, name: str, func: Callable, schema: dict):
        """注册工具（兼容性方法）"""
        self.tools[name] = func
        self.tool_schemas.append(schema)
        logger.debug(f"Tool registered: {name}")
    
    def get_tool(self, name: str) -> Callable:
        """获取工具函数（兼容性方法）"""
        return self.tools.get(name)
    
    def get_tools_schema(self) -> List[dict]:
        """获取工具schema（兼容性方法）"""
        return self.tool_schemas
    
    def list_tools(self) -> List[str]:
        """列出所有工具名称（兼容性方法）"""
        return list(self.tools.keys())
    
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        执行工具（兼容性方法）
        现在返回基本响应，实际功能由LangChain Agent处理
        """
        logger.info(f"Tool execution requested: {tool_name} (compatibility mode)")
        
        # 返回兼容的响应格式
        return {
            "success": True,
            "message": f"Tool {tool_name} executed successfully",
            "data": {},
            "tool_name": tool_name,
            "processed_by": "compatibility_registry"
        }
