"""
Date and Time Utilities

This module provides utilities for working with dates, times, and time zones
in the context of health data and user activities.
"""

from datetime import datetime, date, time, timezone, timedelta
from typing import Optional, List, Tuple, Union
import pytz
import calendar


def get_current_utc() -> datetime:
    """
    Get current UTC datetime
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def get_current_user_time(user_timezone: str = "UTC") -> datetime:
    """
    Get current time in user's timezone
    
    Args:
        user_timezone: User's timezone string (e.g., "Asia/Shanghai")
        
    Returns:
        Current datetime in user's timezone
    """
    try:
        tz = pytz.timezone(user_timezone)
        return datetime.now(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        # Fallback to UTC if timezone is invalid
        return get_current_utc()


def convert_to_utc(dt: datetime, from_timezone: str) -> datetime:
    """
    Convert datetime from specific timezone to UTC
    
    Args:
        dt: Datetime to convert
        from_timezone: Source timezone string
        
    Returns:
        UTC datetime
    """
    if dt.tzinfo is None:
        # Assume it's in the specified timezone
        tz = pytz.timezone(from_timezone)
        dt = tz.localize(dt)
    
    return dt.astimezone(timezone.utc)


def convert_from_utc(dt: datetime, to_timezone: str) -> datetime:
    """
    Convert UTC datetime to specific timezone
    
    Args:
        dt: UTC datetime
        to_timezone: Target timezone string
        
    Returns:
        Datetime in target timezone
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    tz = pytz.timezone(to_timezone)
    return dt.astimezone(tz)


def get_date_range(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime]
) -> List[date]:
    """
    Get list of dates between start and end dates (inclusive)
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of dates
    """
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates


def get_week_boundaries(target_date: Union[date, datetime]) -> Tuple[date, date]:
    """
    Get the start and end dates of the week containing the target date
    (Monday as first day of week)
    
    Args:
        target_date: Target date
        
    Returns:
        Tuple of (week_start, week_end)
    """
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    # Monday is 0, Sunday is 6
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def get_month_boundaries(target_date: Union[date, datetime]) -> Tuple[date, date]:
    """
    Get the start and end dates of the month containing the target date
    
    Args:
        target_date: Target date
        
    Returns:
        Tuple of (month_start, month_end)
    """
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    month_start = target_date.replace(day=1)
    
    # Get last day of month
    _, last_day = calendar.monthrange(target_date.year, target_date.month)
    month_end = target_date.replace(day=last_day)
    
    return month_start, month_end


def get_days_ago(days: int, from_date: Optional[Union[date, datetime]] = None) -> date:
    """
    Get date that is specified number of days ago
    
    Args:
        days: Number of days ago
        from_date: Reference date (default: today)
        
    Returns:
        Date N days ago
    """
    if from_date is None:
        from_date = date.today()
    elif isinstance(from_date, datetime):
        from_date = from_date.date()
    
    return from_date - timedelta(days=days)


def get_time_of_day_category(dt: datetime) -> str:
    """
    Categorize time of day
    
    Args:
        dt: Datetime to categorize
        
    Returns:
        Time category: "early_morning", "morning", "afternoon", "evening", "night"
    """
    hour = dt.hour
    
    if 5 <= hour < 8:
        return "early_morning"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 22:
        return "evening"
    else:
        return "night"


def is_weekend(target_date: Union[date, datetime]) -> bool:
    """
    Check if date is weekend (Saturday or Sunday)
    
    Args:
        target_date: Date to check
        
    Returns:
        True if weekend
    """
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    return target_date.weekday() >= 5  # Saturday is 5, Sunday is 6


def get_sleep_date(bedtime: datetime) -> date:
    """
    Get the date associated with a sleep session
    Convention: sleep sessions before 12 PM belong to the previous day
    
    Args:
        bedtime: Bedtime datetime
        
    Returns:
        Sleep date
    """
    if bedtime.hour < 12:
        # If bedtime is before noon, it belongs to previous day
        return (bedtime - timedelta(days=1)).date()
    else:
        return bedtime.date()


def format_duration(total_seconds: int) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        total_seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if total_seconds < 0:
        return "0分钟"
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if seconds > 0 and hours == 0:  # Only show seconds if less than 1 hour
        parts.append(f"{seconds}秒")
    
    return "".join(parts) if parts else "0分钟"


