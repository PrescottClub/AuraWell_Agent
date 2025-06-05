"""
AuraWell Logging Configuration

This module configures logging for the AuraWell application, including
structured logging, security-aware log filtering, and audit trails.
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

from .settings import settings


class SecurityLogFilter(logging.Filter):
    """
    Filter to remove sensitive information from logs
    """
    
    SENSITIVE_PATTERNS = [
        'api_key', 'password', 'token', 'secret', 'auth',
        'credential', 'private_key', 'client_secret'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records to remove sensitive information
        
        Args:
            record: Log record to filter
            
        Returns:
            True if record should be logged, False otherwise
        """
        # Check message content
        message = str(record.getMessage()).lower()
        
        # Filter out logs containing sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                # Replace sensitive info with placeholder
                record.msg = self._sanitize_message(record.msg)
                break
        
        return True
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize message by replacing sensitive information"""
        import re
        
        # Replace potential API keys and tokens
        patterns = [
            (r'(api_key|token|secret|password)[\s=:]+([^\s]+)', r'\1=***REDACTED***'),
            (r'(Bearer\s+)([^\s]+)', r'\1***REDACTED***'),
            (r'([a-zA-Z0-9]{32,})', lambda m: m.group(1)[:4] + '***REDACTED***' if len(m.group(1)) > 10 else m.group(1))
        ]
        
        sanitized = str(message)
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized


class AuraWellFormatter(logging.Formatter):
    """
    Custom formatter for AuraWell logs with structured output
    """
    
    def __init__(self, include_context: bool = True):
        """
        Initialize the formatter
        
        Args:
            include_context: Whether to include additional context in logs
        """
        self.include_context = include_context
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add thread and process info if available
        if hasattr(record, 'thread') and hasattr(record, 'process'):
            log_entry["thread_id"] = record.thread
            log_entry["process_id"] = record.process
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add custom context if available
        if self.include_context and hasattr(record, 'context'):
            log_entry["context"] = record.context
        
        # Add user context for audit trail
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        # Add request context for API calls
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_structured: bool = True
) -> None:
    """
    Setup logging configuration for AuraWell
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_console: Whether to enable console logging
        enable_structured: Whether to use structured JSON logging
    """
    log_level = log_level or settings.LOG_LEVEL
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configure formatters
    if enable_structured:
        formatter = AuraWellFormatter(include_context=True)
        console_formatter = AuraWellFormatter(include_context=False)
    else:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        formatter = logging.Formatter(format_string)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    
    # Configure handlers
    handlers = []
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(SecurityLogFilter())
        handlers.append(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SecurityLogFilter())
        handlers.append(file_handler)
    
    # Error file handler (separate file for errors)
    if log_file:
        error_file = log_file.replace('.log', '_errors.log')
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        error_handler.addFilter(SecurityLogFilter())
        handlers.append(error_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Configure specific loggers
    configure_aurawell_loggers(log_level)
    
    # Log configuration info
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, Structured: {enable_structured}")


def configure_aurawell_loggers(log_level: str) -> None:
    """
    Configure specific loggers for AuraWell components
    
    Args:
        log_level: Base logging level
    """
    # AuraWell component loggers
    loggers_config = {
        'aurawell.core': log_level,
        'aurawell.integrations': log_level,
        'aurawell.models': log_level,
        'aurawell.utils': log_level,
        'aurawell.config': log_level,
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))
    
    # External library loggers (usually more verbose)
    external_loggers = {
        'requests': 'WARNING',
        'urllib3': 'WARNING',
        'openai': 'INFO',
        'httpx': 'WARNING'
    }
    
    for logger_name, level in external_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))


def get_audit_logger() -> logging.Logger:
    """
    Get a specialized logger for audit events
    
    Returns:
        Configured audit logger
    """
    audit_logger = logging.getLogger('aurawell.audit')
    
    # Ensure audit logger has appropriate handler
    if not audit_logger.handlers:
        audit_file = os.path.join('logs', 'audit.log')
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(audit_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        handler = logging.FileHandler(audit_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        handler.setFormatter(AuraWellFormatter(include_context=True))
        
        audit_logger.addHandler(handler)
        audit_logger.setLevel(logging.INFO)
        audit_logger.propagate = False  # Don't propagate to root logger
    
    return audit_logger


def log_health_data_access(
    user_id: str,
    platform: str,
    data_type: str,
    action: str,
    success: bool,
    additional_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log health data access for audit purposes
    
    Args:
        user_id: User identifier
        platform: Health platform name
        data_type: Type of health data accessed
        action: Action performed (read, write, delete)
        success: Whether the action was successful
        additional_context: Additional context information
    """
    audit_logger = get_audit_logger()
    
    audit_entry = {
        "event_type": "health_data_access",
        "user_id": user_id,
        "platform": platform,
        "data_type": data_type,
        "action": action,
        "success": success,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if additional_context:
        audit_entry["context"] = additional_context
    
    # Use extra parameter to pass structured data
    audit_logger.info(
        f"Health data access: {action} {data_type} from {platform} for user {user_id}",
        extra={"context": audit_entry}
    )


def log_ai_interaction(
    user_id: str,
    interaction_type: str,
    model_used: str,
    token_usage: Optional[Dict[str, int]] = None,
    success: bool = True,
    additional_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log AI interactions for audit and monitoring
    
    Args:
        user_id: User identifier
        interaction_type: Type of AI interaction
        model_used: AI model used
        token_usage: Token usage information
        success: Whether the interaction was successful
        additional_context: Additional context information
    """
    audit_logger = get_audit_logger()
    
    audit_entry = {
        "event_type": "ai_interaction",
        "user_id": user_id,
        "interaction_type": interaction_type,
        "model_used": model_used,
        "success": success,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if token_usage:
        audit_entry["token_usage"] = token_usage
    
    if additional_context:
        audit_entry["context"] = additional_context
    
    audit_logger.info(
        f"AI interaction: {interaction_type} using {model_used} for user {user_id}",
        extra={"context": audit_entry}
    )


def log_recommendation_generated(
    user_id: str,
    recommendation_type: str,
    recommendations_count: int,
    context_factors: List[str],
    confidence_score: Optional[float] = None
) -> None:
    """
    Log recommendation generation for analysis and improvement
    
    Args:
        user_id: User identifier
        recommendation_type: Type of recommendations generated
        recommendations_count: Number of recommendations generated
        context_factors: Factors that influenced the recommendations
        confidence_score: Overall confidence score
    """
    audit_logger = get_audit_logger()
    
    audit_entry = {
        "event_type": "recommendation_generated",
        "user_id": user_id,
        "recommendation_type": recommendation_type,
        "count": recommendations_count,
        "context_factors": context_factors,
        "confidence_score": confidence_score,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    audit_logger.info(
        f"Generated {recommendations_count} {recommendation_type} recommendations for user {user_id}",
        extra={"context": audit_entry}
    )


# Default logging configuration
DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
        },
        'json': {
            '()': AuraWellFormatter,
            'include_context': True
        }
    },
    'filters': {
        'security_filter': {
            '()': SecurityLogFilter
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['security_filter']
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/aurawell.log',
            'formatter': 'json',
            'filters': ['security_filter']
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/aurawell_errors.log',
            'formatter': 'detailed',
            'filters': ['security_filter']
        }
    },
    'loggers': {
        'aurawell': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'aurawell.audit': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}


# 特定功能的日志记录器
health_data_logger = logging.getLogger("aurawell.health_data")
ai_interaction_logger = logging.getLogger("aurawell.ai_interaction")
recommendation_logger = logging.getLogger("aurawell.recommendations")
audit_logger = logging.getLogger("aurawell.audit")
gamification_logger = logging.getLogger("aurawell.gamification")


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_file='logs/aurawell.log' if not settings.DEBUG else None,
        enable_console=True,
        enable_structured=not settings.DEBUG
    ) 