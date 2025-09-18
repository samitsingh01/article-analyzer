-- backend/init.sql
-- PostgreSQL Database initialization script

-- Connect to the default database first
\c postgres;

-- Check if database exists and create if it doesn't
SELECT 'CREATE DATABASE smart_summarizer'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'smart_summarizer')\gexec

-- Connect to our database
\c smart_summarizer;

-- Create extension for UUID generation (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE smart_summarizer TO postgres;
