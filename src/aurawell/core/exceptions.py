"""
Custom Exception Classes for AuraWell

Defines custom exceptions for better error handling and user experience.
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AuraWellException(Exception):
    """Base exception class for AuraWell application with standardized error handling"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
        http_status: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.user_message = user_message or message
        self.http_status = http_status

        # Log the exception for debugging
        logger.error(
            f"AuraWellException: {self.error_code} - {message}",
            extra={
                "error_code": self.error_code,
                "details": self.details,
                "http_status": self.http_status,
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "message": self.user_message,
            "error_code": self.error_code,
            "details": self.details,
            "type": self.__class__.__name__,
        }


# Alias for backward compatibility and consistency
AurawellException = AuraWellException


class ValidationError(AuraWellException):
    """Raised when input validation fails"""

    def __init__(
        self, message: str = "Validation failed", field: Optional[str] = None, **kwargs
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            details=details,
            user_message=f"输入验证失败: {message}",
            http_status=400,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class AuthenticationError(AuraWellException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message,
            error_code="AUTH_ERROR",
            user_message="身份验证失败，请重新登录",
            http_status=401,
            **kwargs,
        )


class AuthorizationError(AuraWellException):
    """Raised when authorization fails"""

    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message,
            error_code="AUTHORIZATION_ERROR",
            user_message="权限不足，无法执行此操作",
            http_status=403,
            **kwargs,
        )


class NotFoundError(AuraWellException):
    """Raised when a resource is not found"""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        super().__init__(
            message,
            error_code="NOT_FOUND",
            details=details,
            user_message="请求的资源不存在",
            http_status=404,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class ConflictError(AuraWellException):
    """Raised when a resource conflict occurs"""

    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(
            message,
            error_code="CONFLICT",
            user_message="操作冲突，请检查当前状态后重试",
            http_status=409,
            **kwargs,
        )


class BusinessLogicError(AuraWellException):
    """Raised when business logic constraints are violated"""

    def __init__(self, message: str = "Business logic error", **kwargs):
        super().__init__(
            message,
            error_code="BUSINESS_LOGIC_ERROR",
            user_message="业务逻辑错误，请检查操作是否符合规则",
            http_status=422,
            **kwargs,
        )


class ExternalServiceError(AuraWellException):
    """Raised when external service call fails"""

    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if service_name:
            details["service"] = service_name
        super().__init__(
            message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            user_message="外部服务暂时不可用，请稍后重试",
            http_status=502,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class DatabaseError(AuraWellException):
    """Raised when database operation fails"""

    def __init__(
        self, message: str = "Database error", operation: Optional[str] = None, **kwargs
    ):
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            details=details,
            user_message="数据库操作失败，请稍后重试",
            http_status=500,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class ConfigurationError(AuraWellException):
    """Raised when configuration is invalid"""

    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(
            message,
            error_code="CONFIGURATION_ERROR",
            user_message="配置错误，请联系管理员",
            http_status=500,
            **kwargs,
        )


class RateLimitError(AuraWellException):
    """Raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            user_message=f"请求过于频繁，请{retry_after or 60}秒后重试",
            http_status=429,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class ServiceUnavailableError(AuraWellException):
    """Raised when service is temporarily unavailable"""

    def __init__(self, message: str = "Service unavailable", **kwargs):
        super().__init__(
            message,
            error_code="SERVICE_UNAVAILABLE",
            user_message="服务暂时不可用，请稍后重试",
            http_status=503,
            **kwargs,
        )
