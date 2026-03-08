"""
Pydantic models for request/response validation.
Updated for multi-layer memory architecture.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ConversationRequest(BaseModel):
    """Request model for storing conversation messages."""
    user_id: str
    session_id: str
    message: str
    role: str = "user"  # 'user' or 'assistant'


class RetrieveContextRequest(BaseModel):
    """Request model for retrieving memory context."""
    user_id: str
    query: str
    session_id: Optional[str] = None
    max_episodes: int = 10
    max_semantic: int = 5
    include_recent: int = 5  # Number of recent messages to include


# ============================================================================
# RESPONSE MODELS - MULTI-LAYER MEMORY
# ============================================================================

class EpisodeResponse(BaseModel):
    """Response model for an episodic memory."""
    episode_id: str
    user_id: str
    session_id: str
    summary: str
    importance_score: float
    message_count: int
    created_at: datetime
    updated_at: datetime


class SemanticMemoryResponse(BaseModel):
    """Response model for semantic memory."""
    memory_id: str
    user_id: str
    memory_type: str  # preference, fact, topic, skill, goal
    content: str
    confidence_score: float
    created_at: datetime


class ConversationLogResponse(BaseModel):
    """Response model for conversation log entry."""
    message_id: str
    session_id: str
    role: str
    content: str
    timestamp: datetime


class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    user_id: str
    communication_style: Optional[str]
    recurring_topics: Optional[List[str]]
    preferences: Optional[Dict[str, Any]]


class RetrievedContext(BaseModel):
    """Complete retrieved context for LLM consumption."""
    user_profile: Optional[UserProfileResponse]
    relevant_episodes: List[EpisodeResponse]
    semantic_memory: List[SemanticMemoryResponse]
    recent_messages: List[ConversationLogResponse]
    context_summary: str


class ConversationResponse(BaseModel):
    """Response model for conversation storage."""
    message_id: str
    episode_id: str
    stored: bool = True
    message: str = "Message stored successfully"


class ContextResponse(BaseModel):
    """Response model for context retrieval."""
    context: RetrievedContext
    query: str
    retrieval_stats: Dict[str, int]


# ============================================================================
# INTERNAL MODELS
# ============================================================================

class CandidateEpisode(BaseModel):
    """Episode candidate after pruning."""
    episode_id: str
    summary: str
    importance_score: float
    recency_score: float
    created_at: datetime


class ScoredEpisode(BaseModel):
    """Episode with computed relevance score."""
    episode_id: str
    summary: str
    importance_score: float
    semantic_similarity: float
    recency_score: float
    contextual_relevance: float
    final_score: float


class WorkingMemoryState(BaseModel):
    """Working memory state (in-memory cache)."""
    session_id: str
    recent_messages: List[Dict[str, str]]
    last_updated: datetime