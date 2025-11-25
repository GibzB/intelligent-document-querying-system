-- Aurora PostgreSQL setup for Bedrock Knowledge Base
-- Run these commands in the Aurora PostgreSQL Query Editor

-- 1. Create vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create bedrock integration schema
CREATE SCHEMA IF NOT EXISTS bedrock_integration;

-- 3. Create bedrock user (replace 'your_password' with actual password from Secrets Manager)
-- Get password from: aws secretsmanager get-secret-value --secret-id doc-query-system-dev-bedrock-user --region us-east-1
CREATE USER IF NOT EXISTS bedrock_user WITH LOGIN PASSWORD 'your_password_here';

-- 4. Grant permissions to bedrock user
GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;

-- 5. Create the knowledge base table
CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_knowledge_base (
    id uuid PRIMARY KEY,
    embedding vector(1536),
    chunks text,
    metadata jsonb
);

-- 6. Grant table permissions
GRANT ALL ON TABLE bedrock_integration.bedrock_knowledge_base TO bedrock_user;

-- 7. Create required indexes
CREATE INDEX IF NOT EXISTS idx_bedrock_kb_vector 
ON bedrock_integration.bedrock_knowledge_base 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_bedrock_kb_text 
ON bedrock_integration.bedrock_knowledge_base 
USING gin (to_tsvector('english', chunks));

-- 8. Verify setup
SELECT * FROM pg_extension WHERE extname = 'vector';
SELECT table_schema || '.' || table_name as show_tables 
FROM information_schema.tables 
WHERE table_type = 'BASE TABLE' 
AND table_schema = 'bedrock_integration';