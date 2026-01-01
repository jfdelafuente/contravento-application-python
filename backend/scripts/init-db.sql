-- ContraVento Database Initialization Script
-- This script runs automatically when PostgreSQL container starts
-- Note: Alembic migrations will create all tables and relationships

-- Enable UUID extension (required for user_id, trip_id, etc.)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto extension (useful for additional security features)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create database if not exists (handled by POSTGRES_DB in docker-compose)
-- The database 'contravento' is created automatically by the postgres container

-- Set default timezone to UTC
SET timezone = 'UTC';

-- Grant privileges to contravento_user
GRANT ALL PRIVILEGES ON DATABASE contravento TO contravento_user;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'ContraVento database initialized successfully';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pgcrypto';
    RAISE NOTICE 'Next step: Run Alembic migrations to create tables';
END $$;
