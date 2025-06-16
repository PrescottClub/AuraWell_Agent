"""
Comprehensive WebSocket Integration Testing for AuraWell Family-Agent

Tests WebSocket connections, heartbeat mechanisms, reconnection logic,
message handling, and real-time communication features.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

import websockets
from websockets.exceptions import ConnectionClosed, ConnectionClosedError

from src.aurawell.interfaces.websocket_interface import (
    WebSocketManager,
    WebSocketConnection,
    MessageType,
    WebSocketMessage,
    HeartbeatManager,
    ConnectionPool,
)
from src.aurawell.core.exceptions import AurawellException


class TestWebSocketConnection:
    """Test WebSocket connection management"""

    @pytest.fixture
    def mock_websocket(self):
        """Mock WebSocket connection"""
        websocket = AsyncMock()
        websocket.closed = False
        websocket.close_code = None
        return websocket

    @pytest.fixture
    def websocket_connection(self, mock_websocket):
        """Create WebSocketConnection instance"""
        return WebSocketConnection(
            websocket=mock_websocket,
            user_id="user123",
            family_id="family123",
            connection_id="conn123",
        )

    @pytest.mark.asyncio
    async def test_websocket_connection_initialization(
        self, websocket_connection, mock_websocket
    ):
        """Test WebSocket connection initialization"""
        assert websocket_connection.user_id == "user123"
        assert websocket_connection.family_id == "family123"
        assert websocket_connection.connection_id == "conn123"
        assert websocket_connection.is_active is True
        assert websocket_connection.last_heartbeat is not None

    @pytest.mark.asyncio
    async def test_send_message_success(self, websocket_connection, mock_websocket):
        """Test successful message sending"""
        message = WebSocketMessage(
            type=MessageType.HEALTH_UPDATE,
            data={"steps": 5000, "calories": 200},
            timestamp=datetime.now(timezone.utc),
        )

        await websocket_connection.send_message(message)

        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])
        assert sent_data["type"] == "health_update"
        assert sent_data["data"]["steps"] == 5000

    @pytest.mark.asyncio
    async def test_send_message_connection_closed(
        self, websocket_connection, mock_websocket
    ):
        """Test message sending when connection is closed"""
        mock_websocket.send.side_effect = ConnectionClosed(None, None)

        message = WebSocketMessage(
            type=MessageType.HEALTH_UPDATE,
            data={"steps": 5000},
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(ConnectionClosed):
            await websocket_connection.send_message(message)

        assert websocket_connection.is_active is False

    @pytest.mark.asyncio
    async def test_receive_message_success(self, websocket_connection, mock_websocket):
        """Test successful message receiving"""
        test_message = {
            "type": "heartbeat",
            "data": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        mock_websocket.recv.return_value = json.dumps(test_message)

        message = await websocket_connection.receive_message()

        assert message.type == MessageType.HEARTBEAT
        assert isinstance(message.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_receive_message_invalid_json(
        self, websocket_connection, mock_websocket
    ):
        """Test receiving invalid JSON message"""
        mock_websocket.recv.return_value = "invalid json"

        with pytest.raises(ValueError):
            await websocket_connection.receive_message()

    @pytest.mark.asyncio
    async def test_heartbeat_update(self, websocket_connection):
        """Test heartbeat timestamp update"""
        original_heartbeat = websocket_connection.last_heartbeat
        await asyncio.sleep(0.01)  # Small delay

        websocket_connection.update_heartbeat()

        assert websocket_connection.last_heartbeat > original_heartbeat

    @pytest.mark.asyncio
    async def test_connection_close(self, websocket_connection, mock_websocket):
        """Test connection closing"""
        await websocket_connection.close()

        mock_websocket.close.assert_called_once()
        assert websocket_connection.is_active is False


class TestHeartbeatManager:
    """Test heartbeat management functionality"""

    @pytest.fixture
    def heartbeat_manager(self):
        """Create HeartbeatManager instance"""
        return HeartbeatManager(heartbeat_interval=1.0, timeout_threshold=5.0)

    @pytest.fixture
    def mock_connection_pool(self):
        """Mock connection pool"""
        pool = AsyncMock(spec=ConnectionPool)
        pool.get_all_connections.return_value = []
        return pool

    @pytest.mark.asyncio
    async def test_heartbeat_manager_start_stop(
        self, heartbeat_manager, mock_connection_pool
    ):
        """Test heartbeat manager start and stop"""
        heartbeat_manager.connection_pool = mock_connection_pool

        # Start heartbeat manager
        await heartbeat_manager.start()
        assert heartbeat_manager.is_running is True

        # Stop heartbeat manager
        await heartbeat_manager.stop()
        assert heartbeat_manager.is_running is False

    @pytest.mark.asyncio
    async def test_heartbeat_detection_active_connection(self, heartbeat_manager):
        """Test heartbeat detection for active connection"""
        mock_connection = AsyncMock(spec=WebSocketConnection)
        mock_connection.last_heartbeat = datetime.now(timezone.utc)
        mock_connection.is_active = True

        is_alive = heartbeat_manager.is_connection_alive(mock_connection)
        assert is_alive is True

    @pytest.mark.asyncio
    async def test_heartbeat_detection_stale_connection(self, heartbeat_manager):
        """Test heartbeat detection for stale connection"""
        mock_connection = AsyncMock(spec=WebSocketConnection)
        # Set heartbeat to 10 seconds ago (beyond threshold)
        mock_connection.last_heartbeat = datetime.now(timezone.utc) - timedelta(
            seconds=10
        )
        mock_connection.is_active = True

        is_alive = heartbeat_manager.is_connection_alive(mock_connection)
        assert is_alive is False

    @pytest.mark.asyncio
    async def test_cleanup_stale_connections(
        self, heartbeat_manager, mock_connection_pool
    ):
        """Test cleanup of stale connections"""
        # Create mock connections - one active, one stale
        active_connection = AsyncMock(spec=WebSocketConnection)
        active_connection.last_heartbeat = datetime.now(timezone.utc)
        active_connection.is_active = True
        active_connection.connection_id = "active123"

        stale_connection = AsyncMock(spec=WebSocketConnection)
        stale_connection.last_heartbeat = datetime.now(timezone.utc) - timedelta(
            seconds=10
        )
        stale_connection.is_active = True
        stale_connection.connection_id = "stale123"

        mock_connection_pool.get_all_connections.return_value = [
            active_connection,
            stale_connection,
        ]
        heartbeat_manager.connection_pool = mock_connection_pool

        await heartbeat_manager.cleanup_stale_connections()

        # Verify stale connection was closed
        stale_connection.close.assert_called_once()
        mock_connection_pool.remove_connection.assert_called_once_with("stale123")

    @pytest.mark.asyncio
    async def test_send_heartbeat_ping(self, heartbeat_manager, mock_connection_pool):
        """Test sending heartbeat ping to all connections"""
        mock_connection = AsyncMock(spec=WebSocketConnection)
        mock_connection.is_active = True
        mock_connection_pool.get_all_connections.return_value = [mock_connection]
        heartbeat_manager.connection_pool = mock_connection_pool

        await heartbeat_manager.send_heartbeat_ping()

        mock_connection.send_message.assert_called_once()
        sent_message = mock_connection.send_message.call_args[0][0]
        assert sent_message.type == MessageType.HEARTBEAT


class TestConnectionPool:
    """Test connection pool management"""

    @pytest.fixture
    def connection_pool(self):
        """Create ConnectionPool instance"""
        return ConnectionPool()

    @pytest.fixture
    def mock_connection(self):
        """Mock WebSocket connection"""
        connection = AsyncMock(spec=WebSocketConnection)
        connection.connection_id = "conn123"
        connection.user_id = "user123"
        connection.family_id = "family123"
        connection.is_active = True
        return connection

    def test_add_connection(self, connection_pool, mock_connection):
        """Test adding connection to pool"""
        connection_pool.add_connection(mock_connection)

        assert "conn123" in connection_pool.connections
        assert connection_pool.get_connection("conn123") == mock_connection

    def test_remove_connection(self, connection_pool, mock_connection):
        """Test removing connection from pool"""
        connection_pool.add_connection(mock_connection)
        connection_pool.remove_connection("conn123")

        assert "conn123" not in connection_pool.connections
        assert connection_pool.get_connection("conn123") is None

    def test_get_connections_by_user(self, connection_pool):
        """Test getting connections by user ID"""
        # Add multiple connections for same user
        conn1 = AsyncMock(spec=WebSocketConnection)
        conn1.connection_id = "conn1"
        conn1.user_id = "user123"
        conn1.family_id = "family123"

        conn2 = AsyncMock(spec=WebSocketConnection)
        conn2.connection_id = "conn2"
        conn2.user_id = "user123"
        conn2.family_id = "family456"

        connection_pool.add_connection(conn1)
        connection_pool.add_connection(conn2)

        user_connections = connection_pool.get_connections_by_user("user123")
        assert len(user_connections) == 2
        assert conn1 in user_connections
        assert conn2 in user_connections

    def test_get_connections_by_family(self, connection_pool):
        """Test getting connections by family ID"""
        # Add multiple connections for same family
        conn1 = AsyncMock(spec=WebSocketConnection)
        conn1.connection_id = "conn1"
        conn1.user_id = "user123"
        conn1.family_id = "family123"

        conn2 = AsyncMock(spec=WebSocketConnection)
        conn2.connection_id = "conn2"
        conn2.user_id = "user456"
        conn2.family_id = "family123"

        connection_pool.add_connection(conn1)
        connection_pool.add_connection(conn2)

        family_connections = connection_pool.get_connections_by_family("family123")
        assert len(family_connections) == 2
        assert conn1 in family_connections
        assert conn2 in family_connections

    def test_get_all_connections(self, connection_pool, mock_connection):
        """Test getting all connections"""
        connection_pool.add_connection(mock_connection)

        all_connections = connection_pool.get_all_connections()
        assert len(all_connections) == 1
        assert mock_connection in all_connections

    def test_connection_count(self, connection_pool, mock_connection):
        """Test connection count tracking"""
        assert connection_pool.connection_count == 0

        connection_pool.add_connection(mock_connection)
        assert connection_pool.connection_count == 1

        connection_pool.remove_connection("conn123")
        assert connection_pool.connection_count == 0


class TestWebSocketManager:
    """Test WebSocket manager functionality"""

    @pytest.fixture
    def websocket_manager(self):
        """Create WebSocketManager instance"""
        return WebSocketManager()

    @pytest.mark.asyncio
    async def test_handle_new_connection(self, websocket_manager):
        """Test handling new WebSocket connection"""
        mock_websocket = AsyncMock()
        mock_websocket.closed = False

        with patch.object(websocket_manager, "_authenticate_connection") as mock_auth:
            mock_auth.return_value = ("user123", "family123")

            connection = await websocket_manager.handle_new_connection(mock_websocket)

            assert connection.user_id == "user123"
            assert connection.family_id == "family123"
            assert (
                connection.connection_id
                in websocket_manager.connection_pool.connections
            )

    @pytest.mark.asyncio
    async def test_broadcast_to_family(self, websocket_manager):
        """Test broadcasting message to family members"""
        # Add mock connections for family
        conn1 = AsyncMock(spec=WebSocketConnection)
        conn1.family_id = "family123"
        conn1.is_active = True

        conn2 = AsyncMock(spec=WebSocketConnection)
        conn2.family_id = "family123"
        conn2.is_active = True

        websocket_manager.connection_pool.add_connection(conn1)
        websocket_manager.connection_pool.add_connection(conn2)

        message = WebSocketMessage(
            type=MessageType.FAMILY_UPDATE,
            data={"event": "member_joined"},
            timestamp=datetime.now(timezone.utc),
        )

        await websocket_manager.broadcast_to_family("family123", message)

        conn1.send_message.assert_called_once_with(message)
        conn2.send_message.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_to_user(self, websocket_manager):
        """Test sending message to specific user"""
        mock_connection = AsyncMock(spec=WebSocketConnection)
        mock_connection.user_id = "user123"
        mock_connection.is_active = True

        websocket_manager.connection_pool.add_connection(mock_connection)

        message = WebSocketMessage(
            type=MessageType.NOTIFICATION,
            data={"text": "Hello user!"},
            timestamp=datetime.now(timezone.utc),
        )

        await websocket_manager.send_to_user("user123", message)

        mock_connection.send_message.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_disconnect(self, websocket_manager):
        """Test connection cleanup when client disconnects"""
        mock_connection = AsyncMock(spec=WebSocketConnection)
        mock_connection.connection_id = "conn123"
        mock_connection.is_active = False

        websocket_manager.connection_pool.add_connection(mock_connection)

        await websocket_manager.cleanup_connection("conn123")

        assert websocket_manager.connection_pool.get_connection("conn123") is None


class TestWebSocketReconnection:
    """Test WebSocket reconnection logic"""

    @pytest.mark.asyncio
    async def test_automatic_reconnection_on_connection_loss(self):
        """Test automatic reconnection when connection is lost"""
        reconnect_attempts = 0
        max_attempts = 3

        async def mock_connect():
            nonlocal reconnect_attempts
            reconnect_attempts += 1
            if reconnect_attempts < max_attempts:
                raise ConnectionClosedError(None, None)
            return AsyncMock()  # Successful connection

        # Simulate reconnection logic
        connection = None
        for attempt in range(max_attempts):
            try:
                connection = await mock_connect()
                break
            except ConnectionClosedError:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.1)  # Brief delay before retry
                else:
                    raise

        assert connection is not None
        assert reconnect_attempts == max_attempts

    @pytest.mark.asyncio
    async def test_exponential_backoff_reconnection(self):
        """Test exponential backoff for reconnection attempts"""
        delays = []

        async def mock_reconnect_with_backoff(max_attempts=3):
            for attempt in range(max_attempts):
                delay = min(2**attempt, 30)  # Exponential backoff with max 30s
                delays.append(delay)
                await asyncio.sleep(0.001)  # Simulate delay (shortened for test)

                # Simulate success on last attempt
                if attempt == max_attempts - 1:
                    return True
            return False

        success = await mock_reconnect_with_backoff()

        assert success is True
        assert len(delays) == 3
        assert delays[0] == 1  # 2^0
        assert delays[1] == 2  # 2^1
        assert delays[2] == 4  # 2^2


@pytest.fixture
def sample_websocket_data():
    """Fixture providing sample WebSocket data for testing"""
    return {
        "user_id": "user123",
        "family_id": "family123",
        "connection_id": "conn123",
        "message_data": {
            "type": "health_update",
            "data": {"steps": 5000, "calories": 200},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
