-- ContraVento Database Initialization Script
-- This script runs automatically when PostgreSQL container starts
-- Note: Alembic migrations will create all tables and relationships
--
-- IMPORTANT: This script uses environment variables from Docker:
--   - POSTGRES_DB: Database name (e.g., contravento, contravento_test, contravento_staging)
--   - POSTGRES_USER: Database user (e.g., contravento_user, contravento_test)
--
-- The database and user are automatically created by the postgres container
-- before this script runs.

-- Enable UUID extension (required for user_id, trip_id, etc.)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto extension (useful for additional security features)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set default timezone to UTC
SET timezone = 'UTC';

-- Note: GRANT is not needed here because the POSTGRES_USER automatically
-- has ALL PRIVILEGES on POSTGRES_DB when created by the container.
--
-- The following line would fail if database/user names differ from hardcoded values:
-- GRANT ALL PRIVILEGES ON DATABASE contravento TO contravento_user;
--
-- Instead, PostgreSQL container initialization handles this automatically:
--   docker-entrypoint.sh creates user with superuser privileges on the database

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'ContraVento database initialized';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pgcrypto';
    RAISE NOTICE 'Timezone: UTC';
    RAISE NOTICE 'Next step: Run Alembic migrations';
    RAISE NOTICE '===========================================';
END $$;
