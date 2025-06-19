"""
WebSocket Interface for AuraWell Health Assistant

Provides real-time streaming chat interface for health consultations.
Features include connection management, message streaming, and user session handling.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field

from ..auth import authenticator, get_current_user_id
from ..models.api_models import (
    ChatRequest,
    EnhancedHealthChatRequest,
    HealthAdviceRequest,
    SwitchMemberRequest,
)
# ChatService已移除，使用agent_router替代
from ..langchain_agent.services.health_advice_service import HealthAdviceService
from ..services.family_service import FamilyService
from ..core.agent_router import agent_router
# RAG Service (v1.1 特种突击队)
from ..services.rag_service import get_rag_service

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket connection manager for handling multiple user connections with heartbeat and reconnection support"""

    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # Store user session data
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        # Store heartbeat tasks
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
        # Heartbeat configuration
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 10  # seconds

    async def connect(
        self, websocket: WebSocket, user_id: str, metadata: Dict[str, Any] = None
    ):
        """Accept a WebSocket connection and register user"""
        await websocket.accept()

        # Close existing connection if user is already connected
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].close()
                # Cancel existing heartbeat task
                if user_id in self.heartbeat_tasks:
                    self.heartbeat_tasks[user_id].cancel()
            except Exception as e:
                logger.warning(
                    f"Error closing existing connection for user {user_id}: {e}"
                )

        # Register new connection
        self.active_connections[user_id] = websocket
        self.connection_metadata[user_id] = metadata or {}
        self.user_sessions[user_id] = {
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "active_member_id": user_id,  # Default to self
            "conversation_id": None,
            "heartbeat_count": 0,
            "last_pong": datetime.now().isoformat(),
        }

        # Start heartbeat task
        self.heartbeat_tasks[user_id] = asyncio.create_task(
            self._heartbeat_task(user_id)
        )

        logger.info(f"WebSocket connection established for user: {user_id}")
        await self.send_personal_message(
            user_id,
            {
                "type": "connection_established",
                "status": "connected",
                "message": "欢迎使用AuraWell健康助手！",
                "timestamp": datetime.now().isoformat(),
                "heartbeat_interval": self.heartbeat_interval,
            },
        )

    def disconnect(self, user_id: str):
        """Disconnect and remove user from active connections"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.connection_metadata:
            del self.connection_metadata[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        if user_id in self.heartbeat_tasks:
            self.heartbeat_tasks[user_id].cancel()
            del self.heartbeat_tasks[user_id]

        logger.info(f"WebSocket connection closed for user: {user_id}")

    async def _heartbeat_task(self, user_id: str):
        """Background task to send periodic heartbeat pings"""
        try:
            while user_id in self.active_connections:
                await asyncio.sleep(self.heartbeat_interval)

                if user_id not in self.active_connections:
                    break

                # Send ping message
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat(),
                    "heartbeat_id": self.user_sessions[user_id]["heartbeat_count"],
                }

                try:
                    await self.send_personal_message(user_id, ping_message)
                    self.user_sessions[user_id]["heartbeat_count"] += 1

                    # Wait for pong response with timeout
                    await asyncio.wait_for(
                        self._wait_for_pong(user_id), timeout=self.heartbeat_timeout
                    )

                except asyncio.TimeoutError:
                    logger.warning(
                        f"Heartbeat timeout for user {user_id}, disconnecting"
                    )
                    await self._handle_heartbeat_timeout(user_id)
                    break
                except Exception as e:
                    logger.error(f"Heartbeat error for user {user_id}: {e}")
                    break

        except asyncio.CancelledError:
            logger.debug(f"Heartbeat task cancelled for user {user_id}")
        except Exception as e:
            logger.error(f"Heartbeat task error for user {user_id}: {e}")

    async def _wait_for_pong(self, user_id: str):
        """Wait for pong response from client"""
        initial_pong_time = self.user_sessions[user_id].get("last_pong")

        while True:
            await asyncio.sleep(0.1)  # Check every 100ms
            current_pong_time = self.user_sessions[user_id].get("last_pong")
            if current_pong_time != initial_pong_time:
                break

    async def _handle_heartbeat_timeout(self, user_id: str):
        """Handle heartbeat timeout by closing connection"""
        try:
            if user_id in self.active_connections:
                await self.active_connections[user_id].close(
                    code=1001, reason="Heartbeat timeout"
                )
            self.disconnect(user_id)
        except Exception as e:
            logger.error(f"Error handling heartbeat timeout for user {user_id}: {e}")

    async def handle_pong(self, user_id: str):
        """Handle pong response from client"""
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["last_pong"] = datetime.now().isoformat()
            self.user_sessions[user_id]["last_activity"] = datetime.now().isoformat()

    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(
                    json.dumps(message, ensure_ascii=False)
                )
                self.user_sessions[user_id][
                    "last_activity"
                ] = datetime.now().isoformat()
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                # Remove disconnected user
                self.disconnect(user_id)

    async def send_streaming_message(
        self, user_id: str, delta: str, status: str = "streaming"
    ):
        """Send streaming message chunk to user"""
        message = {
            "type": "chat_stream",
            "status": status,
            "delta": delta,
            "timestamp": datetime.now().isoformat(),
        }
        await self.send_personal_message(user_id, message)

    async def send_status_update(
        self, user_id: str, status: str, message: str = "", data: Dict = None
    ):
        """Send status update to user"""
        update = {
            "type": "status_update",
            "status": status,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
        }
        await self.send_personal_message(user_id, update)

    async def broadcast_to_family(
        self, family_id: str, message: Dict[str, Any], exclude_user: str = None
    ):
        """Broadcast message to all family members"""
        # Note: Would need family service integration to get family members
        # For now, this is a placeholder for future family features
        logger.info(f"Broadcasting to family {family_id}: {message}")

    def get_connected_users(self) -> List[str]:
        """Get list of connected user IDs"""
        return list(self.active_connections.keys())

    def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get user session data"""
        return self.user_sessions.get(user_id, {})

    def update_user_session(self, user_id: str, updates: Dict[str, Any]):
        """Update user session data"""
        if user_id in self.user_sessions:
            self.user_sessions[user_id].update(updates)
            self.user_sessions[user_id]["last_activity"] = datetime.now().isoformat()


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# WebSocket router
websocket_router = APIRouter()


