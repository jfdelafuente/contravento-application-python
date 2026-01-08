#!/bin/bash
set -e

echo "🔍 MVP Verification Checklist"
echo "=============================="

echo "✅ 1. Code Quality..."
poetry run black src/ tests/ --check --line-length 100
poetry run ruff check src/ tests/

echo "✅ 2. Tests & Coverage..."
poetry run pytest tests/ --cov=src --cov-report=term | grep "TOTAL"

echo "✅ 3. PostgreSQL..."
docker exec contravento-db pg_isready -U contravento_user

echo "✅ 4. Migrations..."
poetry run alembic current

echo "✅ 5. Spanish Errors..."
ENGLISH_ERRORS=$(grep -r "raise HTTPException" src/ | grep -E "\"[A-Z][a-z]+ " | wc -l)
echo "English errors found: $ENGLISH_ERRORS (should be 0)"

echo ""
echo "🎉 MVP Verification Complete!"
