"""
Error Handling for AuraWell

Provides comprehensive error handling, logging, and recovery mechanisms.
"""

import logging
import traceback
import functools
from typing import Dict, List, Optional, Any, Callable, Type
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories"""
    VALIDATION = "validation"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    AI_SERVICE = "ai_service"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Error context information"""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    service_name: Optional[str] = None
    operation: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class AuraWellException(Exception):
    """Base exception class for AuraWell"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR",
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[ErrorContext] = None,
                 cause: Optional[Exception] = None):
        """
        Initialize AuraWell exception
        
        Args:
            message: Error message
            error_code: Unique error code
            category: Error category
            severity: Error severity
            context: Error context information
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
        self.cause = cause
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "message": self.message,
            "error_code": self.error_code,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "context": {
                "user_id": self.context.user_id,
                "request_id": self.context.request_id,
                "service_name": self.context.service_name,
                "operation": self.context.operation,
                "additional_data": self.context.additional_data
            },
            "cause": str(self.cause) if self.cause else None
        }


class ValidationError(AuraWellException):
    """Validation error"""
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        self.field = field


class DatabaseError(AuraWellException):
    """Database error"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class ExternalAPIError(AuraWellException):
    """External API error"""
    def __init__(self, message: str, api_name: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EXTERNAL_API_ERROR",
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.api_name = api_name
        self.status_code = status_code


class AIServiceError(AuraWellException):
    """AI service error"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            category=ErrorCategory.AI_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ErrorHandler:
    """
    Centralized error handling system
    
    Provides error logging, categorization, and recovery mechanisms.
    """
    
    def __init__(self):
        """Initialize error handler"""
        self.logger = logging.getLogger(__name__)
        self._error_counts: Dict[str, int] = {}
        self._error_history: List[Dict[str, Any]] = []
        self._max_history_size = 1000
        self._recovery_strategies: Dict[ErrorCategory, Callable] = {}
        
        # Register default recovery strategies
        self._register_default_recovery_strategies()
    
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None) -> AuraWellException:
        """
        Handle an error and convert it to AuraWell exception
        
        Args:
            error: Original exception
            context: Error context
            
        Returns:
            AuraWell exception
        """
        # Convert to AuraWell exception if needed
        if isinstance(error, AuraWellException):
            aurawell_error = error
        else:
            aurawell_error = self._convert_to_aurawell_exception(error, context)
        
        # Log the error
        self._log_error(aurawell_error)
        
        # Update error statistics
        self._update_error_stats(aurawell_error)
        
        # Add to error history
        self._add_to_history(aurawell_error)
        
        # Attempt recovery if strategy exists
        self._attempt_recovery(aurawell_error)
        
        return aurawell_error
    
    def _convert_to_aurawell_exception(self, error: Exception, context: Optional[ErrorContext]) -> AuraWellException:
        """Convert generic exception to AuraWell exception"""
        error_type = type(error).__name__
        message = str(error)
        
        # Categorize error based on type and message
        category = self._categorize_error(error)
        severity = self._determine_severity(error, category)
        
        # Generate error code
        error_code = f"{category.value.upper()}_{error_type.upper()}"
        
        return AuraWellException(
            message=message,
            error_code=error_code,
            category=category,
            severity=severity,
            context=context,
            cause=error
        )
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message"""
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()
        
        # Database errors
        if any(keyword in error_type for keyword in ['database', 'sql', 'connection']):
            return ErrorCategory.DATABASE
        if any(keyword in error_message for keyword in ['database', 'sql', 'connection', 'table']):
            return ErrorCategory.DATABASE
        
        # Network errors
        if any(keyword in error_type for keyword in ['connection', 'timeout', 'network']):
            return ErrorCategory.NETWORK
        if any(keyword in error_message for keyword in ['connection', 'timeout', 'network', 'unreachable']):
            return ErrorCategory.NETWORK
        
        # Validation errors
        if any(keyword in error_type for keyword in ['validation', 'value']):
            return ErrorCategory.VALIDATION
        if any(keyword in error_message for keyword in ['invalid', 'required', 'missing']):
            return ErrorCategory.VALIDATION
        
        # Authentication/Authorization errors
        if any(keyword in error_message for keyword in ['unauthorized', 'forbidden', 'authentication']):
            return ErrorCategory.AUTHENTICATION
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        error_message = str(error).lower()
        
        # Critical errors
        if category == ErrorCategory.SYSTEM:
            return ErrorSeverity.CRITICAL
        if any(keyword in error_message for keyword in ['critical', 'fatal', 'crash']):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category == ErrorCategory.DATABASE:
            return ErrorSeverity.HIGH
        if any(keyword in error_message for keyword in ['security', 'breach', 'corruption']):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.EXTERNAL_API, ErrorCategory.AI_SERVICE]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        if category == ErrorCategory.VALIDATION:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM
    
    def _log_error(self, error: AuraWellException) -> None:
        """Log error with appropriate level"""
        error_dict = error.to_dict()
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error: {error.message}", extra=error_dict)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {error.message}", extra=error_dict)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {error.message}", extra=error_dict)
        else:
            self.logger.info(f"Low severity error: {error.message}", extra=error_dict)
        
        # Log stack trace for debugging
        if error.cause:
            self.logger.debug(f"Original exception: {traceback.format_exception(type(error.cause), error.cause, error.cause.__traceback__)}")
    
    def _update_error_stats(self, error: AuraWellException) -> None:
        """Update error statistics"""
        self._error_counts[error.error_code] = self._error_counts.get(error.error_code, 0) + 1
        self._error_counts[f"category_{error.category.value}"] = self._error_counts.get(f"category_{error.category.value}", 0) + 1
        self._error_counts[f"severity_{error.severity.value}"] = self._error_counts.get(f"severity_{error.severity.value}", 0) + 1
    
    def _add_to_history(self, error: AuraWellException) -> None:
        """Add error to history"""
        self._error_history.append(error.to_dict())
        
        # Trim history if too large
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size:]
    
    def _attempt_recovery(self, error: AuraWellException) -> None:
        """Attempt error recovery using registered strategies"""
        recovery_strategy = self._recovery_strategies.get(error.category)
        if recovery_strategy:
            try:
                recovery_strategy(error)
                self.logger.info(f"Recovery attempted for error: {error.error_code}")
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed for error {error.error_code}: {recovery_error}")
    
    def _register_default_recovery_strategies(self) -> None:
        """Register default recovery strategies"""
        self._recovery_strategies[ErrorCategory.DATABASE] = self._recover_database_error
        self._recovery_strategies[ErrorCategory.EXTERNAL_API] = self._recover_api_error
        self._recovery_strategies[ErrorCategory.NETWORK] = self._recover_network_error
    
    def _recover_database_error(self, error: AuraWellException) -> None:
        """Attempt to recover from database errors"""
        # In a real implementation, this might:
        # - Retry the operation
        # - Switch to a backup database
        # - Use cached data
        self.logger.info("Attempting database error recovery")
    
    def _recover_api_error(self, error: AuraWellException) -> None:
        """Attempt to recover from API errors"""
        # In a real implementation, this might:
        # - Retry with exponential backoff
        # - Switch to alternative API
        # - Use cached responses
        self.logger.info("Attempting API error recovery")
    
    def _recover_network_error(self, error: AuraWellException) -> None:
        """Attempt to recover from network errors"""
        # In a real implementation, this might:
        # - Retry the request
        # - Switch to alternative endpoint
        # - Queue for later processing
        self.logger.info("Attempting network error recovery")
    
    def register_recovery_strategy(self, category: ErrorCategory, strategy: Callable) -> None:
        """Register custom recovery strategy"""
        self._recovery_strategies[category] = strategy
        self.logger.info(f"Registered recovery strategy for category: {category.value}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "error_counts": self._error_counts.copy(),
            "total_errors": sum(self._error_counts.values()),
            "history_size": len(self._error_history),
            "recovery_strategies": list(self._recovery_strategies.keys())
        }
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors from history"""
        return self._error_history[-limit:]


def error_handler_decorator(error_handler: ErrorHandler, context: Optional[ErrorContext] = None):
    """
    Decorator for automatic error handling
    
    Args:
        error_handler: Error handler instance
        context: Error context
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handled_error = error_handler.handle_error(e, context)
                raise handled_error
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                handled_error = error_handler.handle_error(e, context)
                raise handled_error
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator
