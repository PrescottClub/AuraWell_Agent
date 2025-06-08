"""
AuraWell Middleware Module

Provides middleware components for the FastAPI application.
"""

from .cors_middleware import configure_cors, get_cors_config

__all__ = [
    "configure_cors",
    "get_cors_config"
]
