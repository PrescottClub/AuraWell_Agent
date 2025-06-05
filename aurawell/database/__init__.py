"""
AuraWell Database Layer

Provides data persistence and retrieval functionality for AuraWell.
Supports multiple database backends with a unified interface.
"""

from .connection import DatabaseManager
from .repositories import (
    UserRepository, HealthDataRepository, InsightRepository, PlanRepository
)
from .models import (
    UserModel, HealthDataModel, InsightModel, PlanModel
)

__all__ = [
    'DatabaseManager',
    'UserRepository',
    'HealthDataRepository', 
    'InsightRepository',
    'PlanRepository',
    'UserModel',
    'HealthDataModel',
    'InsightModel',
    'PlanModel'
]
