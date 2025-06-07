"""
AuraWell - 超个性化健康生活方式编排AI Agent

A personalized health lifestyle orchestration AI Agent that integrates 
fitness goals, daily routines, dietary preferences, work schedules, 
and social activities to provide contextual recommendations and habit formation support.
"""

__version__ = "1.0.0-M1"
__author__ = "AuraWell Team"
__description__ = "Personalized Health Lifestyle Orchestration AI Agent"

# M1阶段新增模块
from .agent import HealthToolsRegistry, ConversationAgent
from .interfaces import cli_interface

# Core modules - explicit imports to avoid circular dependencies
# Ensure only existing and relevant modules are imported
# from .core import DeepSeekClient, AuraWellOrchestrator # Example, adjust as needed
# from .models import UserProfile, UnifiedActivitySummary # Example, adjust as needed
# from .integrations import GenericHealthAPIClient # Example, adjust as needed
# from .utils import calculate_bmi, calculate_bmr # Example, adjust as needed

# Removed references to services, database, monitoring as per simplification
