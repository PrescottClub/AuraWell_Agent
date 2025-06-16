"""
Error codes and messages for AuraWell API

Defines standardized error codes and messages for consistent error handling
across the application.
"""

from enum import Enum
from typing import Dict, Any


class ErrorCode(str, Enum):
    """Standardized error codes"""

    # Authentication errors (1000-1099)
    INVALID_CREDENTIALS = "AUTH_1001"
    TOKEN_EXPIRED = "AUTH_1002"
    TOKEN_INVALID = "AUTH_1003"
    UNAUTHORIZED = "AUTH_1004"
    FORBIDDEN = "AUTH_1005"

    # Validation errors (1100-1199)
    INVALID_INPUT = "VALIDATION_1101"
    MISSING_REQUIRED_FIELD = "VALIDATION_1102"
    INVALID_FORMAT = "VALIDATION_1103"
    VALUE_OUT_OF_RANGE = "VALIDATION_1104"
    INVALID_DATE_RANGE = "VALIDATION_1105"

    # User errors (1200-1299)
    USER_NOT_FOUND = "USER_1201"
    USER_ALREADY_EXISTS = "USER_1202"
    PROFILE_UPDATE_FAILED = "USER_1203"

    # Health data errors (1300-1399)
    HEALTH_DATA_NOT_FOUND = "HEALTH_1301"
    INVALID_HEALTH_GOAL = "HEALTH_1302"
    GOAL_ALREADY_EXISTS = "HEALTH_1303"
    ACTIVITY_DATA_ERROR = "HEALTH_1304"
    SLEEP_DATA_ERROR = "HEALTH_1305"

    # AI/Chat errors (1400-1499)
    AI_SERVICE_UNAVAILABLE = "AI_1401"
    CHAT_PROCESSING_ERROR = "AI_1402"
    TOOL_EXECUTION_ERROR = "AI_1403"
    INTENT_RECOGNITION_ERROR = "AI_1404"

    # External API errors (1500-1599)
    EXTERNAL_API_ERROR = "EXTERNAL_1501"
    RATE_LIMIT_EXCEEDED = "EXTERNAL_1502"
    THIRD_PARTY_UNAVAILABLE = "EXTERNAL_1503"

    # Database errors (1600-1699)
    DATABASE_ERROR = "DB_1601"
    CONNECTION_ERROR = "DB_1602"
    TRANSACTION_FAILED = "DB_1603"

    # System errors (1700-1799)
    INTERNAL_SERVER_ERROR = "SYSTEM_1701"
    SERVICE_UNAVAILABLE = "SYSTEM_1702"
    TIMEOUT_ERROR = "SYSTEM_1703"
    CONFIGURATION_ERROR = "SYSTEM_1704"


# Error messages mapping
ERROR_MESSAGES: Dict[ErrorCode, str] = {
    # Authentication
    ErrorCode.INVALID_CREDENTIALS: "Invalid username or password",
    ErrorCode.TOKEN_EXPIRED: "Authentication token has expired",
    ErrorCode.TOKEN_INVALID: "Invalid authentication token",
    ErrorCode.UNAUTHORIZED: "Authentication required",
    ErrorCode.FORBIDDEN: "Access denied",
    # Validation
    ErrorCode.INVALID_INPUT: "Invalid input data provided",
    ErrorCode.MISSING_REQUIRED_FIELD: "Required field is missing",
    ErrorCode.INVALID_FORMAT: "Data format is invalid",
    ErrorCode.VALUE_OUT_OF_RANGE: "Value is outside acceptable range",
    ErrorCode.INVALID_DATE_RANGE: "Invalid date range specified",
    # User
    ErrorCode.USER_NOT_FOUND: "User not found",
    ErrorCode.USER_ALREADY_EXISTS: "User already exists",
    ErrorCode.PROFILE_UPDATE_FAILED: "Failed to update user profile",
    # Health data
    ErrorCode.HEALTH_DATA_NOT_FOUND: "Health data not found",
    ErrorCode.INVALID_HEALTH_GOAL: "Invalid health goal parameters",
    ErrorCode.GOAL_ALREADY_EXISTS: "Health goal already exists",
    ErrorCode.ACTIVITY_DATA_ERROR: "Error processing activity data",
    ErrorCode.SLEEP_DATA_ERROR: "Error processing sleep data",
    # AI/Chat
    ErrorCode.AI_SERVICE_UNAVAILABLE: "AI service is currently unavailable",
    ErrorCode.CHAT_PROCESSING_ERROR: "Error processing chat message",
    ErrorCode.TOOL_EXECUTION_ERROR: "Error executing tool function",
    ErrorCode.INTENT_RECOGNITION_ERROR: "Error recognizing user intent",
    # External API
    ErrorCode.EXTERNAL_API_ERROR: "External API error",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
    ErrorCode.THIRD_PARTY_UNAVAILABLE: "Third-party service unavailable",
    # Database
    ErrorCode.DATABASE_ERROR: "Database operation failed",
    ErrorCode.CONNECTION_ERROR: "Database connection error",
    ErrorCode.TRANSACTION_FAILED: "Database transaction failed",
    # System
    ErrorCode.INTERNAL_SERVER_ERROR: "Internal server error",
    ErrorCode.SERVICE_UNAVAILABLE: "Service temporarily unavailable",
    ErrorCode.TIMEOUT_ERROR: "Request timeout",
    ErrorCode.CONFIGURATION_ERROR: "System configuration error",
}


def get_error_message(error_code: ErrorCode) -> str:
    """Get error message for given error code"""
    return ERROR_MESSAGES.get(error_code, "Unknown error")


def create_error_details(
    error_code: ErrorCode,
    field: str = None,
    value: Any = None,
    additional_info: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Create standardized error details"""
    details = {"error_code": error_code.value, "message": get_error_message(error_code)}

    if field:
        details["field"] = field

    if value is not None:
        details["value"] = str(value)

    if additional_info:
        details.update(additional_info)

    return details
