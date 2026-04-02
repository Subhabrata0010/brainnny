"""
Hybrid Retrieval Service with Candidate Pruning.
Implements multi-stage retrieval pipeline.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.core.snowflake_conn import execute_query, execute_query_with_in_clause, get_snowflake_connection
from app.models.schemas import (
    CandidateEpisode, ScoredEpisode, EpisodeResponse,
    SemanticMemoryResponse, ConversationLogResponse
)

logger = logging.getLogger(__name__)


class HybridRetrieval:
    """
    Multi-stage retrieval pipeline:
    1. Candidate Pruning (fast SQL filters)
    2. Vector Similarity Search (on pruned set)
    3. Hybrid Ranking (combine scores)
    """
    
    def __init__(self):
        logger.info("Initialized HybridRetrieval service")
    
    def candidate_pruning(
        self,
        user_id: str,
        days_back: int = 30,
        min_importance: float = 0.3,
        max_candidates: int = 200
    ) -> List[CandidateEpisode]:
        """
        Stage 1: Fast candidate pruning using SQL filters.
        
        Filters:
        - user_id (security)
        - recency (last N days)
        - importance (minimum threshold)
        - limit (max candidates)
        
        Args:
            user_id: User identifier
            days_back: Days to look back
            min_importance: Minimum importance score
            max_candidates: Maximum candidates to return
        
        Returns:
            List of candidate episodes with recency scores
        """
        logger.info(f"Pruning candidates for user {user_id}")
        
        pruning_query = """
        SELECT 
            episode_id,
            summary,
            importance_score,
            created_at,
            EXP(-0.00005 * DATEDIFF('second', created_at, CURRENT_TIMESTAMP())) as recency_score
        FROM episodes
        WHERE user_id = %(user_id)s
          AND created_at > DATEADD(day, %(days_back)s, CURRENT_TIMESTAMP())
          AND importance_score >= %(min_importance)s
        ORDER BY created_at DESC
        LIMIT %(max_candidates)s
        """
        
        results = execute_query(pruning_query, {
            "user_id": user_id,
            "days_back": -days_back,
            "min_importance": min_importance,
            "max_candidates": max_candidates
        })
        
        candidates = []
        for row in results:
            candidates.append(CandidateEpisode(
                episode_id=row[0],
                summary=row[1],
                importance_score=row[2],
                created_at=row[3],
                recency_score=row[4]
            ))
        
        logger.info(f"Pruned to {len(candidates)} candidates")
        return candidates
    
    def vector_similarity_search(
        self,
        candidates: List[CandidateEpisode],
        query: str,
        top_k: int = 10
    ) -> List[ScoredEpisode]:
        """
        Stage 2: Vector similarity search on pruned candidates.
        
        Uses Snowflake Cortex for embedding and similarity.
        
        Args:
            candidates: Pruned candidate episodes
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of episodes with similarity scores
        """
        if not candidates:
            return []
        
        logger.info(f"Running vector search on {len(candidates)} candidates")
        
        # Extract episode IDs
        candidate_ids = [c.episode_id for c in candidates]
        
        similarity_query = """
        SELECT 
            e.episode_id,
            e.summary,
            e.importance_score,
            e.message_count,
            e.created_at,
            VECTOR_COSINE_SIMILARITY(
                e.embedding,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(query)s)
            ) as semantic_similarity,
            EXP(-0.00005 * DATEDIFF('second', e.created_at, CURRENT_TIMESTAMP())) as recency_score,
            LEAST(1.0, e.message_count / 20.0) as contextual_relevance
        FROM episodes e
        WHERE e.episode_id IN ({placeholders})
          AND e.embedding IS NOT NULL
        ORDER BY semantic_similarity DESC
        LIMIT %(top_k)s
        """
        
        results = execute_query_with_in_clause(
            similarity_query, 
            candidate_ids,
            param_name="episode_id",
            other_params={"query": query, "top_k": top_k}
        )
        
        scored = []
        for row in results:
            scored.append(ScoredEpisode(
                episode_id=row[0],
                summary=row[1],
                importance_score=row[2],
                semantic_similarity=row[5],
                recency_score=row[6],
                contextual_relevance=row[7],
                final_score=0.0  # Will be computed in ranking
            ))
        
        logger.info(f"Vector search returned {len(scored)} results")
        return scored
    
    def hybrid_ranking(
        self,
        scored_episodes: List[ScoredEpisode]
    ) -> List[ScoredEpisode]:
        """
        Stage 3: Compute final hybrid ranking score.
        
        Formula:
        score = 0.4 * semantic_similarity +
                0.2 * recency_score +
                0.2 * importance_score +
                0.2 * contextual_relevance
        
        Args:
            scored_episodes: Episodes with component scores
        
        Returns:
            Episodes sorted by final score
        """
        logger.info(f"Computing hybrid scores for {len(scored_episodes)} episodes")
        
        for episode in scored_episodes:
            episode.final_score = (
                0.4 * episode.semantic_similarity +
                0.2 * episode.recency_score +
                0.2 * episode.importance_score +
                0.2 * episode.contextual_relevance
            )
        
        # Sort by final score descending
        scored_episodes.sort(key=lambda x: x.final_score, reverse=True)
        
        return scored_episodes
    
    def retrieve_episodes(
        self,
        user_id: str,
        query: str,
        max_results: int = 10
    ) -> List[EpisodeResponse]:
        """
        Complete retrieval pipeline for episodes.
        
        Pipeline:
        1. Candidate pruning
        2. Vector similarity
        3. Hybrid ranking
        
        Args:
            user_id: User identifier
            query: Search query
            max_results: Maximum episodes to return
        
        Returns:
            List of relevant episodes
        """
        # Stage 1: Candidate pruning
        candidates = self.candidate_pruning(user_id)
        
        if not candidates:
            logger.warning(f"No candidates found for user {user_id}")
            return []
        
        # Stage 2: Vector similarity
        scored = self.vector_similarity_search(candidates, query, top_k=max_results)
        
        if not scored:
            logger.warning(f"No similarity results for query: {query}")
            return []
        
        # Stage 3: Hybrid ranking
        ranked = self.hybrid_ranking(scored)
        
        # Fetch full episode details
        episode_ids = [ep.episode_id for ep in ranked]
        
        detail_query = """
        SELECT 
            episode_id, user_id, session_id, summary,
            importance_score, message_count, created_at, updated_at
        FROM episodes
        WHERE episode_id IN ({placeholders})
        """
        
        results = execute_query_with_in_clause(detail_query, episode_ids, param_name="episode_id")
        
        episodes = []
        for row in results:
            episodes.append(EpisodeResponse(
                episode_id=row[0],
                user_id=row[1],
                session_id=row[2],
                summary=row[3],
                importance_score=row[4],
                message_count=row[5],
                created_at=row[6],
                updated_at=row[7]
            ))
        
        logger.info(f"Retrieved {len(episodes)} episodes")
        return episodes
    
    def retrieve_semantic_memory(
        self,
        user_id: str,
        query: str,
        max_results: int = 5
    ) -> List[SemanticMemoryResponse]:
        """
        Retrieve relevant semantic memories.
        
        Args:
            user_id: User identifier
            query: Search query
            max_results: Maximum memories to return
        
        Returns:
            List of semantic memories
        """
        logger.info(f"Retrieving semantic memory for user {user_id}")
        
        semantic_query = """
        SELECT 
            memory_id,
            user_id,
            memory_type,
            content,
            confidence_score,
            created_at,
            VECTOR_COSINE_SIMILARITY(
                embedding,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(query)s)
            ) as similarity
        FROM semantic_memory
        WHERE user_id = %(user_id)s
          AND embedding IS NOT NULL
          AND confidence_score >= 0.5
        ORDER BY similarity DESC
        LIMIT %(max_results)s
        """
        
        results = execute_query(semantic_query, {
            "user_id": user_id,
            "query": query,
            "max_results": max_results
        })
        
        memories = []
        for row in results:
            memories.append(SemanticMemoryResponse(
                memory_id=row[0],
                user_id=row[1],
                memory_type=row[2],
                content=row[3],
                confidence_score=row[4],
                created_at=row[5]
            ))
        
        logger.info(f"Retrieved {len(memories)} semantic memories")
        return memories
    
    def get_recent_messages(
        self,
        user_id: str,
        session_id: str = None,
        limit: int = 5
    ) -> List[ConversationLogResponse]:
        """
        Get recent conversation messages.
        
        Args:
            user_id: User identifier
            session_id: Optional session filter
            limit: Number of messages to return
        
        Returns:
            List of recent messages
        """
        logger.info(f"Retrieving recent messages for user {user_id}")
        
        if session_id:
            query = """
            SELECT message_id, session_id, role, content, timestamp
            FROM conversation_logs
            WHERE user_id = %(user_id)s
              AND session_id = %(session_id)s
            ORDER BY timestamp DESC
            LIMIT %(limit)s
            """
            params = {"user_id": user_id, "session_id": session_id, "limit": limit}
        else:
            query = """
            SELECT message_id, session_id, role, content, timestamp
            FROM conversation_logs
            WHERE user_id = %(user_id)s
            ORDER BY timestamp DESC
            LIMIT %(limit)s
            """
            params = {"user_id": user_id, "limit": limit}
        
        results = execute_query(query, params)
        
        messages = []
        for row in results:
            messages.append(ConversationLogResponse(
                message_id=row[0],
                session_id=row[1],
                role=row[2],
                content=row[3],
                timestamp=row[4]
            ))
        
        # Reverse to chronological order
        messages.reverse()
        
        logger.info(f"Retrieved {len(messages)} recent messages")
        return messages