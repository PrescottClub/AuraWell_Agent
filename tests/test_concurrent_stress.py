"""
Comprehensive Concurrent Stress Testing for AuraWell Family-Agent

Tests system behavior under high concurrent load, stress conditions,
performance benchmarks, and resource utilization limits.
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from unittest.mock import AsyncMock, patch
import concurrent.futures
import threading

from src.aurawell.services.family_service import FamilyService
from src.aurawell.services.dashboard_service import FamilyDashboardService
from src.aurawell.interfaces.websocket_interface import WebSocketManager
from src.aurawell.models.family_models import (
    FamilyRole,
    FamilyCreateRequest,
    InviteMemberRequest,
    FamilyInfo,
)
from src.aurawell.core.exceptions import AurawellException


class TestConcurrentLoad:
    """Test system behavior under concurrent load"""

    @pytest.fixture
    def load_test_config(self):
        """Configuration for load testing"""
        return {
            "concurrent_users": 50,
            "requests_per_user": 10,
            "max_response_time_ms": 2000,
            "success_rate_threshold": 0.95,
            "memory_limit_mb": 512,
        }

    @pytest.fixture
    def mock_services(self):
        """Mock services for load testing"""
        mock_db = AsyncMock()
        mock_session = AsyncMock()
        mock_db.get_session.return_value.__aenter__.return_value = mock_session

        family_service = FamilyService(database_manager=mock_db)
        dashboard_service = FamilyDashboardService(database_manager=mock_db)
        websocket_manager = WebSocketManager()

        return {
            "family_service": family_service,
            "dashboard_service": dashboard_service,
            "websocket_manager": websocket_manager,
            "database": mock_db,
            "session": mock_session,
        }

    @pytest.mark.asyncio
    async def test_concurrent_family_creation_load(
        self, load_test_config, mock_services
    ):
        """Test concurrent family creation under load"""
        family_service = mock_services["family_service"]

        # Performance metrics
        response_times = []
        success_count = 0
        error_count = 0

        async def create_family_load_test(user_index: int):
            nonlocal success_count, error_count

            start_time = time.time()

            try:
                with patch(
                    "aurawell.services.family_service.FamilyRepository"
                ) as mock_repo, patch(
                    "aurawell.services.family_service.UserRepository"
                ) as mock_user_repo:

                    # Mock successful responses
                    mock_user_repo.return_value.get_user_by_id.return_value = {
                        "user_id": f"user_{user_index}",
                        "username": f"user{user_index}",
                    }
                    mock_repo.return_value.get_families_by_user.return_value = []
                    mock_repo.return_value.create_family.return_value = None
                    mock_repo.return_value.add_family_member.return_value = None
                    mock_repo.return_value.log_family_activity.return_value = None

                    request = FamilyCreateRequest(name=f"Load Test Family {user_index}")
                    result = await family_service.create_family(
                        f"user_{user_index}", request
                    )

                    success_count += 1
                    return result

            except Exception as e:
                error_count += 1
                return e
            finally:
                end_time = time.time()
                response_times.append((end_time - start_time) * 1000)  # Convert to ms

        # Generate concurrent load
        tasks = [
            create_family_load_test(i)
            for i in range(load_test_config["concurrent_users"])
        ]

        # Execute load test
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Analyze results
        total_requests = len(tasks)
        success_rate = success_count / total_requests
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[
            18
        ]  # 95th percentile
        total_duration = end_time - start_time
        throughput = total_requests / total_duration

        # Performance assertions
        assert (
            success_rate >= load_test_config["success_rate_threshold"]
        ), f"Success rate {success_rate:.2%} below threshold {load_test_config['success_rate_threshold']:.2%}"

        assert (
            p95_response_time <= load_test_config["max_response_time_ms"]
        ), f"P95 response time {p95_response_time:.2f}ms exceeds limit {load_test_config['max_response_time_ms']}ms"

        # Log performance metrics
        print(f"\n=== Load Test Results ===")
        print(f"Total Requests: {total_requests}")
        print(f"Success Rate: {success_rate:.2%}")
        print(f"Average Response Time: {avg_response_time:.2f}ms")
        print(f"P95 Response Time: {p95_response_time:.2f}ms")
        print(f"Throughput: {throughput:.2f} requests/second")
        print(f"Total Duration: {total_duration:.2f}s")

    @pytest.mark.asyncio
    async def test_concurrent_member_operations_stress(
        self, load_test_config, mock_services
    ):
        """Test concurrent member operations under stress"""
        family_service = mock_services["family_service"]

        # Stress test configuration
        family_id = "stress_test_family"
        owner_id = "stress_test_owner"

        response_times = []
        success_count = 0
        error_count = 0

        async def invite_member_stress_test(invite_index: int):
            nonlocal success_count, error_count

            start_time = time.time()

            try:
                with patch(
                    "aurawell.services.family_service.FamilyRepository"
                ) as mock_repo, patch(
                    "aurawell.services.family_service.UserRepository"
                ) as mock_user_repo:

                    # Mock responses
                    mock_repo.return_value.get_family_member.return_value = {
                        "user_id": owner_id,
                        "role": FamilyRole.OWNER,
                    }
                    mock_repo.return_value.get_family_by_id.return_value = {
                        "family_id": family_id,
                        "member_count": 1,
                    }
                    mock_user_repo.return_value.get_user_by_email.return_value = {
                        "user_id": f"invitee_{invite_index}"
                    }
                    mock_repo.return_value.get_pending_invite.return_value = None
                    mock_repo.return_value.create_invite.return_value = None
                    mock_repo.return_value.log_family_activity.return_value = None

                    request = InviteMemberRequest(
                        email=f"stress_test_{invite_index}@example.com"
                    )
                    result = await family_service.invite_member(
                        family_id, owner_id, request
                    )

                    success_count += 1
                    return result

            except Exception as e:
                error_count += 1
                return e
            finally:
                end_time = time.time()
                response_times.append((end_time - start_time) * 1000)

        # Generate stress load
        stress_requests = load_test_config["concurrent_users"] * 2  # Double the load
        tasks = [invite_member_stress_test(i) for i in range(stress_requests)]

        # Execute stress test
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze stress test results
        success_rate = success_count / stress_requests
        avg_response_time = statistics.mean(response_times) if response_times else 0

        # Stress test should maintain reasonable performance
        assert (
            success_rate >= 0.90
        ), f"Stress test success rate {success_rate:.2%} too low"
        assert (
            avg_response_time <= load_test_config["max_response_time_ms"] * 1.5
        ), f"Stress test response time {avg_response_time:.2f}ms too high"

    @pytest.mark.asyncio
    async def test_websocket_concurrent_connections(
        self, load_test_config, mock_services
    ):
        """Test WebSocket manager under concurrent connection load"""
        websocket_manager = mock_services["websocket_manager"]

        connection_times = []
        active_connections = []

        async def create_websocket_connection(conn_index: int):
            start_time = time.time()

            try:
                # Mock WebSocket connection
                mock_websocket = AsyncMock()
                mock_websocket.closed = False

                with patch.object(
                    websocket_manager, "_authenticate_connection"
                ) as mock_auth:
                    mock_auth.return_value = (
                        f"user_{conn_index}",
                        f"family_{conn_index % 10}",
                    )

                    connection = await websocket_manager.handle_new_connection(
                        mock_websocket
                    )
                    active_connections.append(connection)

                    end_time = time.time()
                    connection_times.append((end_time - start_time) * 1000)

                    return connection

            except Exception as e:
                return e

        # Create concurrent WebSocket connections
        connection_tasks = [
            create_websocket_connection(i)
            for i in range(load_test_config["concurrent_users"])
        ]

        connections = await asyncio.gather(*connection_tasks, return_exceptions=True)

        # Verify connection performance
        successful_connections = [
            c for c in connections if not isinstance(c, Exception)
        ]
        success_rate = len(successful_connections) / len(connection_tasks)
        avg_connection_time = (
            statistics.mean(connection_times) if connection_times else 0
        )

        assert (
            success_rate >= 0.95
        ), f"WebSocket connection success rate {success_rate:.2%} too low"
        assert (
            avg_connection_time <= 100
        ), f"WebSocket connection time {avg_connection_time:.2f}ms too high"

        # Test concurrent message broadcasting
        if successful_connections:
            broadcast_start = time.time()

            # Mock message broadcasting to all connections
            with patch.object(
                websocket_manager.connection_pool, "get_connections_by_family"
            ) as mock_get_conns:
                mock_get_conns.return_value = successful_connections[
                    :10
                ]  # Limit for test

                from aurawell.interfaces.websocket_interface import (
                    WebSocketMessage,
                    MessageType,
                )

                message = WebSocketMessage(
                    type=MessageType.FAMILY_UPDATE,
                    data={"event": "stress_test"},
                    timestamp=datetime.now(timezone.utc),
                )

                await websocket_manager.broadcast_to_family("family_0", message)

            broadcast_end = time.time()
            broadcast_time = (broadcast_end - broadcast_start) * 1000

            assert (
                broadcast_time <= 500
            ), f"Broadcast time {broadcast_time:.2f}ms too high"


class TestMemoryAndResourceUsage:
    """Test memory usage and resource consumption under load"""

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, load_test_config):
        """Test memory usage doesn't exceed limits under load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create memory-intensive operations
        large_data_sets = []

        async def memory_intensive_operation(index: int):
            # Simulate data processing
            data = {
                f"user_{i}": {
                    "family_data": [f"data_{j}" for j in range(100)],
                    "health_metrics": list(range(1000)),
                    "activity_log": [
                        {"timestamp": time.time(), "action": f"action_{k}"}
                        for k in range(50)
                    ],
                }
                for i in range(10)
            }
            large_data_sets.append(data)

            # Simulate processing delay
            await asyncio.sleep(0.01)

            return len(data)

        # Execute memory-intensive operations
        tasks = [
            memory_intensive_operation(i)
            for i in range(load_test_config["concurrent_users"])
        ]

        await asyncio.gather(*tasks)

        # Check memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        assert (
            memory_increase <= load_test_config["memory_limit_mb"]
        ), f"Memory usage increased by {memory_increase:.2f}MB, exceeding limit {load_test_config['memory_limit_mb']}MB"

        # Cleanup
        large_data_sets.clear()

    @pytest.mark.asyncio
    async def test_connection_pool_resource_management(
        self, load_test_config, mock_services
    ):
        """Test connection pool resource management under load"""
        websocket_manager = mock_services["websocket_manager"]

        # Create many connections
        connections = []
        for i in range(load_test_config["concurrent_users"] * 2):
            mock_websocket = AsyncMock()
            mock_websocket.closed = False

            with patch.object(
                websocket_manager, "_authenticate_connection"
            ) as mock_auth:
                mock_auth.return_value = (f"user_{i}", f"family_{i % 5}")

                connection = await websocket_manager.handle_new_connection(
                    mock_websocket
                )
                connections.append(connection)

        # Verify connection pool size
        pool_size = websocket_manager.connection_pool.connection_count
        assert pool_size == len(connections)

        # Test cleanup of inactive connections
        # Mark half as inactive
        for i in range(0, len(connections), 2):
            connections[i].is_active = False

        # Trigger cleanup
        await websocket_manager.cleanup_inactive_connections()

        # Verify cleanup reduced pool size
        new_pool_size = websocket_manager.connection_pool.connection_count
        assert new_pool_size < pool_size


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    @pytest.mark.asyncio
    async def test_family_service_performance_benchmark(self, mock_services):
        """Benchmark family service operations"""
        family_service = mock_services["family_service"]

        # Benchmark configuration
        benchmark_iterations = 100
        operations = ["create_family", "invite_member", "update_role"]

        benchmark_results = {}

        for operation in operations:
            times = []

            for i in range(benchmark_iterations):
                start_time = time.time()

                try:
                    if operation == "create_family":
                        with patch(
                            "aurawell.services.family_service.FamilyRepository"
                        ) as mock_repo, patch(
                            "aurawell.services.family_service.UserRepository"
                        ) as mock_user_repo:

                            mock_user_repo.return_value.get_user_by_id.return_value = {
                                "user_id": f"user_{i}",
                                "username": f"user{i}",
                            }
                            mock_repo.return_value.get_families_by_user.return_value = (
                                []
                            )

                            request = FamilyCreateRequest(name=f"Benchmark Family {i}")
                            await family_service.create_family(f"user_{i}", request)

                    elif operation == "invite_member":
                        with patch(
                            "aurawell.services.family_service.FamilyRepository"
                        ) as mock_repo, patch(
                            "aurawell.services.family_service.UserRepository"
                        ) as mock_user_repo:

                            mock_repo.return_value.get_family_member.return_value = {
                                "user_id": "owner",
                                "role": FamilyRole.OWNER,
                            }
                            mock_repo.return_value.get_family_by_id.return_value = {
                                "family_id": "family",
                                "member_count": 1,
                            }
                            mock_user_repo.return_value.get_user_by_email.return_value = {
                                "user_id": f"invitee_{i}"
                            }
                            mock_repo.return_value.get_pending_invite.return_value = (
                                None
                            )

                            request = InviteMemberRequest(
                                email=f"benchmark_{i}@example.com"
                            )
                            await family_service.invite_member(
                                "family", "owner", request
                            )

                except Exception:
                    pass  # Ignore errors for benchmark

                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # Convert to ms

            # Calculate benchmark statistics
            benchmark_results[operation] = {
                "avg_time_ms": statistics.mean(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "p95_time_ms": (
                    statistics.quantiles(times, n=20)[18]
                    if len(times) >= 20
                    else max(times)
                ),
                "operations_per_second": 1000 / statistics.mean(times),
            }

        # Print benchmark results
        print(f"\n=== Performance Benchmark Results ===")
        for operation, metrics in benchmark_results.items():
            print(f"\n{operation.upper()}:")
            print(f"  Average: {metrics['avg_time_ms']:.2f}ms")
            print(f"  Min: {metrics['min_time_ms']:.2f}ms")
            print(f"  Max: {metrics['max_time_ms']:.2f}ms")
            print(f"  P95: {metrics['p95_time_ms']:.2f}ms")
            print(f"  Ops/sec: {metrics['operations_per_second']:.2f}")

        # Performance assertions
        for operation, metrics in benchmark_results.items():
            assert (
                metrics["avg_time_ms"] <= 100
            ), f"{operation} average time {metrics['avg_time_ms']:.2f}ms exceeds 100ms"
            assert (
                metrics["p95_time_ms"] <= 200
            ), f"{operation} P95 time {metrics['p95_time_ms']:.2f}ms exceeds 200ms"


@pytest.fixture
def stress_test_data():
    """Fixture providing data for stress testing"""
    return {
        "test_users": [f"stress_user_{i}" for i in range(100)],
        "test_families": [f"stress_family_{i}" for i in range(20)],
        "test_emails": [f"stress_test_{i}@example.com" for i in range(100)],
    }
