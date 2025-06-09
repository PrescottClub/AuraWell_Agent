"""
AuraWell - 超个性化健康生活方式编排AI Agent

A personalized health lifestyle orchestration AI Agent that integrates 
fitness goals, daily routines, dietary preferences, work schedules, 
and social activities to provide contextual recommendations and habit formation support.
"""

__version__ = "0.5.0"
__author__ = "AuraWell Team"
__description__ = "Personalized Health Lifestyle Orchestration AI Agent"

# Core modules - 现在使用LangChain Agent，保留兼容性接口
from .interfaces import cli_interface
from .langchain_agent.agent import LangChainAgent
from .agent import HealthToolsRegistry  # 保持API兼容性

# v0.4.0 新增：数据库层
from .database import DatabaseManager, get_database_manager
from .services import DatabaseService
from .repositories import UserRepository, HealthDataRepository, AchievementRepository

# 核心数据模型
from .models.user_profile import UserProfile
from .models.health_data_model import UnifiedActivitySummary, UnifiedSleepSession
from .models.enums import HealthPlatform, DataQuality

# 工具函数
from .utils import calculate_bmi, calculate_bmr

__all__ = [
    # 版本信息
    "__version__", "__author__", "__description__",

    # 智能代理 - 现在使用LangChain Agent，保留兼容性
    "LangChainAgent", "HealthToolsRegistry", "cli_interface",

    # 数据库层
    "DatabaseManager", "get_database_manager", "DatabaseService",
    "UserRepository", "HealthDataRepository", "AchievementRepository",

    # 数据模型
    "UserProfile", "UnifiedActivitySummary", "UnifiedSleepSession",
    "HealthPlatform", "DataQuality",

    # 工具函数
    "calculate_bmi", "calculate_bmr",
]
