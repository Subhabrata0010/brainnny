-- ============================================================================
-- Second Brain - Complete Snowflake Schema
-- Database: SECOND_BRAIN_DB
-- ============================================================================

-- Create database and schema
CREATE DATABASE IF NOT EXISTS SECOND_BRAIN_DB;
USE DATABASE SECOND_BRAIN_DB;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- ============================================================================
-- TABLE: pages
-- Stores conversation session summaries with aggregated embeddings
-- ============================================================================

CREATE TABLE IF NOT EXISTS pages (
    page_id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    session_title STRING,
    summary STRING,
    embedding VECTOR(FLOAT, 1024),
    importance_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY (user_id, created_at);

-- Index for faster user queries
CREATE INDEX IF NOT EXISTS idx_pages_user ON pages(user_id);

-- ============================================================================
-- TABLE: nodes
-- Stores hierarchical memory nodes within pages
-- ============================================================================

CREATE TABLE IF NOT EXISTS nodes (
    node_id STRING PRIMARY KEY,
    page_id STRING NOT NULL,
    parent_node_id STRING,
    node_type STRING NOT NULL,  -- topic, idea, decision, constraint, promise, summary
    content STRING NOT NULL,
    embedding VECTOR(FLOAT, 1024),
    importance_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    
    -- Foreign key constraint
    CONSTRAINT fk_nodes_page FOREIGN KEY (page_id) REFERENCES pages(page_id),
    CONSTRAINT fk_nodes_parent FOREIGN KEY (parent_node_id) REFERENCES nodes(node_id)
)
CLUSTER BY (page_id);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_nodes_page ON nodes(page_id);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);

-- ============================================================================
-- TABLE: user_profile
-- Stores user preferences and communication patterns
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_profile (
    user_id STRING PRIMARY KEY,
    communication_style STRING,
    recurring_topics ARRAY,
    preferences VARIANT,  -- JSON object for flexible preferences
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- TABLE: cross_model_sessions
-- Tracks sessions across different LLM models
-- ============================================================================

CREATE TABLE IF NOT EXISTS cross_model_sessions (
    session_id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    model_used STRING NOT NULL,  -- claude, openai, gemini
    page_ids ARRAY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES user_profile(user_id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON cross_model_sessions(user_id);

-- ============================================================================
-- TABLE: reminder_log
-- Stores promises and commitments with reminder dates
-- ============================================================================

CREATE TABLE IF NOT EXISTS reminder_log (
    reminder_id STRING PRIMARY KEY,
    user_id STRING NOT NULL,
    promise_node_id STRING NOT NULL,
    reminder_date DATE,
    status STRING DEFAULT 'open',  -- open, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    
    CONSTRAINT fk_reminder_node FOREIGN KEY (promise_node_id) REFERENCES nodes(node_id)
);

CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminder_log(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminder_log(status);

-- ============================================================================
-- VIEW: scoring_view
-- Implements scoring formula for node ranking
-- ============================================================================

CREATE OR REPLACE VIEW scoring_view AS
SELECT 
    n.node_id,
    n.page_id,
    n.node_type,
    n.content,
    n.importance_score,
    n.created_at,
    n.embedding,
    -- Recency decay component (decays over time)
    EXP(-0.00005 * DATEDIFF('second', n.created_at, CURRENT_TIMESTAMP())) as recency_score,
    -- Page importance component
    p.importance_score as page_importance
FROM nodes n
JOIN pages p ON n.page_id = p.page_id;

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Create a test user profile
INSERT INTO user_profile (user_id, communication_style, recurring_topics, preferences)
SELECT 
    'test_user_001',
    'professional',
    ARRAY_CONSTRUCT('AI', 'Machine Learning', 'Product Development'),
    PARSE_JSON('{"timezone": "UTC", "notification_preference": "email"}')
WHERE NOT EXISTS (SELECT 1 FROM user_profile WHERE user_id = 'test_user_001');

-- ============================================================================
-- GRANTS (adjust for your security model)
-- ============================================================================

-- Grant usage on database and schema
GRANT USAGE ON DATABASE SECOND_BRAIN_DB TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA PUBLIC TO ROLE PUBLIC;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA PUBLIC TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA PUBLIC TO ROLE PUBLIC;

-- Grant future permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA PUBLIC TO ROLE PUBLIC;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA PUBLIC TO ROLE PUBLIC;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created
SHOW TABLES;

-- Verify view created
SHOW VIEWS;

-- Test vector embedding (requires Cortex)
-- SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024('e5-base-v2', 'test message');

-- ============================================================================
-- CLEANUP (if needed)
-- ============================================================================

-- DROP DATABASE SECOND_BRAIN_DB CASCADE;