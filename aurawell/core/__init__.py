"""
AuraWell Core Module

Contains the core functionality of AuraWell including AI integration,
data processing, and orchestration logic.
"""

from .deepseek_client import DeepSeekClient, DeepSeekResponse
from .orchestrator_v2 import AuraWellOrchestrator, HealthInsight, HealthPlan
