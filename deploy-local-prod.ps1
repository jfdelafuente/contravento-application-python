# ============================================================================
# Deploy Local Production Build - ContraVento (PowerShell)
# ============================================================================
# Script para probar el build de producción del frontend localmente
#
# Usa:
#   - Frontend: Dockerfile.prod (Nginx + archivos estáticos optimizados)
#   - Backend: Modo development con hot reload
#   - PostgreSQL, Redis, MailHog, pgAdmin
#
# Uso:
#   .\deploy-local-prod.ps1 [comando]
#
# Comandos:
#   start   - Iniciar entorno (default)
#   stop    - Detener entorno
#   rebuild - Rebuild frontend (después de cambios)
#   logs    - Ver logs
#   clean   - Limpiar todo (contenedores + volúmenes)
# ============================================================================

param(
    [string]$Command = "start"
)

# Colors
function Print-Info { Write-Host "ℹ️  $args" -ForegroundColor Blue }
function Print-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Print-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Print-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Print-Header {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  $args" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""
}

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Print-Error ".env.local not found!"
    Print-Info "Creating from .env.local.example..."
    Copy-Item .env.local.example .env.local
    Print-Success ".env.local created"
}

switch ($Command.ToLower()) {
    "start" {
        Print-Header "Starting Local Production Build"

        Print-Info "Building frontend with production Dockerfile..."
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local build frontend

        Print-Info "Starting all services..."
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local up -d

        Print-Success "Local production build started!"
        Write-Host ""
        Print-Info "Access your environment:"
        Write-Host "  Frontend (Nginx):    http://localhost:8080"
        Write-Host "  Backend API:         http://localhost:8000"
        Write-Host "  API Docs:            http://localhost:8000/docs"
        Write-Host "  MailHog UI:          http://localhost:8025"
        Write-Host "  pgAdmin:             http://localhost:5050"
        Write-Host ""
        Print-Warning "Frontend NO tiene hot reload (usa archivos estáticos)"
        Print-Info "Para cambios en frontend: .\deploy-local-prod.ps1 rebuild"
    }

    "stop" {
        Print-Header "Stopping Local Production Build"
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local down
        Print-Success "Services stopped"
    }

    "rebuild" {
        Print-Header "Rebuilding Frontend"

        Print-Info "Rebuilding frontend with production Dockerfile..."
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local build --no-cache frontend

        Print-Info "Restarting frontend..."
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local up -d frontend

        Print-Success "Frontend rebuilt and restarted"
        Print-Info "Access: http://localhost:8080"
    }

    "logs" {
        Print-Header "Showing Logs"
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local logs -f
    }

    "clean" {
        Print-Header "Cleaning Everything"

        Print-Warning "This will remove all containers and volumes!"
        $confirmation = Read-Host "Are you sure? (y/N)"
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local down -v
            Print-Success "Cleaned"
        } else {
            Print-Info "Cancelled"
        }
    }

    default {
        Print-Error "Unknown command: $Command"
        Write-Host ""
        Write-Host "Available commands:"
        Write-Host "  start   - Start environment (default)"
        Write-Host "  stop    - Stop environment"
        Write-Host "  rebuild - Rebuild frontend after changes"
        Write-Host "  logs    - Show logs"
        Write-Host "  clean   - Remove everything"
        exit 1
    }
}
