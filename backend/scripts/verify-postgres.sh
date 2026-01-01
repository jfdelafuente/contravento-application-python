#!/bin/bash
# Verify PostgreSQL setup and run migrations
# Usage: bash scripts/verify-postgres.sh

set -e

echo "🔍 ContraVento - PostgreSQL Verification"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi
echo "✅ Docker is running"

# Check if postgres container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "contravento-db"; then
    echo "❌ PostgreSQL container not found."
    echo "   Run: docker-compose up -d postgres"
    exit 1
fi
echo "✅ PostgreSQL container exists"

# Check if postgres container is running
if ! docker ps --format '{{.Names}}' | grep -q "contravento-db"; then
    echo "⚠️  PostgreSQL container is stopped. Starting..."
    docker start contravento-db
    sleep 5
fi
echo "✅ PostgreSQL container is running"

# Check PostgreSQL connection
echo ""
echo "🔌 Testing PostgreSQL connection..."
if docker exec contravento-db pg_isready -U contravento_user -d contravento > /dev/null 2>&1; then
    echo "✅ PostgreSQL is accepting connections"
else
    echo "❌ PostgreSQL is not ready"
    exit 1
fi

# Check extensions
echo ""
echo "🔧 Checking PostgreSQL extensions..."
EXTENSIONS=$(docker exec contravento-db psql -U contravento_user -d contravento -t -c "SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pgcrypto');")
if echo "$EXTENSIONS" | grep -q "uuid-ossp"; then
    echo "✅ uuid-ossp extension enabled"
else
    echo "⚠️  uuid-ossp extension not found (will be created by init-db.sql)"
fi

# Show current tables
echo ""
echo "📊 Current database tables:"
docker exec contravento-db psql -U contravento_user -d contravento -c "\dt" 2>/dev/null || echo "   No tables yet (run migrations first)"

# Check Alembic current version
echo ""
echo "🗂️  Checking Alembic migration status..."
if poetry run alembic current 2>/dev/null | grep -q "head"; then
    echo "✅ Database is at HEAD revision"
    poetry run alembic current
else
    echo "⚠️  Database needs migrations"
    echo "   Current revision:"
    poetry run alembic current 2>/dev/null || echo "   No migrations applied yet"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PostgreSQL verification complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Run migrations: poetry run alembic upgrade head"
echo "   2. Seed achievements: poetry run python scripts/seed_achievements.py"
echo "   3. Create test user: poetry run python scripts/create_verified_user.py"
echo "   4. Start backend: poetry run uvicorn src.main:app --reload"
echo ""
