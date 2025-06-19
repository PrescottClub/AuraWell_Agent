"""
Dashboard-related data models for AuraWell

This module contains all Pydantic models related to dashboard functionality,
including dashboard data, reports, leaderboards, and metrics.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# Define base response classes for now to avoid circular imports
class BaseResponse(BaseModel):
    """Base response model"""

    success: bool = True
    status: str = "success"
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseResponse):
    """Success response model"""

    data: Any = None


# ================================
# Dashboard Models
# ================================


class DashboardMetric(BaseModel):
    """Dashboard metric model"""

    name: str
    value: float
    unit: str
    trend: Optional[str] = None  # 'up', 'down', 'stable'
    change_percentage: Optional[float] = None


class DashboardData(BaseModel):
    """Dashboard overview data"""

    user_id: str
    metrics: List[DashboardMetric]
    last_updated: datetime = Field(default_factory=datetime.now)


class DashboardResponse(SuccessResponse):
    """Dashboard data response"""

    data: Optional[DashboardData] = None


# ================================
# Report Models
# ================================


class ReportData(BaseModel):
    """Report data model"""

    report_id: str
    title: str
    content: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.now)


class ReportResponse(SuccessResponse):
    """Report response"""

    data: Optional[ReportData] = None


# ================================
# Leaderboard Models
# ================================


class LeaderboardEntry(BaseModel):
    """Leaderboard entry model"""

    rank: int
    user_id: str
    display_name: str
    score: float
    metric_name: str


class LeaderboardData(BaseModel):
    """Leaderboard data model"""

    entries: List[LeaderboardEntry]
    total_participants: int
    metric_name: str
    period: str  # 'daily', 'weekly', 'monthly'


class LeaderboardResponse(SuccessResponse):
    """Leaderboard response"""

    data: Optional[LeaderboardData] = None