class WebSocketMessage(BaseModel):
    """WebSocket message model"""

    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    active_member_id: Optional[str] = Field(
        None, description="Active member ID for family context"
    )


async def get_user_from_websocket(websocket: WebSocket, token: str) -> str:
    """Extract user ID from WebSocket connection token"""
    try:
        payload = authenticator.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@websocket_router.websocket("/ws/chat/{user_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket, user_id: str, token: str = None
):
    """
    WebSocket endpoint for real-time chat

    Query parameters:
    - token: JWT authentication token (REQUIRED in production)
    """
    try:
        # 🔒 强化认证：生产环境必须要求token
        from ..config.settings import get_settings
        settings = get_settings()

        if not token:
            # 检查是否为生产环境
            if settings.ENVIRONMENT == "production":
                logger.error(f"Production environment requires token for WebSocket connection: {user_id}")
                await websocket.close(code=4001, reason="Authentication required in production")
                return
            else:
                # 开发环境警告但允许连接
                logger.warning(f"⚠️ Development: WebSocket connection without token for user: {user_id}")

        # 验证token（如果提供）
        authenticated_user_id = None
        if token:
            try:
                authenticated_user_id = await get_user_from_websocket(websocket, token)
                if authenticated_user_id != user_id:
                    logger.error(f"User ID mismatch: token={authenticated_user_id}, path={user_id}")
                    await websocket.close(code=4001, reason="User ID mismatch")
                    return
                logger.info(f"✅ WebSocket authenticated successfully for user: {user_id}")
            except Exception as e:
                logger.error(f"WebSocket authentication failed for user {user_id}: {e}")
                await websocket.close(code=4001, reason="Authentication failed")
                return

        # Connect user
        await websocket_manager.connect(
            websocket, user_id, {"endpoint": "/ws/chat", "authenticated": bool(token)}
        )

        # Initialize services
        # chat_service = ChatService()  # 已移除，使用agent_router替代
        health_advice_service = HealthAdviceService()
        family_service = FamilyService()

        # Main message loop
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                message = WebSocketMessage(**message_data)

                # Update user activity
                websocket_manager.user_sessions[user_id][
                    "last_activity"
                ] = datetime.now().isoformat()

                # Send acknowledgment
                await websocket_manager.send_status_update(
                    user_id, "sending", "正在处理您的消息..."
                )

                # Handle different message types
                if message.type == "health_chat":
                    await handle_health_chat(user_id, message, health_advice_service)

                elif message.type == "general_chat":
                    await handle_general_chat(user_id, message)

                elif message.type == "rag_query":
                    await handle_rag_query(user_id, message)

                elif message.type == "switch_member":
                    await handle_member_switch(user_id, message, family_service)

                elif message.type == "get_status":
                    await handle_status_request(user_id, message)

                elif message.type == "pong":
                    # Handle pong response for heartbeat
                    await websocket_manager.handle_pong(user_id)
                    logger.debug(f"Received pong from user {user_id}")

                else:
                    await websocket_manager.send_status_update(
                        user_id, "error", f"未知的消息类型: {message.type}"
                    )

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user: {user_id}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from user {user_id}: {e}")
                await websocket_manager.send_status_update(
                    user_id, "error", "消息格式错误，请发送有效的JSON"
                )
            except Exception as e:
                logger.error(
                    f"Error handling WebSocket message for user {user_id}: {e}"
                )
                await websocket_manager.send_status_update(
                    user_id, "error", f"处理消息时发生错误: {str(e)}"
                )

    except Exception as e:
        logger.error(f"WebSocket connection error for user {user_id}: {e}")
        try:
            await websocket.close(code=4000, reason=str(e))
        except:
            pass

    finally:
        # Clean up
        websocket_manager.disconnect(user_id)