def format_time_period(start_time: datetime, end_time: datetime, timezone_str: str = "UTC") -> str:
    """
    Format time period for display
    
    Args:
        start_time: Start time
        end_time: End time
        timezone_str: Timezone for display
        
    Returns:
        Formatted time period string
    """
    if timezone_str != "UTC":
        start_time = convert_from_utc(start_time, timezone_str)
        end_time = convert_from_utc(end_time, timezone_str)
    
    if start_time.date() == end_time.date():
        # Same day
        return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
    else:
        # Different days
        return f"{start_time.strftime('%m-%d %H:%M')} - {end_time.strftime('%m-%d %H:%M')}"


def get_age_in_years(birth_date: date, reference_date: Optional[date] = None) -> int:
    """
    Calculate age in years
    
    Args:
        birth_date: Date of birth
        reference_date: Reference date (default: today)
        
    Returns:
        Age in years
    """
    if reference_date is None:
        reference_date = date.today()
    
    age = reference_date.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if reference_date.month < birth_date.month or \
       (reference_date.month == birth_date.month and reference_date.day < birth_date.day):
        age -= 1
    
    return age


def get_days_between(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> int:
    """
    Get number of days between two dates
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of days (positive if end_date is after start_date)
    """
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    return (end_date - start_date).days


def is_same_week(date1: Union[date, datetime], date2: Union[date, datetime]) -> bool:
    """
    Check if two dates are in the same week
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        True if same week
    """
    week1_start, week1_end = get_week_boundaries(date1)
    week2_start, week2_end = get_week_boundaries(date2)
    
    return week1_start == week2_start


def get_relative_time_description(target_time: datetime, reference_time: Optional[datetime] = None) -> str:
    """
    Get relative time description in Chinese
    
    Args:
        target_time: Target time
        reference_time: Reference time (default: now)
        
    Returns:
        Relative time description
    """
    if reference_time is None:
        reference_time = get_current_utc()
    
    diff = target_time - reference_time
    diff_seconds = diff.total_seconds()
    
    if abs(diff_seconds) < 60:
        return "刚刚"
    elif abs(diff_seconds) < 3600:
        minutes = abs(diff_seconds) // 60
        if diff_seconds > 0:
            return f"{int(minutes)}分钟后"
        else:
            return f"{int(minutes)}分钟前"
    elif abs(diff_seconds) < 86400:
        hours = abs(diff_seconds) // 3600
        if diff_seconds > 0:
            return f"{int(hours)}小时后"
        else:
            return f"{int(hours)}小时前"
    else:
        days = abs(diff_seconds) // 86400
        if diff_seconds > 0:
            return f"{int(days)}天后"
        else:
            return f"{int(days)}天前"


def get_workout_time_category(workout_time: datetime) -> str:
    """
    Categorize workout time for analysis
    
    Args:
        workout_time: Workout datetime
        
    Returns:
        Workout time category
    """
    hour = workout_time.hour
    
    if 5 <= hour < 9:
        return "早晨"
    elif 9 <= hour < 12:
        return "上午"
    elif 12 <= hour < 14:
        return "午间"
    elif 14 <= hour < 17:
        return "下午"
    elif 17 <= hour < 20:
        return "傍晚"
    else:
        return "晚间"


def create_sleep_schedule_boundaries(
    bedtime_str: str,
    wake_time_str: str,
    timezone_str: str = "UTC"
) -> Tuple[time, time]:
    """
    Create sleep schedule time boundaries
    
    Args:
        bedtime_str: Bedtime string (HH:MM format)
        wake_time_str: Wake time string (HH:MM format)
        timezone_str: Timezone string
        
    Returns:
        Tuple of (bedtime, wake_time) as time objects
    """
    try:
        bedtime = time.fromisoformat(bedtime_str)
        wake_time = time.fromisoformat(wake_time_str)
        return bedtime, wake_time
    except ValueError:
        # Default sleep schedule
        return time(23, 0), time(7, 0)


def get_recommended_sleep_window(
    target_wake_time: time,
    target_sleep_duration_hours: float
) -> time:
    """
    Calculate recommended bedtime based on wake time and desired sleep duration
    
    Args:
        target_wake_time: Desired wake time
        target_sleep_duration_hours: Desired sleep duration in hours
        
    Returns:
        Recommended bedtime
    """
    # Convert to minutes for easier calculation
    wake_minutes = target_wake_time.hour * 60 + target_wake_time.minute
    sleep_duration_minutes = int(target_sleep_duration_hours * 60)
    
    # Calculate bedtime
    bedtime_minutes = wake_minutes - sleep_duration_minutes
    
    # Handle negative values (bedtime on previous day)
    if bedtime_minutes < 0:
        bedtime_minutes += 24 * 60
    
    bedtime_hour = bedtime_minutes // 60
    bedtime_minute = bedtime_minutes % 60
    
    return time(bedtime_hour, bedtime_minute) 