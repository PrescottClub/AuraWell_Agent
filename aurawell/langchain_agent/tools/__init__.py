"""
LangChain 工具适配器模块
将现有的健康工具适配到LangChain框架
"""

from .adapter import ToolAdapter
from .health_tools import LangChainHealthTools

__all__ = ["ToolAdapter", "LangChainHealthTools"]
