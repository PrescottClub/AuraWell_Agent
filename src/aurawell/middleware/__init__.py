"""
AuraWell Middleware Module

Provides middleware components for the FastAPI application.
"""

from .cors_middleware import configure_cors, get_cors_config
from .error_handler import (
    AuraWellException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ExternalServiceException,
    aurawell_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

__all__ = [
    "configure_cors",
    "get_cors_config",
    "AuraWellException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "ExternalServiceException",
    "aurawell_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "general_exception_handler"
]
