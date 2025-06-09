"""
Error handling middleware for AuraWell API

Provides centralized error handling and standardized error responses.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..models.error_codes import ErrorCode, get_error_message, create_error_details
from ..models.api_models import ErrorResponse


logger = logging.getLogger(__name__)


class AuraWellException(Exception):
    """Base exception for AuraWell application"""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode, 
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AuraWellException):
    """Validation error exception"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = create_error_details(
            ErrorCode.INVALID_INPUT,
            field=field,
            value=value
        )
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationException(AuraWellException):
    """Authentication error exception"""
    
    def __init__(self, message: str = None, error_code: ErrorCode = ErrorCode.UNAUTHORIZED):
        super().__init__(
            message=message or get_error_message(error_code),
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(AuraWellException):
    """Authorization error exception"""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or get_error_message(ErrorCode.FORBIDDEN),
            error_code=ErrorCode.FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundException(AuraWellException):
    """Resource not found exception"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            error_code=ErrorCode.USER_NOT_FOUND,  # Generic not found
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ExternalServiceException(AuraWellException):
    """External service error exception"""
    
    def __init__(self, message: str, service_name: str = None):
        details = {}
        if service_name:
            details["service_name"] = service_name
            
        super().__init__(
            message=message,
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


async def aurawell_exception_handler(request: Request, exc: AuraWellException) -> JSONResponse:
    """Handle AuraWell custom exceptions"""
    logger.warning(
        f"AuraWell exception: {exc.error_code.value} - {exc.message}",
        extra={
            "error_code": exc.error_code.value,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "details": exc.details
        }
    )
    
    error_response = ErrorResponse(
        message=exc.message,
        error_code=exc.error_code.value,
        details=exc.details
    )
    
    # Convert to dict and handle datetime serialization
    content = error_response.model_dump()
    content["timestamp"] = content["timestamp"].isoformat()
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    # Map HTTP status codes to error codes
    error_code_mapping = {
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.USER_NOT_FOUND,
        422: ErrorCode.INVALID_INPUT,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        502: ErrorCode.EXTERNAL_API_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }
    
    error_code = error_code_mapping.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "detail": exc.detail
        }
    )
    
    error_response = ErrorResponse(
        message=exc.detail,
        error_code=error_code.value,
        details={"path": str(request.url.path)}
    )
    
    # Convert to dict and handle datetime serialization
    content = error_response.model_dump()
    content["timestamp"] = content["timestamp"].isoformat()
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation exceptions"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    logger.warning(
        f"Validation error: {len(errors)} validation errors",
        extra={
            "path": str(request.url.path),
            "errors": errors
        }
    )
    
    error_response = ErrorResponse(
        message="Validation failed",
        error_code=ErrorCode.INVALID_INPUT.value,
        details={
            "path": str(request.url.path),
            "validation_errors": errors
        }
    )
    
    # Convert to dict and handle datetime serialization
    content = error_response.model_dump()
    content["timestamp"] = content["timestamp"].isoformat()
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "path": str(request.url.path),
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    
    error_response = ErrorResponse(
        message="Internal server error",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        details={
            "path": str(request.url.path),
            "exception_type": type(exc).__name__
        }
    )
    
    # Convert to dict and handle datetime serialization
    content = error_response.model_dump()
    content["timestamp"] = content["timestamp"].isoformat()
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )
