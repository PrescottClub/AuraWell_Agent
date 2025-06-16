"""
Caching utilities for AuraWell API

Provides Redis-based caching for improved performance and response times.
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Union
from functools import wraps
import hashlib
from concurrent.futures import ThreadPoolExecutor

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based cache manager for AuraWell API"""

    def __init__(
        self, redis_url: str = "redis://localhost:6379/0", enabled: bool = True
    ):
        self.enabled = enabled and REDIS_AVAILABLE
        self.redis_client = None
        self.executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="redis_cache"
        )

        if self.enabled:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed, disabling cache: {e}")
                self.enabled = False
        else:
            logger.info("Cache disabled or Redis not available")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and parameters"""
        # Create a deterministic key from arguments
        key_data = {"args": args, "kwargs": sorted(kwargs.items())}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()[:8]
        return f"aurawell:{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None

        try:
            loop = asyncio.get_event_loop()
            value = await loop.run_in_executor(
                self.executor, self.redis_client.get, key
            )
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (seconds)"""
        if not self.enabled:
            return False

        try:
            serialized_value = json.dumps(value, default=str)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self.redis_client.setex, key, ttl, serialized_value
            )
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self.redis_client.delete, key
            )
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0

        try:
            loop = asyncio.get_event_loop()
            keys = await loop.run_in_executor(
                self.executor, self.redis_client.keys, pattern
            )
            if keys:
                result = await loop.run_in_executor(
                    self.executor, self.redis_client.delete, *keys
                )
                return result
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    def cleanup(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)

    def cache_key(self, prefix: str, ttl: int = 300):
        """Decorator for caching function results"""

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result

                # Execute function
                result = await func(*args, **kwargs)

                # Cache the result
                await self.set(cache_key, result, ttl)
                logger.debug(f"Cache miss for {func.__name__}, result cached")

                return result

            return wrapper

        return decorator


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Cache decorators for common use cases
def cache_user_data(ttl: int = 600):
    """Cache user-related data for 10 minutes"""
    return get_cache_manager().cache_key("user_data", ttl)


def cache_health_data(ttl: int = 300):
    """Cache health data for 5 minutes"""
    return get_cache_manager().cache_key("health_data", ttl)


def cache_ai_response(ttl: int = 1800):
    """Cache AI responses for 30 minutes"""
    return get_cache_manager().cache_key("ai_response", ttl)


def cache_achievements(ttl: int = 900):
    """Cache achievement data for 15 minutes"""
    return get_cache_manager().cache_key("achievements", ttl)


# Cache invalidation helpers
async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user"""
    cache = get_cache_manager()
    pattern = f"aurawell:user_data:*{user_id}*"
    cleared = await cache.clear_pattern(pattern)
    logger.info(f"Invalidated {cleared} cache entries for user {user_id}")


async def invalidate_health_cache(user_id: str):
    """Invalidate health data cache for a user"""
    cache = get_cache_manager()
    pattern = f"aurawell:health_data:*{user_id}*"
    cleared = await cache.clear_pattern(pattern)
    logger.info(f"Invalidated {cleared} health cache entries for user {user_id}")


# Performance monitoring
class PerformanceMonitor:
    """Monitor API performance metrics"""

    def __init__(self):
        self.request_times: Dict[str, list] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "errors": 0}

    def record_request_time(self, endpoint: str, duration: float):
        """Record request processing time"""
        if endpoint not in self.request_times:
            self.request_times[endpoint] = []

        self.request_times[endpoint].append(duration)

        # Keep only last 100 requests per endpoint
        if len(self.request_times[endpoint]) > 100:
            self.request_times[endpoint] = self.request_times[endpoint][-100:]

    def get_average_response_time(self, endpoint: str) -> float:
        """Get average response time for endpoint"""
        times = self.request_times.get(endpoint, [])
        return sum(times) / len(times) if times else 0.0

    def get_slow_endpoints(self, threshold: float = 0.5) -> Dict[str, float]:
        """Get endpoints with average response time above threshold"""
        slow_endpoints = {}
        for endpoint, times in self.request_times.items():
            avg_time = sum(times) / len(times) if times else 0.0
            if avg_time > threshold:
                slow_endpoints[endpoint] = avg_time
        return slow_endpoints

    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_stats["hits"] += 1

    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_stats["misses"] += 1

    def record_cache_error(self):
        """Record cache error"""
        self.cache_stats["errors"] += 1

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate percentage"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        return (self.cache_stats["hits"] / total * 100) if total > 0 else 0.0


# Global performance monitor
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
