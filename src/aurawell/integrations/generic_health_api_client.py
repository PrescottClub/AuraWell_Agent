"""
Generic Health API Client Template for AuraWell

This module provides a base template for integrating with health platform APIs.
It includes OAuth 2.0 authentication, basic HTTP operations, error handling,
and rate limiting logic.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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


class GenericHealthAPIClient(ABC):
    """
    Generic base class for health platform API clients

    Provides common functionality for OAuth authentication, HTTP requests,
    error handling, and rate limiting.
    """

    def __init__(
        self,
        base_url: str,
        credentials: APICredentials,
        rate_limit_info: Optional[RateLimitInfo] = None,
    ):
        """
        Initialize the generic health API client

        Args:
            base_url: Base URL for the API
            credentials: API credentials including client ID, secret, etc.
            rate_limit_info: Rate limiting configuration
        """
        self.base_url = base_url.rstrip("/")
        self.credentials = credentials
        self.rate_limit = rate_limit_info or RateLimitInfo()

        # Configure requests session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(f"Initialized {self.__class__.__name__} for {base_url}")

    def _check_rate_limit(self) -> None:
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
            "User-Agent": "AuraWell/1.0",
        }

        if self.credentials.access_token:
            headers["Authorization"] = f"Bearer {self.credentials.access_token}"
        elif self.credentials.api_key:
            headers["X-API-Key"] = self.credentials.api_key

        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and extract data

        Args:
            response: HTTP response object

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
            error_message = response_data.get("error", "Unknown API error")
            raise HealthAPIError(
                f"API error: {error_message}",
                status_code=response.status_code,
                response_data=response_data,
            )

        return response_data

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API endpoint

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: URL parameters
            data: Request body data
            headers: Additional headers

        Returns:
            API response data

        Raises:
            HealthAPIError: For various API errors
        """
        # Check rate limiting
        self._check_rate_limit()

        # Prepare URL and headers
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_auth_headers()
        if headers:
            request_headers.update(headers)

        # Log the request
        logger.info(f"Making {method} request to {url}")
        logger.debug(f"Headers: {request_headers}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Data: {data}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=30,
            )

            return self._handle_response(response)

        except requests.exceptions.Timeout:
            raise HealthAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise HealthAPIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise HealthAPIError(f"Request failed: {str(e)}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request"""
        return self._make_request("GET", endpoint, params=params)

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request"""
        return self._make_request("POST", endpoint, data=data)

    def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PUT request"""
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._make_request("DELETE", endpoint)

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Perform authentication with the health platform

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token

        Returns:
            True if refresh successful, False otherwise
        """
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile information

        Args:
            user_id: User identifier

        Returns:
            User profile data
        """
        pass

    @abstractmethod
    def get_activity_data(
        self,
        user_id: str,
        start_date: str,
        end_date: str,
        data_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get user activity data for a date range

        Args:
            user_id: User identifier
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            data_types: Optional list of specific data types to retrieve

        Returns:
            Activity data
        """
        pass

    def is_token_valid(self) -> bool:
        """
        Check if current access token is valid and not expired

        Returns:
            True if token is valid, False otherwise
        """
        if not self.credentials.access_token:
            return False

        if self.credentials.token_expires_at:
            return datetime.now() < self.credentials.token_expires_at

        return True

    def ensure_authenticated(self) -> bool:
        """
        Ensure the client is authenticated, refresh token if needed

        Returns:
            True if authenticated, False otherwise
        """
        if self.is_token_valid():
            return True

        if self.credentials.refresh_token:
            logger.info("Access token expired, attempting to refresh")
            if self.refresh_access_token():
                return True

        logger.info("No valid token, attempting fresh authentication")
        return self.authenticate()


def load_credentials_from_env(platform_name: str) -> APICredentials:
    """
    Load API credentials from environment variables

    Args:
        platform_name: Name of the platform (e.g., 'XIAOMI', 'APPLE', 'BOHE')

    Returns:
        APICredentials object
    """
    prefix = platform_name.upper()

    return APICredentials(
        client_id=os.getenv(f"{prefix}_HEALTH_CLIENT_ID", ""),
        client_secret=os.getenv(f"{prefix}_HEALTH_CLIENT_SECRET", ""),
        api_key=os.getenv(f"{prefix}_HEALTH_API_KEY"),
        access_token=os.getenv(f"{prefix}_HEALTH_ACCESS_TOKEN"),
        refresh_token=os.getenv(f"{prefix}_HEALTH_REFRESH_TOKEN"),
    )