async def handle_health_chat(
    user_id: str, message: WebSocketMessage, health_advice_service: HealthAdviceService
):
    """Handle health chat messages with streaming response"""
    try:
        # Extract message data
        query = message.data.get("message", "")
        conversation_id = message.conversation_id
        active_member_id = message.active_member_id or user_id

        if not query:
            await websocket_manager.send_status_update(
                user_id, "error", "消息内容不能为空"
            )
            return

        # Update session
        websocket_manager.update_user_session(
            user_id,
            {"conversation_id": conversation_id, "active_member_id": active_member_id},
        )

        # Create advice request
        advice_request = HealthAdviceRequest(
            user_query=query,
            conversation_id=conversation_id,
            user_id=active_member_id,
            context=message.data.get("context", {}),
            priority="normal",
        )

        # Update status to streaming
        await websocket_manager.send_status_update(
            user_id, "streaming", "AI正在生成回复..."
        )

        # Get streaming response
        full_response = ""
        async for token in health_advice_service.get_streaming_advice(advice_request):
            full_response += token
            await websocket_manager.send_streaming_message(user_id, token, "streaming")

        # Send completion status
        await websocket_manager.send_status_update(
            user_id,
            "done",
            "回复完成",
            {
                "full_response": full_response,
                "conversation_id": conversation_id,
                "response_length": len(full_response),
            },
        )

    except Exception as e:
        logger.error(f"Error in health chat for user {user_id}: {e}")
        await websocket_manager.send_status_update(
            user_id, "error", f"健康咨询处理失败: {str(e)}"
        )


async def handle_general_chat(
    user_id: str, message: WebSocketMessage
):
    """Handle general chat messages using agent_router"""
    try:
        query = message.data.get("message", "")
        conversation_id = message.conversation_id

        if not query:
            await websocket_manager.send_status_update(
                user_id, "error", "消息内容不能为空"
            )
            return

        # Use agent_router to process the message
        await websocket_manager.send_status_update(user_id, "streaming", "正在处理...")

        # Process message with agent_router
        response_data = await agent_router.process_message(
            user_id=user_id,
            message=query,
            context={
                "conversation_id": conversation_id,
                "request_type": "general_chat",
            },
        )

        response = response_data.get("message", "抱歉，我现在无法处理您的请求。")

        # Send response in chunks to simulate streaming
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            chunk = response[i : i + chunk_size]
            await websocket_manager.send_streaming_message(user_id, chunk, "streaming")
            await asyncio.sleep(0.1)  # Simulate delay

        # Send completion
        await websocket_manager.send_status_update(
            user_id,
            "done",
            "回复完成",
            {"full_response": response, "conversation_id": conversation_id},
        )

    except Exception as e:
        logger.error(f"Error in general chat for user {user_id}: {e}")
        await websocket_manager.send_status_update(
            user_id, "error", f"聊天处理失败: {str(e)}"
        )


