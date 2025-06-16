"""
Chat-related data models for AuraWell

This module contains all Pydantic models related to chat functionality,
including chat requests, responses, conversations, and member context.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
# Define base response classes for now to avoid circular imports
class BaseResponse:
    """Base response model"""
    pass

class SuccessResponse:
    """Success response model"""
    pass


# ================================
# Chat Core Models
# ================================

class ChatRequest(BaseModel):
    """Chat conversation request"""
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatData(BaseModel):
    """Chat response data"""
    reply: str
    user_id: str
    conversation_id: Optional[str] = None
    tools_used: Optional[List[str]] = None


class ChatResponse(BaseResponse):
    """Chat conversation response - 保持向后兼容的格式"""
    reply: str
    user_id: str
    conversation_id: Optional[str] = None
    tools_used: Optional[List[str]] = None


class ChatMessage(BaseModel):
    """Individual chat message"""
    id: str
    sender: str  # 'user' or 'agent'
    content: str
    timestamp: datetime
    suggestions: Optional[List['HealthSuggestion']] = None
    quick_replies: Optional[List['QuickReply']] = None


# ================================
# Health Chat Models
# ================================

class HealthSuggestion(BaseModel):
    """Health suggestion card"""
    title: str
    content: str
    action: Optional[str] = None
    action_text: Optional[str] = None


class QuickReply(BaseModel):
    """Quick reply option"""
    text: str


class HealthChatRequest(BaseModel):
    """Enhanced health chat request with conversation context"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class HealthChatResponse(BaseResponse):
    """Enhanced health chat response with suggestions and quick replies"""
    reply: str
    conversation_id: str
    message_id: str
    timestamp: datetime
    suggestions: Optional[List[HealthSuggestion]] = None
    quick_replies: Optional[List[QuickReply]] = None


class EnhancedHealthChatRequest(BaseModel):
    """Enhanced health chat request with member context"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    member_id: Optional[str] = Field(None, description="Active family member ID for data isolation")
    context: Optional[Dict[str, Any]] = None

    @field_validator('member_id')
    @classmethod
    def validate_member_id(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Member ID cannot be empty if provided')
        return v


# ================================
# Conversation Models
# ================================

class ConversationCreateRequest(BaseModel):
    """Request to create a new conversation"""
    type: str = Field(default="health_consultation")
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Conversation metadata response"""
    conversation_id: str
    type: str
    created_at: datetime
    title: Optional[str] = None
    status: str = "active"


class ConversationListItem(BaseModel):
    """Conversation list item"""
    id: str
    title: Optional[str] = None
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    status: str = "active"


class ConversationListResponse(BaseResponse):
    """List of user conversations"""
    conversations: List[ConversationListItem] = Field(default_factory=list)


class ChatHistoryRequest(BaseModel):
    """Request for chat history"""
    conversation_id: str
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ChatHistoryResponse(BaseResponse):
    """Chat history response"""
    messages: List[ChatMessage]
    total: int
    has_more: bool


class ConversationHistoryKey(BaseModel):
    """Conversation history composite key"""
    user_id: str
    member_id: Optional[str] = None
    session_id: Optional[str] = None

    @property
    def composite_key(self) -> str:
        """Generate composite key for conversation history isolation"""
        parts = [self.user_id]
        if self.member_id:
            parts.append(f"member:{self.member_id}")
        if self.session_id:
            parts.append(f"session:{self.session_id}")
        return ":".join(parts)


# ================================
# Health Suggestions Models  
# ================================

class HealthSuggestionsResponse(BaseResponse):
    """Health suggestions template response"""
    suggestions: List[str]


# Update forward references
ChatMessage.model_rebuild() 