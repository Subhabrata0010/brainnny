-- ============================================================================
-- Second Brain - Multi-Layer Memory Schema (Migration 002)
-- Replaces page-node architecture with cognitive memory layers
-- ============================================================================

USE DATABASE SECOND_BRAIN_DB;
USE SCHEMA PUBLIC;

-- ============================================================================
-- Drop old tables (if migrating from previous version)
-- ============================================================================

-- Uncomment these if migrating from page-node architecture:
-- DROP TABLE IF EXISTS nodes;
-- DROP TABLE IF EXISTS pages;

-- ============================================================================
-- LAYER 1: WORKING MEMORY (In-Memory Cache - not stored in DB)
-- Handled in application layer
-- ============================================================================

-- ============================================================================
-- LAYER 2: EPISODIC MEMORY
-- Stores conversation episodes (sessions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS episodes (
    episode_id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    session_id STRING NOT NULL,
    summary STRING,
    embedding VECTOR(FLOAT, 768),
    importance_score FLOAT DEFAULT 0.5,
    message_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY (user_id, created_at);

-- Indexes for fast candidate pruning
CREATE INDEX IF NOT EXISTS idx_episodes_user ON episodes(user_id);
CREATE INDEX IF NOT EXISTS idx_episodes_session ON episodes(session_id);
CREATE INDEX IF NOT EXISTS idx_episodes_importance ON episodes(importance_score);

COMMENT ON TABLE episodes IS 'Episodic memory layer - stores conversation sessions';

-- ============================================================================
-- LAYER 3: SEMANTIC MEMORY
-- Stores extracted knowledge about the user
-- ============================================================================

CREATE TABLE IF NOT EXISTS semantic_memory (
    memory_id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    memory_type STRING NOT NULL,  -- preference, fact, topic, skill, goal
    content STRING NOT NULL,
    confidence_score FLOAT DEFAULT 0.5,
    embedding VECTOR(FLOAT, 768),
    source_episode_id STRING,  -- Reference to originating episode
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    
    CONSTRAINT fk_semantic_episode FOREIGN KEY (source_episode_id) REFERENCES episodes(episode_id)
)
CLUSTER BY (user_id, memory_type);

-- Indexes for semantic search
CREATE INDEX IF NOT EXISTS idx_semantic_user ON semantic_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_semantic_type ON semantic_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON semantic_memory(confidence_score);

COMMENT ON TABLE semantic_memory IS 'Semantic memory layer - extracted user knowledge';

-- ============================================================================
-- RAW CONVERSATION LOGS
-- Complete message history
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversation_logs (
    message_id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    session_id STRING NOT NULL,
    episode_id STRING,
    role STRING NOT NULL,  -- 'user' or 'assistant'
    content STRING NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    
    CONSTRAINT fk_log_episode FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
)
CLUSTER BY (user_id, timestamp);

-- Indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_logs_user ON conversation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_session ON conversation_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_logs_episode ON conversation_logs(episode_id);

COMMENT ON TABLE conversation_logs IS 'Raw conversation message history';

-- ============================================================================
-- USER PROFILE (Keep from original)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_profile (
    user_id STRING PRIMARY KEY,
    communication_style STRING,
    recurring_topics ARRAY,
    preferences VARIANT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

COMMENT ON TABLE user_profile IS 'User preferences and patterns';

-- ============================================================================
-- CANDIDATE PRUNING VIEW
-- Pre-filter candidates before vector search
-- ============================================================================

CREATE OR REPLACE VIEW candidate_episodes AS
SELECT 
    e.episode_id,
    e.user_id,
    e.session_id,
    e.summary,
    e.embedding,
    e.importance_score,
    e.message_count,
    e.created_at,
    e.updated_at,
    -- Recency score for ranking
    EXP(-0.00005 * DATEDIFF('second', e.created_at, CURRENT_TIMESTAMP())) as recency_score
FROM episodes e;

COMMENT ON VIEW candidate_episodes IS 'Episodes with pre-computed recency scores for pruning';

-- ============================================================================
-- RETRIEVAL SCORING VIEW
-- Implements hybrid ranking formula
-- ============================================================================

CREATE OR REPLACE VIEW episode_scores AS
SELECT 
    e.episode_id,
    e.user_id,
    e.summary,
    e.importance_score,
    e.created_at,
    -- Recency component (decays over time)
    EXP(-0.00005 * DATEDIFF('second', e.created_at, CURRENT_TIMESTAMP())) as recency_score,
    -- Contextual relevance (based on message count)
    LEAST(1.0, e.message_count / 20.0) as contextual_relevance
FROM episodes e;

COMMENT ON VIEW episode_scores IS 'Episode scores for hybrid ranking';

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Create test user
INSERT INTO user_profile (user_id, communication_style, recurring_topics, preferences)
SELECT 
    'test_user_001',
    'professional',
    ARRAY_CONSTRUCT('AI', 'Product Development', 'Engineering'),
    PARSE_JSON('{"timezone": "UTC", "notification_preference": "email"}')
WHERE NOT EXISTS (SELECT 1 FROM user_profile WHERE user_id = 'test_user_001');

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get recent episodes for a user (candidate pruning)
CREATE OR REPLACE FUNCTION get_candidate_episodes(
    p_user_id STRING,
    p_days_back INT,
    p_min_importance FLOAT,
    p_limit INT
)
RETURNS TABLE (
    episode_id STRING,
    summary STRING,
    importance_score FLOAT,
    created_at TIMESTAMP
)
AS
$$
    SELECT 
        episode_id,
        summary,
        importance_score,
        created_at
    FROM episodes
    WHERE user_id = p_user_id
    AND created_at > DATEADD(day, -p_days_back, CURRENT_TIMESTAMP())
    AND importance_score >= p_min_importance
    ORDER BY created_at DESC
    LIMIT p_limit
$$;

COMMENT ON FUNCTION get_candidate_episodes IS 'Fast candidate pruning for retrieval';

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT USAGE ON DATABASE SECOND_BRAIN_DB TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA PUBLIC TO ROLE PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA PUBLIC TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA PUBLIC TO ROLE PUBLIC;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify tables
SHOW TABLES;

-- Test Cortex embeddings
-- SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024('e5-base-v2', 'test message');

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================

/*
Migration from page-node to multi-layer:

1. Episodes replace Pages (session-level storage)
2. Semantic Memory replaces Nodes (extracted knowledge)
3. Conversation Logs added (raw message history)
4. Working Memory handled in application (not DB)
5. Candidate pruning via views and functions
6. Hybrid ranking formula implemented

New retrieval flow:
1. Candidate pruning (SQL filters)
2. Vector similarity (on pruned set)
3. Hybrid scoring (combine components)
4. Context assembly
*/