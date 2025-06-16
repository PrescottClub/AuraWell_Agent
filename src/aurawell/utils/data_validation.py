"""
Data Validation Utilities

This module provides validation functions for health data to ensure
data quality and consistency across the AuraWell platform.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import re
import logging

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format

    Args:
        phone: Phone number to validate

    Returns:
        True if valid phone format, False otherwise
    """
    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)
    # Check if it's between 10-15 digits
    return 10 <= len(digits_only) <= 15


def validate_date_string(date_str: str) -> bool:
    """
    Validate date string in YYYY-MM-DD format

    Args:
        date_str: Date string to validate

    Returns:
        True if valid date format, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_health_metrics(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate health metrics data

    Args:
        data: Dictionary containing health metrics

    Returns:
        Dictionary with validation errors (empty if all valid)
    """
    errors = {}

    # Validate steps
    if "steps" in data:
        if not isinstance(data["steps"], (int, type(None))) or (
            data["steps"] is not None and data["steps"] < 0
        ):
            errors.setdefault("steps", []).append(
                "Steps must be a non-negative integer or None"
            )

    # Validate weight
    if "weight_kg" in data:
        if not isinstance(data["weight_kg"], (float, int, type(None))) or (
            data["weight_kg"] is not None and not 20 <= data["weight_kg"] <= 300
        ):
            errors.setdefault("weight_kg", []).append(
                "Weight must be between 20-300 kg"
            )

    # Validate height
    if "height_cm" in data:
        if not isinstance(data["height_cm"], (float, int, type(None))) or (
            data["height_cm"] is not None and not 50 <= data["height_cm"] <= 250
        ):
            errors.setdefault("height_cm", []).append(
                "Height must be between 50-250 cm"
            )

    # Validate heart rate
    if "heart_rate_bpm" in data:
        if not isinstance(data["heart_rate_bpm"], (int, type(None))) or (
            data["heart_rate_bpm"] is not None
            and not 30 <= data["heart_rate_bpm"] <= 220
        ):
            errors.setdefault("heart_rate_bpm", []).append(
                "Heart rate must be between 30-220 BPM"
            )

    # Validate sleep duration
    if "sleep_hours" in data:
        if not isinstance(data["sleep_hours"], (float, int, type(None))) or (
            data["sleep_hours"] is not None and not 0 <= data["sleep_hours"] <= 24
        ):
            errors.setdefault("sleep_hours", []).append(
                "Sleep hours must be between 0-24"
            )

    return errors


def sanitize_user_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        input_str: User input string

    Returns:
        Sanitized string
    """
    if not isinstance(input_str, str):
        return str(input_str)

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', "", input_str)
    # Limit length
    sanitized = sanitized[:1000]
    # Strip whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format

    Args:
        api_key: API key to validate

    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(api_key, str):
        return False

    # API key should be at least 16 characters and contain only alphanumeric and specific symbols
    if len(api_key) < 16:
        return False

    # Check for valid characters (alphanumeric, hyphens, underscores)
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, api_key))


def validate_data_quality_score(score: float) -> bool:
    """
    Validate data quality score

    Args:
        score: Quality score to validate

    Returns:
        True if valid score (0.0-1.0), False otherwise
    """
    return isinstance(score, (float, int)) and 0.0 <= score <= 1.0


def validate_user_id(user_id: str) -> bool:
    """
    验证用户ID格式

    Args:
        user_id: 用户ID

    Returns:
        True if valid user ID, False otherwise
    """
    if not isinstance(user_id, str):
        return False

    # 用户ID应该是非空字符串，长度在3-50之间，只包含字母数字和下划线
    if not user_id or len(user_id) < 3 or len(user_id) > 50:
        return False

    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, user_id))


def validate_date_range(date_range: str) -> bool:
    """
    验证日期范围格式

    Args:
        date_range: 日期范围字符串，格式如 "2024-01-01_to_2024-01-07"

    Returns:
        True if valid date range format, False otherwise
    """
    if not isinstance(date_range, str):
        return False

    try:
        if "_to_" not in date_range:
            return False

        start_str, end_str = date_range.split("_to_")

        # 验证日期格式
        if not validate_date_string(start_str.strip()) or not validate_date_string(
            end_str.strip()
        ):
            return False

        # 验证日期逻辑
        start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d").date()

        return start_date <= end_date

    except (ValueError, AttributeError):
        return False


def validate_goals(goals: Dict[str, Any]) -> bool:
    """
    验证健康目标数据

    Args:
        goals: 健康目标字典

    Returns:
        True if valid goals data, False otherwise
    """
    if not isinstance(goals, dict) or not goals:
        return False

    valid_goal_keys = {
        "daily_steps",
        "sleep_hours",
        "daily_calories",
        "weight_target",
        "target_date",
    }

    # 检查是否包含有效的目标键
    if not any(key in goals for key in valid_goal_keys):
        return False

    # 验证各个目标值
    if "daily_steps" in goals:
        if (
            not isinstance(goals["daily_steps"], (int, float))
            or not 1000 <= goals["daily_steps"] <= 50000
        ):
            return False

    if "sleep_hours" in goals:
        if (
            not isinstance(goals["sleep_hours"], (int, float))
            or not 4.0 <= goals["sleep_hours"] <= 12.0
        ):
            return False

    if "daily_calories" in goals:
        if (
            not isinstance(goals["daily_calories"], (int, float))
            or not 200 <= goals["daily_calories"] <= 5000
        ):
            return False

    if "weight_target" in goals:
        if (
            not isinstance(goals["weight_target"], (int, float))
            or not 30 <= goals["weight_target"] <= 300
        ):
            return False

    if "target_date" in goals:
        if goals["target_date"] is not None:
            if not isinstance(goals["target_date"], str):
                return False
            if not validate_date_string(goals["target_date"]):
                return False

    return True
