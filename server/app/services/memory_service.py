"""
Memory service - Multi-layer memory storage operations.
Handles episodes, semantic memory, and conversation logs.
"""

import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.snowflake_conn import execute_query, execute_query_with_in_clause, get_snowflake_connection
from app.models.schemas import (
    UserProfileResponse,
    PageResponse,
    NodeResponse,
    ExtractedNode,
    ExtractedConversation
)

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for multi-layer memory operations on Snowflake."""
    
    @staticmethod
    def _ensure_user_exists(user_id: str) -> None:
        """
        Ensure a user exists in user_profile table.
        Creates a new profile if it doesn't exist.
        
        Args:
            user_id: User identifier
        """
        check_query = """
        SELECT user_id FROM user_profile
        WHERE user_id = %(user_id)s
        """
        
        existing = execute_query(check_query, {"user_id": user_id})
        
        if not existing:
            # Create new user profile
            insert_query = """
            INSERT INTO user_profile (
                user_id, communication_style, recurring_topics, preferences, updated_at
            )
            SELECT 
                %(user_id)s, NULL, ARRAY_CONSTRUCT(), OBJECT_CONSTRUCT(), CURRENT_TIMESTAMP()
            """
            
            execute_query(insert_query, {"user_id": user_id}, fetch=False)
            logger.info(f"Created new user profile for {user_id}")
    
    @staticmethod
    def store_message(
        user_id: str,
        session_id: str,
        message: str,
        role: str = "user"
    ) -> tuple[str, str]:
        """
        Store a conversation message in conversation_logs.
        Create or update episode for the session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            message: Message content
            role: Message role (user or assistant)
        
        Returns:
            Tuple of (message_id, episode_id)
        """
        logger.info(f"Storing message for user {user_id}, session {session_id}")
        
        # Ensure user exists in user_profile
        MemoryService._ensure_user_exists(user_id)
        
        # Get or create episode
        episode_id = MemoryService._get_or_create_episode(user_id, session_id)
        
        # Generate message ID
        message_id = str(uuid.uuid4())
        
        # Insert message
        insert_query = """
        INSERT INTO conversation_logs (
            message_id, user_id, session_id, episode_id, role, content, timestamp
        )
        VALUES (
            %(message_id)s, %(user_id)s, %(session_id)s, 
            %(episode_id)s, %(role)s, %(content)s, CURRENT_TIMESTAMP()
        )
        """
        
        execute_query(insert_query, {
            "message_id": message_id,
            "user_id": user_id,
            "session_id": session_id,
            "episode_id": episode_id,
            "role": role,
            "content": message
        }, fetch=False)
        
        # Update episode message count
        MemoryService._update_episode_count(episode_id)
        
        logger.info(f"Message {message_id} stored in episode {episode_id}")
        return message_id, episode_id
    
    @staticmethod
    def _get_or_create_episode(user_id: str, session_id: str) -> str:
        """
        Get existing episode or create new one for session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        
        Returns:
            episode_id
        """
        # Check for existing episode
        check_query = """
        SELECT episode_id FROM episodes
        WHERE user_id = %(user_id)s AND session_id = %(session_id)s
        """
        
        existing = execute_query(check_query, {
            "user_id": user_id,
            "session_id": session_id
        })
        
        if existing:
            return existing[0][0]
        
        # Create new episode
        episode_id = str(uuid.uuid4())
        
        insert_query = """
        INSERT INTO episodes (
            episode_id, user_id, session_id, summary,
            importance_score, message_count, created_at, updated_at
        )
        VALUES (
            %(episode_id)s, %(user_id)s, %(session_id)s, %(summary)s,
            0.5, 0, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
        )
        """
        
        execute_query(insert_query, {
            "episode_id": episode_id,
            "user_id": user_id,
            "session_id": session_id,
            "summary": f"Session {session_id}"  # Placeholder, can be updated later
        }, fetch=False)
        
        logger.info(f"Created new episode {episode_id} for session {session_id}")
        return episode_id
    
    @staticmethod
    def _update_episode_count(episode_id: str):
        """Update message count for episode."""
        update_query = """
        UPDATE episodes
        SET message_count = message_count + 1,
            updated_at = CURRENT_TIMESTAMP()
        WHERE episode_id = %(episode_id)s
        """
        
        execute_query(update_query, {"episode_id": episode_id}, fetch=False)
    
    @staticmethod
    def update_episode_embedding(episode_id: str):
        """
        Generate and store embedding for episode based on its messages.
        Uses concatenated message content.
        
        Args:
            episode_id: Episode identifier
        """
        logger.info(f"Updating embedding for episode {episode_id}")
        
        # Get all messages for episode
        messages_query = """
        SELECT content FROM conversation_logs
        WHERE episode_id = %(episode_id)s
        ORDER BY timestamp ASC
        """
        
        results = execute_query(messages_query, {"episode_id": episode_id})
        
        if not results:
            logger.warning(f"No messages found for episode {episode_id}")
            return
        
        # Concatenate messages
        combined_text = " ".join([row[0] for row in results])
        
        # Limit to reasonable length for embedding (first 2000 chars)
        combined_text = combined_text[:2000]
        
        # Update embedding
        update_query = """
        UPDATE episodes
        SET embedding = SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(text)s),
            summary = %(summary)s,
            updated_at = CURRENT_TIMESTAMP()
        WHERE episode_id = %(episode_id)s
        """
        
        # Create basic summary (first 200 chars)
        summary = combined_text[:200] + "..." if len(combined_text) > 200 else combined_text
        
        execute_query(update_query, {
            "episode_id": episode_id,
            "text": combined_text,
            "summary": summary
        }, fetch=False)
        
        logger.info(f"Updated embedding for episode {episode_id}")
    
    @staticmethod
    def store_semantic_memory(
        user_id: str,
        memory_type: str,
        content: str,
        confidence_score: float = 0.5,
        source_episode_id: str = None
    ) -> str:
        """
        Store a semantic memory (extracted knowledge).
        
        Args:
            user_id: User identifier
            memory_type: Type of memory (preference, fact, topic, skill, goal)
            content: Memory content
            confidence_score: Confidence in this memory
            source_episode_id: Optional source episode
        
        Returns:
            memory_id
        """
        logger.info(f"Storing semantic memory for user {user_id}, type {memory_type}")
        
        memory_id = str(uuid.uuid4())
        
        insert_query = """
        INSERT INTO semantic_memory (
            memory_id, user_id, memory_type, content,
            confidence_score, source_episode_id, created_at, updated_at, embedding
        )
        SELECT
            %(memory_id)s, %(user_id)s, %(memory_type)s, %(content)s,
            %(confidence)s, %(source)s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
            SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(content)s)
        """
        
        execute_query(insert_query, {
            "memory_id": memory_id,
            "user_id": user_id,
            "memory_type": memory_type,
            "content": content,
            "confidence": confidence_score,
            "source": source_episode_id
        }, fetch=False)
        
        logger.info(f"Stored semantic memory {memory_id}")
        return memory_id
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[UserProfileResponse]:
        """
        Get user profile information.
        
        Args:
            user_id: User identifier
        
        Returns:
            User profile or None
        """
        query = """
        SELECT user_id, communication_style, recurring_topics, preferences
        FROM user_profile
        WHERE user_id = %(user_id)s
        """
        
        results = execute_query(query, {"user_id": user_id})
        
        if results:
            row = results[0]
            # Parse JSON strings from Snowflake to Python objects
            recurring_topics = json.loads(row[2]) if row[2] and isinstance(row[2], str) else (row[2] or [])
            preferences = json.loads(row[3]) if row[3] and isinstance(row[3], str) else (row[3] or {})
            
            return UserProfileResponse(
                user_id=row[0],
                communication_style=row[1],
                recurring_topics=recurring_topics,
                preferences=preferences
            )
        
        return None

        """
        Create or update a page for a conversation session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            extraction: Extracted conversation data
        
        Returns:
            page_id
        """
        # Check if page exists for this session
        check_query = """
        SELECT page_id FROM pages 
        WHERE user_id = %(user_id)s AND page_id = %(session_id)s
        """
        
        existing = execute_query(check_query, {
            "user_id": user_id,
            "session_id": session_id
        })
        
        if existing:
            # Update existing page
            update_query = """
            UPDATE pages
            SET 
                summary = %(summary)s,
                importance_score = %(importance)s,
                updated_at = CURRENT_TIMESTAMP()
            WHERE page_id = %(page_id)s AND user_id = %(user_id)s
            """
            
            execute_query(update_query, {
                "page_id": session_id,
                "user_id": user_id,
                "summary": extraction.summary,
                "importance": extraction.overall_importance
            }, fetch=False)
            
            return session_id
        else:
            # Create new page (without embedding initially)
            insert_query = """
            INSERT INTO pages (
                page_id, user_id, session_title, summary, 
                importance_score, created_at, updated_at
            )
            VALUES (
                %(page_id)s, %(user_id)s, %(title)s, %(summary)s,
                %(importance)s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
            )
            """
            
            execute_query(insert_query, {
                "page_id": session_id,
                "user_id": user_id,
                "title": extraction.session_title,
                "summary": extraction.summary,
                "importance": extraction.overall_importance
            }, fetch=False)
            
            return session_id
    
    @staticmethod
    def create_nodes(page_id: str, nodes: List[ExtractedNode]) -> int:
        """
        Create nodes for a page and generate their embeddings.
        
        Args:
            page_id: Parent page identifier
            nodes: List of extracted nodes
        
        Returns:
            Number of nodes created
        """
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        try:
            for node in nodes:
                node_id = str(uuid.uuid4())
                
                # Insert node with Cortex embedding
                insert_query = """
                INSERT INTO nodes (
                    node_id, page_id, parent_node_id, node_type, 
                    content, importance_score, created_at, embedding
                )
                SELECT 
                    %(node_id)s,
                    %(page_id)s,
                    NULL,
                    %(node_type)s,
                    %(content)s,
                    %(importance)s,
                    CURRENT_TIMESTAMP(),
                    SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(content)s)
                """
                
                cursor.execute(insert_query, {
                    "node_id": node_id,
                    "page_id": page_id,
                    "node_type": node.node_type,
                    "content": node.content,
                    "importance": node.importance_score
                })
            
            return len(nodes)
        
        finally:
            cursor.close()
    
    @staticmethod
    def update_page_embedding(page_id: str):
        """
        Update page embedding by creating embedding from concatenated node content.
        
        Args:
            page_id: Page identifier
        """
        # Get all node content and create embedding from combined text
        get_nodes_query = """
        SELECT content FROM nodes
        WHERE page_id = %(page_id)s
        ORDER BY created_at
        """
        
        try:
            results = execute_query(get_nodes_query, {"page_id": page_id})
            
            if results and len(results) > 0:
                # Concatenate node contents (limit to reasonable length)
                combined_content = " ".join([row[0] for row in results])[:2000]
                
                # Update page embedding with combined content
                update_query = """
                UPDATE pages
                SET embedding = SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(content)s),
                    updated_at = CURRENT_TIMESTAMP()
                WHERE page_id = %(page_id)s
                """
                execute_query(update_query, {"page_id": page_id, "content": combined_content}, fetch=False)
            else:
                # No nodes, use summary
                fallback_query = """
                UPDATE pages
                SET embedding = SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', summary),
                    updated_at = CURRENT_TIMESTAMP()
                WHERE page_id = %(page_id)s
                """
                execute_query(fallback_query, {"page_id": page_id}, fetch=False)
        
        except Exception as e:
            logger.error(f"Error updating page embedding: {e}")
            # Fallback: use summary embedding
            fallback_query = """
            UPDATE pages
            SET embedding = SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', summary),
                updated_at = CURRENT_TIMESTAMP()
            WHERE page_id = %(page_id)s
            """
            execute_query(fallback_query, {"page_id": page_id}, fetch=False)
    
    @staticmethod
    def search_pages(user_id: str, query: str, top_k: int = 3) -> List[PageResponse]:
        """
        Search for relevant pages using semantic similarity.
        
        Args:
            user_id: User identifier
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of relevant pages
        """
        search_query = """
        SELECT 
            page_id,
            user_id,
            session_title,
            summary,
            importance_score,
            created_at,
            updated_at,
            VECTOR_COSINE_SIMILARITY(
                embedding,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(query)s)
            ) as similarity
        FROM pages
        WHERE user_id = %(user_id)s
          AND embedding IS NOT NULL
        ORDER BY similarity DESC
        LIMIT %(top_k)s
        """
        
        results = execute_query(search_query, {
            "user_id": user_id,
            "query": query,
            "top_k": top_k
        })
        
        pages = []
        for row in results:
            pages.append(PageResponse(
                page_id=row[0],
                user_id=row[1],
                session_title=row[2],
                summary=row[3],
                importance_score=row[4],
                created_at=row[5],
                updated_at=row[6]
            ))
        
        return pages
    
    @staticmethod
    def search_nodes(
        page_ids: List[str], 
        query: str, 
        user_id: str,
        top_k: int = 10
    ) -> List[NodeResponse]:
        """
        Search for relevant nodes within specified pages using scoring view.
        
        Args:
            page_ids: List of page IDs to search within
            query: Search query
            user_id: User identifier (for security)
            top_k: Number of results to return
        
        Returns:
            List of relevant nodes
        """
        if not page_ids:
            return []
        
        # Use scoring view for ranking
        search_query = """
        WITH query_embedding AS (
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', %(query)s) as qemb
        ),
        scored_nodes AS (
            SELECT 
                n.node_id,
                n.page_id,
                n.parent_node_id,
                n.node_type,
                n.content,
                n.importance_score,
                n.created_at,
                -- Compute combined score
                (
                    0.4 * VECTOR_COSINE_SIMILARITY(n.embedding, (SELECT qemb FROM query_embedding)) +
                    0.2 * EXP(-0.00005 * DATEDIFF('second', n.created_at, CURRENT_TIMESTAMP())) +
                    0.2 * n.importance_score +
                    0.2 * VECTOR_COSINE_SIMILARITY(n.embedding, (SELECT qemb FROM query_embedding))
                ) as combined_score
            FROM nodes n
            JOIN pages p ON n.page_id = p.page_id
            WHERE n.page_id IN ({placeholders})
              AND p.user_id = %(user_id)s
        )
        SELECT 
            node_id, page_id, parent_node_id, node_type, 
            content, importance_score, created_at
        FROM scored_nodes
        ORDER BY combined_score DESC
        LIMIT %(top_k)s
        """
        
        results = execute_query_with_in_clause(
            search_query,
            page_ids,
            param_name="page_id",
            other_params={
                "query": query,
                "user_id": user_id,
                "top_k": top_k
            }
        )
        
        nodes = []
        for row in results:
            nodes.append(NodeResponse(
                node_id=row[0],
                page_id=row[1],
                parent_node_id=row[2],
                node_type=row[3],
                content=row[4],
                importance_score=row[5],
                created_at=row[6]
            ))
        
        return nodes
    
    @staticmethod
    def get_open_commitments(user_id: str) -> List[Dict[str, Any]]:
        """
        Get open commitments/promises for user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of open commitments
        """
        query = """
        SELECT n.content, r.reminder_date, r.status
        FROM reminder_log r
        JOIN nodes n ON r.promise_node_id = n.node_id
        JOIN pages p ON n.page_id = p.page_id
        WHERE p.user_id = %(user_id)s
          AND r.status = 'open'
        ORDER BY r.reminder_date ASC
        """
        
        results = execute_query(query, {"user_id": user_id})
        
        commitments = []
        for row in results:
            commitments.append({
                "content": row[0],
                "reminder_date": row[1],
                "status": row[2]
            })
        
        return commitments