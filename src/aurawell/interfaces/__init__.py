"""
AuraWell Interfaces 模块

M1阶段：用户交互接口
M2阶段：FastAPI REST API接口
"""

from . import cli_interface
from .api_interface import app

__all__ = ["cli_interface", "app"]
