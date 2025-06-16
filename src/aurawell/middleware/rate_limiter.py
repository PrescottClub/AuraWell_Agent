"""
Rate Limiting and Request Logging Middleware for AuraWell API

Provides rate limiting based on user_id and family_id, and comprehensive request logging.
"""

import time
import logging
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.exceptions import RateLimitError

logger = logging.getLogger(__name__)
request_logger = logging.getLogger("aurawell.requests")


class RateLimiter:
    """Simple in-memory rate limiter with sliding window"""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps for each key
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())

    def is_allowed(self, key: str) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed for the given key

        Args:
            key: Rate limiting key (e.g., user_id, family_id)

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests outside the window
        request_times = self.requests[key]
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        # Check if we're under the limit
        if len(request_times) < self.max_requests:
            request_times.append(now)
            return True, None

        # Calculate retry after time
        oldest_request = request_times[0]
        retry_after = int(oldest_request + self.window_seconds - now) + 1

        return False, retry_after

    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for the key"""
        now = time.time()
        window_start = now - self.window_seconds

        request_times = self.requests[key]
        # Clean old requests
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        return max(0, self.max_requests - len(request_times))


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting and request logging middleware"""

    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter(
            max_requests=10, window_seconds=60
        )

        # Paths that should be rate limited
        self.rate_limited_paths = [
            "/api/v1/families",
            "/api/v1/health",
            "/api/v1/dashboard",
            "/api/v1/reports",
            "/ws",
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting and logging"""
        start_time = time.time()

        # Extract user and family information
        user_id = self._extract_user_id(request)
        family_id = self._extract_family_id(request)

        # Check if path should be rate limited
        should_rate_limit = any(
            request.url.path.startswith(path) for path in self.rate_limited_paths
        )

        if should_rate_limit and user_id:
            # Apply rate limiting
            rate_limit_key = f"user:{user_id}"
            if family_id:
                rate_limit_key = f"family:{family_id}:user:{user_id}"

            is_allowed, retry_after = self.rate_limiter.is_allowed(rate_limit_key)

            if not is_allowed:
                # Log rate limit violation
                await self._log_request(
                    request,
                    None,
                    user_id,
                    family_id,
                    start_time,
                    status_code=429,
                    error="Rate limit exceeded",
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "error_code": "RATE_LIMIT_ERROR",
                        "message": f"请求过于频繁，请{retry_after}秒后重试",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )

        # Process the request
        try:
            response = await call_next(request)

            # Log successful request
            await self._log_request(
                request,
                response,
                user_id,
                family_id,
                start_time,
                status_code=response.status_code,
            )

            # Add rate limit headers
            if should_rate_limit and user_id:
                rate_limit_key = f"user:{user_id}"
                if family_id:
                    rate_limit_key = f"family:{family_id}:user:{user_id}"

                remaining = self.rate_limiter.get_remaining_requests(rate_limit_key)
                response.headers["X-RateLimit-Limit"] = str(
                    self.rate_limiter.max_requests
                )
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(
                    int(time.time() + self.rate_limiter.window_seconds)
                )

            return response

        except Exception as e:
            # Log error
            await self._log_request(
                request,
                None,
                user_id,
                family_id,
                start_time,
                status_code=500,
                error=str(e),
            )
            raise

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user_id from request"""
        # Try to get from headers first
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return user_id

        # Try to get from query parameters
        user_id = request.query_params.get("user_id")
        if user_id:
            return user_id

        # Try to get from path parameters
        if hasattr(request, "path_params"):
            user_id = request.path_params.get("user_id")
            if user_id:
                return user_id

        return None

    def _extract_family_id(self, request: Request) -> Optional[str]:
        """Extract family_id from request"""
        # Try to get from headers first
        family_id = request.headers.get("X-Family-ID")
        if family_id:
            return family_id

        # Try to get from query parameters
        family_id = request.query_params.get("family_id")
        if family_id:
            return family_id

        # Try to get from path parameters
        if hasattr(request, "path_params"):
            family_id = request.path_params.get("family_id")
            if family_id:
                return family_id

        return None

    async def _log_request(
        self,
        request: Request,
        response: Optional[Response],
        user_id: Optional[str],
        family_id: Optional[str],
        start_time: float,
        status_code: int,
        error: Optional[str] = None,
    ):
        """Log request details"""
        end_time = time.time()
        latency_ms = round((end_time - start_time) * 1000, 2)

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "user_id": user_id,
            "family_id": family_id,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "user_agent": request.headers.get("User-Agent"),
            "ip_address": request.client.host if request.client else None,
            "error": error,
        }

        # Log to request logger
        request_logger.info(json.dumps(log_entry, ensure_ascii=False))

        # Also log to main logger for monitoring
        if status_code >= 400:
            logger.warning(
                f"Request failed: {request.method} {request.url.path} - {status_code} ({latency_ms}ms)"
            )
        elif latency_ms > 2000:  # Log slow requests
            logger.warning(
                f"Slow request: {request.method} {request.url.path} - {latency_ms}ms"
            )
        else:
            logger.debug(
                f"Request: {request.method} {request.url.path} - {status_code} ({latency_ms}ms)"
            )
