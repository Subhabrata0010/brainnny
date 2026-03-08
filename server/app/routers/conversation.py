"""
Conversation router - Handles message storage.
POST /conversation - Store user messages in conversation logs.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import ConversationRequest, ConversationResponse
from app.services.memory_service import MemoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.post("", response_model=ConversationResponse)
def store_conversation(request: ConversationRequest):
    """
    Store a conversation message.
    
    Process:
    1. Store message in conversation_logs
    2. Create or update episode for session
    3. Update episode message count
    4. Generate embedding for episode (async in production)
    
    Args:
        request: Conversation request with user_id, session_id, message, role
    
    Returns:
        ConversationResponse with message_id and episode_id
    """
    try:
        logger.info(f"Storing message for user {request.user_id}, session {request.session_id}")
        
        # Store message and get episode ID
        message_id, episode_id = MemoryService.store_message(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message,
            role=request.role
        )
        
        # Update episode embedding (based on all messages)
        # In production, this could be async/batched
        MemoryService.update_episode_embedding(episode_id)
        
        logger.info(f"Stored message {message_id} in episode {episode_id}")
        
        return ConversationResponse(
            message_id=message_id,
            episode_id=episode_id,
            stored=True
        )
    
    except Exception as e:
        logger.error(f"Error storing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))