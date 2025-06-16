"""
AuraWell Utils Module

Contains utility functions and helper classes for the AuraWell system.
"""

# from .data_validation import *
from .date_utils import *
from .health_calculations import *
from .encryption_utils import *

# Performance and caching utilities
try:
    from .cache import (
        CacheManager,
        get_cache_manager,
        cache_user_data,
        cache_health_data,
        cache_ai_response,
        cache_achievements,
        invalidate_user_cache,
        invalidate_health_cache,
        PerformanceMonitor,
        get_performance_monitor
    )
    from .async_tasks import (
        TaskManager,
        AsyncTask,
        TaskStatus,
        get_task_manager,
        async_task,
        process_health_data_batch,
        generate_health_report,
        sync_external_health_data,
        QueryOptimizer,
        ConnectionPool
    )

    PERFORMANCE_UTILS_AVAILABLE = True
except ImportError:
    PERFORMANCE_UTILS_AVAILABLE = False
