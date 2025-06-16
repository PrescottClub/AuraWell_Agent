"""
LangChain Agent Services Module

This module provides health advice services and parsers
for the LangChain-based health assistant.
"""

try:
    # Import health advice services for module access
    # from .health_advice_service import HealthAdviceService
    # from .parsers import FiveSectionParser, HealthAdviceResponse, HealthAdviceSection

    __all__ = [
        # "HealthAdviceService",
        # "FiveSectionParser",
        # "HealthAdviceResponse",
        # "HealthAdviceSection"
    ]

except ImportError as e:
    # Handle import errors gracefully
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(f"Import error in services module: {e}")
    __all__ = []
