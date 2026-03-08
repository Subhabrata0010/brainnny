-- ============================================================================
-- Migration 003: Update vector dimensions from 1024 to 768
-- Change embedding model from arctic-embed-l to arctic-embed-m
-- ============================================================================

-- Episodes table
ALTER TABLE episodes DROP COLUMN embedding;
ALTER TABLE episodes ADD COLUMN embedding VECTOR(FLOAT, 768);

-- Semantic memory table  
ALTER TABLE semantic_memory DROP COLUMN embedding;
ALTER TABLE semantic_memory ADD COLUMN embedding VECTOR(FLOAT, 768);

-- Note: All existing embeddings will be NULL after this migration
-- They will be regenerated on next update/insert
