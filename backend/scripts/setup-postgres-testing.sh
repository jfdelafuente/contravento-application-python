#!/bin/bash

# =============================================================================
# Setup PostgreSQL Testing Environment
# =============================================================================
# Quick script to set up minimal PostgreSQL testing environment
# Usage: bash scripts/setup-postgres-testing.sh

set -e  # Exit on error

echo "=========================================="
echo "ContraVento - PostgreSQL Testing Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if Docker is running
echo -e "${YELLOW}[1/7] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 2: Start PostgreSQL
echo -e "${YELLOW}[2/7] Starting PostgreSQL container...${NC}"
docker-compose up postgres -d
echo -e "${GREEN}✓ PostgreSQL container started${NC}"
echo ""

# Step 3: Wait for PostgreSQL to be healthy
echo -e "${YELLOW}[3/7] Waiting for PostgreSQL to be ready...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec contravento-db pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "  Waiting... ($attempt/$max_attempts)"
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}Error: PostgreSQL did not become ready in time${NC}"
    exit 1
fi
echo ""

# Step 4: Create test database and user
echo -e "${YELLOW}[4/7] Creating test database and user...${NC}"
docker exec contravento-db psql -U postgres -c "
    SELECT 'Database already exists' WHERE EXISTS (SELECT FROM pg_database WHERE datname = 'contravento_test')
    UNION ALL
    SELECT 'Creating database' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'contravento_test');
" > /dev/null 2>&1

docker exec contravento-db psql -U postgres <<-EOSQL > /dev/null 2>&1
    -- Create database if not exists
    SELECT 'CREATE DATABASE contravento_test'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'contravento_test')\gexec

    -- Create user if not exists
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'contravento_test') THEN
            CREATE USER contravento_test WITH PASSWORD 'test_password';
        END IF;
    END
    \$\$;

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE contravento_test TO contravento_test;
EOSQL

echo -e "${GREEN}✓ Database 'contravento_test' created${NC}"
echo -e "${GREEN}✓ User 'contravento_test' created${NC}"
echo ""

# Step 5: Apply migrations
echo -e "${YELLOW}[5/7] Applying database migrations...${NC}"
export DATABASE_URL="postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"

if command -v poetry &> /dev/null; then
    poetry run alembic upgrade head
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
else
    echo -e "${RED}Warning: Poetry not found. Please run migrations manually:${NC}"
    echo "  cd backend"
    echo "  poetry run alembic upgrade head"
fi
echo ""

# Step 6: Verify tables
echo -e "${YELLOW}[6/7] Verifying database tables...${NC}"
table_count=$(docker exec contravento-db psql -U contravento_test -d contravento_test -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null | xargs)

if [ "$table_count" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $table_count tables in database${NC}"
    echo ""
    echo "Tables created:"
    docker exec contravento-db psql -U contravento_test -d contravento_test -c "\dt" | grep "public"
else
    echo -e "${YELLOW}Warning: No tables found. Migrations may not have run.${NC}"
fi
echo ""

# Step 7: Summary
echo -e "${GREEN}=========================================="
echo "✓ PostgreSQL Testing Environment Ready!"
echo "==========================================${NC}"
echo ""
echo "Connection details:"
echo "  Host:     localhost"
echo "  Port:     5432"
echo "  Database: contravento_test"
echo "  User:     contravento_test"
echo "  Password: test_password"
echo ""
echo "DATABASE_URL:"
echo "  postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"
echo ""
echo "Next steps:"
echo "  1. Start backend:"
echo "     cd backend"
echo "     poetry run uvicorn src.main:app --reload --port 8000"
echo ""
echo "  2. Run tests:"
echo "     poetry run pytest"
echo ""
echo "  3. Connect to database:"
echo "     docker exec -it contravento-db psql -U contravento_test -d contravento_test"
echo ""
echo "  4. View logs:"
echo "     docker-compose logs -f postgres"
echo ""
echo "  5. Stop PostgreSQL:"
echo "     docker-compose down"
echo ""
echo "  6. Clean up (delete all data):"
echo "     docker-compose down -v"
echo ""
