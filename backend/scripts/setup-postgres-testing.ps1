# =============================================================================
# Setup PostgreSQL Testing Environment (PowerShell version)
# =============================================================================
# Quick script to set up minimal PostgreSQL testing environment for Windows
# Usage: .\scripts\setup-postgres-testing.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ContraVento - PostgreSQL Testing Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Docker is running
Write-Host "[1/7] Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Start PostgreSQL
Write-Host "[2/7] Starting PostgreSQL container..." -ForegroundColor Yellow
docker-compose up postgres -d
Write-Host "✓ PostgreSQL container started" -ForegroundColor Green
Write-Host ""

# Step 3: Wait for PostgreSQL to be healthy
Write-Host "[3/7] Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts) {
    try {
        docker exec contravento-db pg_isready -U postgres 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green
            $ready = $true
            break
        }
    }
    catch {
        # Continue waiting
    }

    $attempt++
    Write-Host "  Waiting... ($attempt/$maxAttempts)"
    Start-Sleep -Seconds 1
}

if (-not $ready) {
    Write-Host "Error: PostgreSQL did not become ready in time" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Create test database and user
Write-Host "[4/7] Creating test database and user..." -ForegroundColor Yellow

$sqlCommands = @"
-- Create database if not exists
SELECT 'CREATE DATABASE contravento_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'contravento_test')\gexec

-- Create user if not exists
DO `$`$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'contravento_test') THEN
        CREATE USER contravento_test WITH PASSWORD 'test_password';
    END IF;
END
`$`$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE contravento_test TO contravento_test;
"@

$sqlCommands | docker exec -i contravento-db psql -U postgres 2>&1 | Out-Null

Write-Host "✓ Database 'contravento_test' created" -ForegroundColor Green
Write-Host "✓ User 'contravento_test' created" -ForegroundColor Green
Write-Host ""

# Step 5: Apply migrations
Write-Host "[5/7] Applying database migrations..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"

if (Get-Command poetry -ErrorAction SilentlyContinue) {
    try {
        Set-Location backend
        poetry run alembic upgrade head
        Set-Location ..
        Write-Host "✓ Migrations applied successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Error applying migrations. Please run manually:" -ForegroundColor Yellow
        Write-Host "  cd backend"
        Write-Host "  poetry run alembic upgrade head"
    }
}
else {
    Write-Host "Warning: Poetry not found. Please run migrations manually:" -ForegroundColor Yellow
    Write-Host "  cd backend"
    Write-Host "  poetry run alembic upgrade head"
}
Write-Host ""

# Step 6: Verify tables
Write-Host "[6/7] Verifying database tables..." -ForegroundColor Yellow
try {
    $tableCountOutput = docker exec contravento-db psql -U contravento_test -d contravento_test -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>&1
    $tableCount = [int]($tableCountOutput -replace '\s+', '')

    if ($tableCount -gt 0) {
        Write-Host "✓ Found $tableCount tables in database" -ForegroundColor Green
        Write-Host ""
        Write-Host "Tables created:"
        docker exec contravento-db psql -U contravento_test -d contravento_test -c "\dt"
    }
    else {
        Write-Host "Warning: No tables found. Migrations may not have run." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Warning: Could not verify tables" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Summary
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✓ PostgreSQL Testing Environment Ready!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Connection details:"
Write-Host "  Host:     localhost"
Write-Host "  Port:     5432"
Write-Host "  Database: contravento_test"
Write-Host "  User:     contravento_test"
Write-Host "  Password: test_password"
Write-Host ""
Write-Host "DATABASE_URL:"
Write-Host "  postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Start backend:"
Write-Host "     cd backend"
Write-Host "     poetry run uvicorn src.main:app --reload --port 8000"
Write-Host ""
Write-Host "  2. Run tests:"
Write-Host "     poetry run pytest"
Write-Host ""
Write-Host "  3. Connect to database:"
Write-Host "     docker exec -it contravento-db psql -U contravento_test -d contravento_test"
Write-Host ""
Write-Host "  4. View logs:"
Write-Host "     docker-compose logs -f postgres"
Write-Host ""
Write-Host "  5. Stop PostgreSQL:"
Write-Host "     docker-compose down"
Write-Host ""
Write-Host "  6. Clean up (delete all data):"
Write-Host "     docker-compose down -v"
Write-Host ""
