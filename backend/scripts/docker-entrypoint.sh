#!/bin/sh
# Docker entrypoint script for backend container
# Runs migrations and initializes dev data before starting the server

set -e

echo "🚀 Starting ContraVento Backend..."
echo ""

# Step 1: Run database migrations
echo "📦 Running Alembic migrations..."
alembic upgrade head
echo "✅ Migrations completed"
echo ""

# Step 2: Initialize development data (only in development/testing/ci)
if [ "$APP_ENV" = "development" ] || [ "$APP_ENV" = "testing" ] || [ "$APP_ENV" = "ci" ]; then
    echo "🌱 Initializing development data..."
    python scripts/init_dev_data.py
    echo ""
fi

# Step 3: Start the application
echo "🎯 Starting FastAPI server..."
echo "Environment: $APP_ENV"
echo "Debug mode: $DEBUG"
echo ""

# Execute the CMD from Dockerfile
exec "$@"
