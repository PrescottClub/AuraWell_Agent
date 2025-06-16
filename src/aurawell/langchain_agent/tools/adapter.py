"""
工具适配器
将现有的健康工具适配到LangChain框架
"""
import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ToolAdapter(ABC):
    """
    工具适配器基类
    负责将现有工具适配到LangChain框架
    """

    def __init__(self, name: str, description: str):
        """
        初始化工具适配器

        Args:
            name: 工具名称
            description: 工具描述
        """
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            Dict[str, Any]: 执行结果
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具的参数模式

        Returns:
            Dict[str, Any]: 参数模式
        """
        pass

    def to_langchain_tool(self):
        """
        转换为LangChain工具格式

        Returns:
            LangChain工具实例
        """
        # For now, return a mock tool interface
        # In production, this would create a proper LangChain tool
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.get_schema(),
            "execute": self.execute
        }


class HealthToolAdapter(ToolAdapter):
    """
    健康工具适配器
    将现有的健康工具适配到LangChain框架
    """

    def __init__(self, name: str, description: str, original_tool: Callable):
        """
        初始化健康工具适配器

        Args:
            name: 工具名称
            description: 工具描述
            original_tool: 原始工具函数
        """
        super().__init__(name, description)
        self.original_tool = original_tool

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行健康工具

        Args:
            **kwargs: 工具参数

        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            logger.info(f"执行健康工具: {self.name}, 参数: {kwargs}")

            # 调用原始工具
            if asyncio.iscoroutinefunction(self.original_tool):
                result = await self.original_tool(**kwargs)
            else:
                result = self.original_tool(**kwargs)

            # 检查原始工具是否返回了错误状态
            if isinstance(result, dict) and result.get("success") is False:
                # 如果原始工具返回失败，直接传播错误
                return {
                    "success": False,
                    "tool_name": self.name,
                    "error": result.get("error", "Unknown error"),
                    "message": result.get("message", f"工具 {self.name} 执行失败"),
                    "result": result  # 保留原始结果以供调试
                }
            
            # 标准化成功返回格式
            return {
                "success": True,
                "tool_name": self.name,
                "result": result,
                "message": f"工具 {self.name} 执行成功"
            }

        except Exception as e:
            logger.error(f"健康工具 {self.name} 执行失败: {e}")
            return {
                "success": False,
                "tool_name": self.name,
                "error": str(e),
                "message": f"工具 {self.name} 执行失败"
            }

    def get_schema(self) -> Dict[str, Any]:
        """
        获取健康工具的参数模式

        Returns:
            Dict[str, Any]: 参数模式
        """
        # Extract basic schema from function inspection
        import inspect

        try:
            sig = inspect.signature(self.original_tool)
            properties = {}
            required = []

            for param_name, param in sig.parameters.items():
                if param_name in ['self', 'args', 'kwargs']:
                    continue

                param_type = "string"  # Default type
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"

                properties[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name} for {self.name}"
                }

                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            return {
                "type": "object",
                "properties": properties,
                "required": required
            }
        except Exception as e:
            logger.warning(f"Could not extract schema for {self.name}: {e}")
            return {
                "type": "object",
                "properties": {},
                "required": []
            }


class ToolRegistry:
    """
    工具注册表
    管理所有可用的LangChain工具适配器
    """

    def __init__(self):
        self._tools: Dict[str, ToolAdapter] = {}

    def register_tool(self, tool: ToolAdapter) -> None:
        """
        注册工具

        Args:
            tool: 工具适配器实例
        """
        self._tools[tool.name] = tool
        logger.info(f"工具 {tool.name} 已注册")

    def get_tool(self, name: str) -> Optional[ToolAdapter]:
        """
        获取工具

        Args:
            name: 工具名称

        Returns:
            Optional[ToolAdapter]: 工具适配器实例
        """
        return self._tools.get(name)

    def get_all_tools(self) -> List[ToolAdapter]:
        """
        获取所有工具

        Returns:
            List[ToolAdapter]: 所有工具适配器列表
        """
        return list(self._tools.values())

    def get_tool_names(self) -> List[str]:
        """
        获取所有工具名称

        Returns:
            List[str]: 工具名称列表
        """
        return list(self._tools.keys())

    async def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        执行工具

        Args:
            name: 工具名称
            **kwargs: 工具参数

        Returns:
            Dict[str, Any]: 执行结果
        """
        tool = self.get_tool(name)
        if tool is None:
            return {
                "success": False,
                "error": f"工具 {name} 不存在",
                "message": f"未找到工具 {name}"
            }

        return await tool.execute(**kwargs)


# 全局工具注册表实例
tool_registry = ToolRegistry()
