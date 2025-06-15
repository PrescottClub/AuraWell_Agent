"""
Custom Exception Classes for AuraWell

Defines custom exceptions for better error handling and user experience.
"""

from typing import Any, Dict, Optional


class AuraWellException(Exception):
    """Base exception class for AuraWell application"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "type": self.__class__.__name__
        }


class ValidationError(AuraWellException):
    """Raised when input validation fails"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        if field:
            self.details["field"] = field


class AuthenticationError(AuraWellException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)


class AuthorizationError(AuraWellException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, error_code="AUTHORIZATION_ERROR", **kwargs)


class NotFoundError(AuraWellException):
    """Raised when a resource is not found"""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, error_code="NOT_FOUND", **kwargs)


class ConflictError(AuraWellException):
    """Raised when a resource conflict occurs"""
    
    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(message, error_code="CONFLICT", **kwargs)


class BusinessLogicError(AuraWellException):
    """Raised when business logic constraints are violated"""
    
    def __init__(self, message: str = "Business logic error", **kwargs):
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR", **kwargs)


class ExternalServiceError(AuraWellException):
    """Raised when external service call fails"""
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", **kwargs)
        if service_name:
            self.details["service"] = service_name


class DatabaseError(AuraWellException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database error", **kwargs):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)


class ConfigurationError(AuraWellException):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)


class RateLimitError(AuraWellException):
    """Raised when rate limit is exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)
        if retry_after:
            self.details["retry_after"] = retry_after


class ServiceUnavailableError(AuraWellException):
    """Raised when service is temporarily unavailable"""
    
    def __init__(self, message: str = "Service unavailable", **kwargs):
        super().__init__(message, error_code="SERVICE_UNAVAILABLE", **kwargs) 