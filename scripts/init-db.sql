-- Initialize PostgreSQL database with pgvector extension
-- This script runs automatically when the PostgreSQL container is first created

-- Enable pgvector extension for vector similarity search (RAG-ready)
CREATE EXTENSION IF NOT EXISTS vector;

-- Log extension creation
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension enabled successfully';
END $$;