async def handle_rag_query(user_id: str, message: WebSocketMessage):
    """Handle RAG document retrieval queries - 特种突击任务"""
    try:
        # 提取查询参数
        query = message.data.get("query", "")
        k = message.data.get("k", 3)

        if not query:
            await websocket_manager.send_status_update(
                user_id, "error", "查询内容不能为空"
            )
            return

        # 获取RAG服务
        rag_service = get_rag_service()

        # 更新状态
        await websocket_manager.send_status_update(
            user_id, "searching", f"正在检索相关文档..."
        )

        # 执行RAG检索
        results = await rag_service.retrieve_from_rag(
            user_query=query,
            k=k
        )

        # 流式发送结果
        await websocket_manager.send_status_update(
            user_id, "streaming", "检索完成，正在发送结果..."
        )

        # 逐个发送文档
        for i, doc in enumerate(results):
            doc_message = {
                "type": "rag_document",
                "index": i + 1,
                "total": len(results),
                "content": doc,
                "timestamp": datetime.now().isoformat(),
            }
            await websocket_manager.send_personal_message(user_id, doc_message)
            await asyncio.sleep(0.1)  # 小延迟以模拟流式传输

        # 发送完成状态
        await websocket_manager.send_status_update(
            user_id,
            "done",
            f"RAG检索完成，共找到 {len(results)} 个相关文档",
            {
                "query": query,
                "total_found": len(results),
                "results": results
            }
        )

        logger.info(f"RAG查询成功 - 用户: {user_id}, 查询: {query[:50]}, 结果数: {len(results)}")

    except Exception as e:
        logger.error(f"RAG查询失败 - 用户: {user_id}, 错误: {e}")
        await websocket_manager.send_status_update(
            user_id, "error", f"RAG检索失败: {str(e)}"
        )


async def handle_member_switch(
    user_id: str, message: WebSocketMessage, family_service: FamilyService
):
    """Handle member switching for family context"""
    try:
        target_member_id = message.data.get("target_member_id")
        if not target_member_id:
            await websocket_manager.send_status_update(
                user_id, "error", "缺少目标成员ID"
            )
            return

        # Update session
        websocket_manager.update_user_session(
            user_id, {"active_member_id": target_member_id}
        )

        await websocket_manager.send_status_update(
            user_id,
            "done",
            f"已切换到成员: {target_member_id}",
            {"active_member_id": target_member_id},
        )

    except Exception as e:
        logger.error(f"Error switching member for user {user_id}: {e}")
        await websocket_manager.send_status_update(
            user_id, "error", f"切换成员失败: {str(e)}"
        )


async def handle_status_request(user_id: str, message: WebSocketMessage):
    """Handle status requests"""
    try:
        session = websocket_manager.get_user_session(user_id)
        await websocket_manager.send_status_update(
            user_id,
            "done",
            "状态信息",
            {
                "session": session,
                "connected_users": len(websocket_manager.get_connected_users()),
                "server_time": datetime.now().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Error handling status request for user {user_id}: {e}")
        await websocket_manager.send_status_update(
            user_id, "error", f"获取状态失败: {str(e)}"
        )


# Health and monitoring endpoints
@websocket_router.get("/ws/health")
async def websocket_health():
    """WebSocket service health check"""
    return {
        "status": "healthy",
        "service": "websocket",
        "active_connections": len(websocket_manager.get_connected_users()),
        "timestamp": datetime.now().isoformat(),
    }


@websocket_router.get("/ws/stats")
async def websocket_stats():
    """WebSocket service statistics"""
    return {
        "active_connections": len(websocket_manager.get_connected_users()),
        "connected_users": websocket_manager.get_connected_users(),
        "sessions": {
            user_id: {
                "connected_at": session.get("connected_at"),
                "last_activity": session.get("last_activity"),
                "active_member_id": session.get("active_member_id"),
            }
            for user_id, session in websocket_manager.user_sessions.items()
        },
        "timestamp": datetime.now().isoformat(),
    }
