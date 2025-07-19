"""
AuraWell Core Module

Contains the core functionality of AuraWell including AI integration,
data processing, and orchestration logic.
"""

from .deepseek_client import DeepSeekClient, DeepSeekResponse
from .service_factory import (
    ServiceClientFactory,
    get_deepseek_client,
    get_mcp_tools_interface,
    MCPToolProtocol,
    MockMCPToolInterface
)
from .orchestrator_v2 import AuraWellOrchestrator, HealthInsight, HealthPlan
