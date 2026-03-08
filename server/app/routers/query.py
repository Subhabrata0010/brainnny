"""
Query router - Handles memory queries with two-level retrieval.
POST /query - Search memory and assemble context.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.memory_service import MemoryService
from app.services.prompt_service import PromptAssembler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query_memory(request: QueryRequest):
    """
    Query memory using two-level retrieval.
    
    Process:
    1. Search pages (session-level) using semantic similarity
    2. Search nodes within selected pages using scoring view
    3. Assemble context with user profile and commitments
    4. Return assembled prompt and metadata
    
    Args:
        request: Query request with user_id, query, model, optional reuse_pages
    
    Returns:
        QueryResponse with pages, nodes, assembled context
    """
    try:
        logger.info(f"Querying memory for user {request.user_id}")
        
        # Step 1: Search pages
        if request.reuse_pages:
            # User specified pages to reuse
            # For simplicity, fetch these pages directly
            # In production, validate ownership
            page_ids = request.reuse_pages
            pages = []  # Would need to fetch page details
        else:
            # Semantic search for relevant pages
            pages = MemoryService.search_pages(
                user_id=request.user_id,
                query=request.query,
                top_k=3
            )
            page_ids = [page.page_id for page in pages]
        
        logger.info(f"Found {len(pages)} relevant pages")
        
        # Step 2: Search nodes within selected pages
        nodes = MemoryService.search_nodes(
            page_ids=page_ids,
            query=request.query,
            user_id=request.user_id,
            top_k=10
        )
        
        logger.info(f"Found {len(nodes)} relevant nodes")
        
        # Step 3: Get user profile and commitments
        user_profile = MemoryService.get_user_profile(request.user_id)
        commitments = MemoryService.get_open_commitments(request.user_id)
        
        # Step 4: Assemble final context
        assembled_context = PromptAssembler.assemble_prompt(
            query=request.query,
            pages=pages,
            nodes=nodes,
            user_profile=user_profile,
            commitments=commitments
        )
        
        logger.info(f"Assembled context of {len(assembled_context)} characters")
        
        return QueryResponse(
            pages=pages,
            nodes=nodes,
            assembled_context=assembled_context,
            model_used=request.model
        )
    
    except Exception as e:
        logger.error(f"Error querying memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))