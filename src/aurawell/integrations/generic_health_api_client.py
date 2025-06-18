"""
Async Generic Health API Client for AuraWell

This module provides an asynchronous base template for integrating with health platform APIs.
It includes OAuth 2.0 authentication, async HTTP operations, error handling,
and rate limiting logic using httpx.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import httpx
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class APICredentials:
    """Data class for API credentials"""

    client_id: str
    client_secret: str
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


@dataclass
class RateLimitInfo:
    """Rate limiting information"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    last_request_time: float = 0
    current_minute_requests: int = 0
    current_hour_requests: int = 0


class HealthAPIError(Exception):
    """Base exception for health API errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class AuthenticationError(HealthAPIError):
    """Authentication related errors"""

    pass


class RateLimitError(HealthAPIError):
    """Rate limit exceeded errors"""

    pass


class AsyncGenericHealthAPIClient(ABC):
    """
    Async Generic base class for health platform API clients

    Provides common async functionality for OAuth authentication, HTTP requests,
    error handling, and rate limiting using httpx.
    """

    def __init__(
        self,
        base_url: str,
        credentials: APICredentials,
        rate_limit_info: Optional[RateLimitInfo] = None,
        timeout: float = 30.0,
        max_connections: int = 100,
    ):
        """
        Initialize the async generic health API client

        Args:
            base_url: Base URL for the API
            credentials: API credentials including client ID, secret, etc.
            rate_limit_info: Rate limiting configuration
            timeout: Request timeout in seconds
            max_connections: Maximum concurrent connections
        """
        self.base_url = base_url.rstrip("/")
        self.credentials = credentials
        self.rate_limit = rate_limit_info or RateLimitInfo()
        self.timeout = timeout

        # Configure httpx async client with connection pooling and retries
        self._client = None
        self._limits = httpx.Limits(
            max_keepalive_connections=max_connections,
            max_connections=max_connections * 2,
            keepalive_expiry=30.0
        )

        logger.info(f"Initialized {self.__class__.__name__} for {base_url}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure async client is initialized"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                limits=self._limits,
                follow_redirects=True,
                http2=True  # Enable HTTP/2 for better performance
            )
        return self._client

    async def close(self):
        """Close the async client and cleanup resources"""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.debug("Async HTTP client closed")

    async def _check_rate_limit(self) -> None:
        """
        Check and enforce rate limiting

        Raises:
            RateLimitError: If rate limit would be exceeded
        """
        current_time = time.time()

        # Reset counters if a minute/hour has passed
        if current_time - self.rate_limit.last_request_time > 60:
            self.rate_limit.current_minute_requests = 0
        if current_time - self.rate_limit.last_request_time > 3600:
            self.rate_limit.current_hour_requests = 0

        # Check limits
        if (
            self.rate_limit.current_minute_requests
            >= self.rate_limit.requests_per_minute
        ):
            raise RateLimitError("Rate limit exceeded: too many requests per minute")
        if self.rate_limit.current_hour_requests >= self.rate_limit.requests_per_hour:
            raise RateLimitError("Rate limit exceeded: too many requests per hour")

        # Update counters
        self.rate_limit.current_minute_requests += 1
        self.rate_limit.current_hour_requests += 1
        self.rate_limit.last_request_time = current_time

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests

        Returns:
            Dictionary of headers including authorization
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AuraWell/2.0",
        }

        if self.credentials.access_token:
            headers["Authorization"] = f"Bearer {self.credentials.access_token}"
        elif self.credentials.api_key:
            headers["X-API-Key"] = self.credentials.api_key

        return headers

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle API response and extract data

        Args:
            response: HTTPX response object

        Returns:
            Parsed response data

        Raises:
            HealthAPIError: For various API errors
        """
        try:
            response_data = response.json() if response.content else {}
        except json.JSONDecodeError:
            response_data = {"raw_content": response.text}

        # Log the response
        logger.debug(f"API Response: {response.status_code} - {response_data}")

        # Handle different status codes
        if response.status_code == 200:
            return response_data
        elif response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded",
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code >= 400:
            raise HealthAPIError(
                f"API error: {response.status_code}",
                status_code=response.status_code,
                response_data=response_data,
            )

        return response_data

    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with intelligent retry logic

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            max_retries: Maximum retry attempts

        Returns:
            Response data
        """
        client = await self._ensure_client()
        request_headers = self._get_auth_headers()
        if headers:
            request_headers.update(headers)

        url = f"{endpoint}" if endpoint.startswith('http') else f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(max_retries + 1):
            try:
                # Check rate limit before making request
                await self._check_rate_limit()

                # Make the async request
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=request_headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, headers=request_headers)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data, headers=request_headers)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=request_headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                return await self._handle_response(response)

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt == max_retries:
                    raise HealthAPIError(f"Request failed after {max_retries} retries: {str(e)}")

                # Exponential backoff
                wait_time = (2 ** attempt) * 0.5
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}")
                await asyncio.sleep(wait_time)

            except RateLimitError as e:
                if attempt == max_retries:
                    raise

                # Wait longer for rate limit errors
                wait_time = 60
                logger.warning(f"Rate limit hit (attempt {attempt + 1}), waiting {wait_time}s")
                await asyncio.sleep(wait_time)

    # ============================================
    # Public async HTTP methods
    # ============================================

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make async GET request"""
        return await self._make_request_with_retry("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make async POST request"""
        return await self._make_request_with_retry("POST", endpoint, data=data)

    async def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make async PUT request"""
        return await self._make_request_with_retry("PUT", endpoint, data=data)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make async DELETE request"""
        return await self._make_request_with_retry("DELETE", endpoint)

    # ============================================
    # Abstract methods (to be implemented by subclasses)
    # ============================================

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the health platform API

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    async def refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token

        Returns:
            True if token refresh successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile information

        Args:
            user_id: User identifier

        Returns:
            User profile data
        """
        pass

    @abstractmethod
    async def get_activity_data(
        self,
        user_id: str,
        start_date: str,
        end_date: str,
        data_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get user activity/health data for a date range

        Args:
            user_id: User identifier
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            data_types: List of data types to fetch (e.g., ['steps', 'heart_rate'])

        Returns:
            Activity data
        """
        pass

    # ============================================
    # Utility methods
    # ============================================

    def is_token_valid(self) -> bool:
        """
        Check if the current access token is valid and not expired

        Returns:
            True if token is valid, False otherwise
        """
        if not self.credentials.access_token:
            return False

        if self.credentials.token_expires_at:
            return datetime.now() < self.credentials.token_expires_at

        return True

    async def ensure_authenticated(self) -> bool:
        """
        Ensure the client is authenticated, refreshing token if needed

        Returns:
            True if authenticated, False otherwise
        """
        if self.is_token_valid():
            return True

        logger.info("Token expired or invalid, attempting to refresh...")

        if self.credentials.refresh_token:
            if await self.refresh_access_token():
                return True

        logger.info("Refresh failed, attempting full authentication...")
        return await self.authenticate()


# ============================================
# Utility function for loading credentials
# ============================================

def load_credentials_from_env(platform_name: str) -> APICredentials:
    """
    Load API credentials from environment variables

    Args:
        platform_name: Name of the platform (e.g., 'apple', 'xiaomi')

    Returns:
        APICredentials object
    """
    prefix = platform_name.upper()

    return APICredentials(
        client_id=os.getenv(f"{prefix}_CLIENT_ID", ""),
        client_secret=os.getenv(f"{prefix}_CLIENT_SECRET", ""),
        api_key=os.getenv(f"{prefix}_API_KEY"),
        access_token=os.getenv(f"{prefix}_ACCESS_TOKEN"),
        refresh_token=os.getenv(f"{prefix}_REFRESH_TOKEN"),
    )


# ============================================
# 向后兼容的同步包装器 (GenericHealthAPIClient)
# ============================================

class GenericHealthAPIClient:
    """
    向后兼容的同步包装器

    包装AsyncGenericHealthAPIClient，提供同步API接口
    为了向后兼容，保持类名不变
    """

    def __init__(self, base_url: str, credentials: APICredentials, **kwargs):
        # 创建异步客户端实例
        self._async_client = None
        self._init_params = {
            'base_url': base_url,
            'credentials': credentials,
            **kwargs
        }
        self._loop = None

    def _get_or_create_async_client(self):
        """获取或创建异步客户端"""
        if self._async_client is None:
            # 这里需要一个具体的异步客户端实现
            # 由于这是抽象基类，我们暂时返回None
            pass
        return self._async_client

    def _run_async(self, coro):
        """运行异步协程"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """同步GET请求"""
        client = self._get_or_create_async_client()
        if client:
            return self._run_async(client.get(endpoint, params))
        raise NotImplementedError("Sync wrapper requires concrete async client implementation")

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """同步POST请求"""
        client = self._get_or_create_async_client()
        if client:
            return self._run_async(client.post(endpoint, data))
        raise NotImplementedError("Sync wrapper requires concrete async client implementation")

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """同步PUT请求"""
        client = self._get_or_create_async_client()
        if client:
            return self._run_async(client.put(endpoint, data))
        raise NotImplementedError("Sync wrapper requires concrete async client implementation")

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """同步DELETE请求"""
        client = self._get_or_create_async_client()
        if client:
            return self._run_async(client.delete(endpoint))
        raise NotImplementedError("Sync wrapper requires concrete async client implementation")

    def authenticate(self) -> bool:
        """同步认证"""
        client = self._get_or_create_async_client()
        if client:
            return self._run_async(client.authenticate())
        raise NotImplementedError("Sync wrapper requires concrete async client implementation")

    def is_token_valid(self) -> bool:
        """检查令牌有效性"""
        client = self._get_or_create_async_client()
        if client:
            return client.is_token_valid()
        return False

    def __enter__(self):
        """同步上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """同步上下文管理器退出"""
        client = self._get_or_create_async_client()
        if client:
            self._run_async(client.close())


# 为了完全兼容，我们将AsyncGenericHealthAPIClient也设为主要的导出类
# 这样现有代码可以无缝迁移到异步版本
__all__ = [
    'AsyncGenericHealthAPIClient',
    'GenericHealthAPIClient',
    'APICredentials',
    'RateLimitInfo',
    'HealthAPIError',
    'AuthenticationError',
    'RateLimitError',
    'load_credentials_from_env'
]
