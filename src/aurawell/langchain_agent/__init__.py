"""
LangChain Agent 模块
提供基于LangChain框架的对话代理实现
"""

from .agent import HealthAdviceAgent

# 为了保持兼容性，创建别名
LangChainAgent = HealthAdviceAgent

__all__ = ["LangChainAgent", "HealthAdviceAgent"]
