"""
Context router - Handles memory context retrieval.
POST /retrieve-context - Retrieve structured memory context.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    RetrieveContextRequest, ContextResponse, RetrievedContext
)
from app.services.retrieval_service import HybridRetrieval
from app.services.memory_service import MemoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/retrieve-context", tags=["context"])


@router.post("", response_model=ContextResponse)
def retrieve_context(request: RetrieveContextRequest):
    """
    Retrieve structured memory context using hybrid retrieval.
    
    Process:
    1. Candidate pruning (fast SQL filters)
    2. Vector similarity search (on pruned set)
    3. Hybrid ranking (combine scores)
    4. Assemble complete context
    
    Returns structured context that can be sent to any LLM.
    
    Args:
        request: Retrieval request with user_id, query, optional session_id
    
    Returns:
        ContextResponse with multi-layer memory context
    """
    try:
        logger.info(f"Retrieving context for user {request.user_id}")
        
        # Ensure user exists
        MemoryService._ensure_user_exists(request.user_id)
        
        # Initialize retrieval service
        retrieval = HybridRetrieval()
        
        # Retrieve episodic memory (relevant past conversations)
        episodes = retrieval.retrieve_episodes(
            user_id=request.user_id,
            query=request.query,
            max_results=request.max_episodes
        )
        
        logger.info(f"Retrieved {len(episodes)} relevant episodes")
        
        # Retrieve semantic memory (extracted knowledge)
        semantic_memories = retrieval.retrieve_semantic_memory(
            user_id=request.user_id,
            query=request.query,
            max_results=request.max_semantic
        )
        
        logger.info(f"Retrieved {len(semantic_memories)} semantic memories")
        
        # Get recent messages (working memory)
        recent_messages = retrieval.get_recent_messages(
            user_id=request.user_id,
            session_id=request.session_id,
            limit=request.include_recent
        )
        
        logger.info(f"Retrieved {len(recent_messages)} recent messages")
        
        # Get user profile
        user_profile = MemoryService.get_user_profile(request.user_id)
        
        # Assemble context summary
        context_summary = _build_context_summary(
            episodes=episodes,
            semantic_memories=semantic_memories,
            recent_messages=recent_messages,
            query=request.query
        )
        
        # Build complete context
        context = RetrievedContext(
            user_profile=user_profile,
            relevant_episodes=episodes,
            semantic_memory=semantic_memories,
            recent_messages=recent_messages,
            context_summary=context_summary
        )
        
        # Build response with stats
        response = ContextResponse(
            context=context,
            query=request.query,
            retrieval_stats={
                "episodes_retrieved": len(episodes),
                "semantic_memories": len(semantic_memories),
                "recent_messages": len(recent_messages)
            }
        )
        
        logger.info(f"Context retrieval complete for user {request.user_id}")
        return response
    
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _build_context_summary(episodes, semantic_memories, recent_messages, query: str) -> str:
    """
    Build a text summary of the retrieved context.
    This can be used as a prefix to LLM prompts.
    """
    sections = []
    
    # Add query
    sections.append(f"Query: {query}\n")
    
    # Add relevant episodes summary
    if episodes:
        sections.append("=== RELEVANT PAST CONVERSATIONS ===")
        for i, ep in enumerate(episodes[:3], 1):
            sections.append(f"{i}. {ep.summary}")
        sections.append("")
    
    # Add semantic memory
    if semantic_memories:
        sections.append("=== EXTRACTED KNOWLEDGE ===")
        by_type = {}
        for mem in semantic_memories:
            if mem.memory_type not in by_type:
                by_type[mem.memory_type] = []
            by_type[mem.memory_type].append(mem.content)
        
        for mem_type, contents in by_type.items():
            sections.append(f"{mem_type.upper()}:")
            for content in contents:
                sections.append(f"  • {content}")
        sections.append("")
    
    # Add recent messages
    if recent_messages:
        sections.append("=== RECENT CONVERSATION ===")
        for msg in recent_messages[-3:]:
            sections.append(f"{msg.role.upper()}: {msg.content[:100]}")
        sections.append("")
    
    return "\n".join(sections)