#!/bin/bash
# ============================================================================
# Deploy Local Production Build - ContraVento
# ============================================================================
# Script para probar el build de producción del frontend localmente
#
# Usa:
#   - Frontend: Dockerfile.prod (Nginx + archivos estáticos optimizados)
#   - Backend: Modo development con hot reload
#   - PostgreSQL, Redis, MailHog, pgAdmin
#
# Diferencias con ./deploy.sh local:
#   - Frontend sin hot reload (archivos estáticos)
#   - Nginx sirve en puerto 8080
#   - Proxy Nginx /api/* → backend:8000/*
#
# Uso:
#   ./deploy-local-prod.sh [comando] [flags]
#
# Comandos:
#   start   - Iniciar entorno (default)
#   stop    - Detener entorno
#   rebuild - Rebuild frontend (después de cambios)
#   logs    - Ver logs
#   clean   - Limpiar todo (contenedores + volúmenes)
#
# Flags (para start):
#   --rebuild - Forzar rebuild de todas las imágenes (ignora cache)
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    print_error ".env.local not found!"
    print_info "Creating from .env.local.example..."
    cp .env.local.example .env.local
    print_success ".env.local created"
fi

# Parse command and flags
COMMAND=${1:-start}
REBUILD_FLAG=false

# Check for flags in any position
for arg in "$@"; do
    case "$arg" in
        --rebuild)
            REBUILD_FLAG=true
            ;;
    esac
done

case $COMMAND in
    start)
        print_header "Starting Local Production Build"

        # Get backend port (priority: env var > .env.local > default 8000)
        backend_port=${BACKEND_PORT:-}
        port_source=""

        if [ -n "$backend_port" ]; then
            # Port set via environment variable
            port_source="environment variable"
        elif [ -f ".env.local" ]; then
            # Try to read from .env.local file
            backend_port=$(grep "^BACKEND_PORT=" ".env.local" 2>/dev/null | cut -d'=' -f2 | tr -d ' "' || echo "")
            if [ -n "$backend_port" ]; then
                port_source=".env.local"
            fi
        fi

        # Fallback to 8000 if still not set
        if [ -z "$backend_port" ]; then
            backend_port=8000
            port_source="default"
        fi

        # Build services
        if [ "$REBUILD_FLAG" = "true" ]; then
            print_info "Building all services (--no-cache - forced rebuild)..."
            docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local build --no-cache
        else
            print_info "Building frontend with production Dockerfile..."
            docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local build frontend
        fi

        print_info "Starting all services..."
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local up -d

        print_success "Local production build started!"
        echo ""
        print_info "Access your environment:"
        echo "  Frontend (Nginx):    http://localhost:8080"
        echo "  Backend API:         http://localhost:${backend_port} (port from: ${port_source})"
        echo "  API Docs:            http://localhost:${backend_port}/docs"
        echo "  MailHog UI:          http://localhost:8025"
        echo "  pgAdmin:             http://localhost:5050"
        echo ""
        print_warning "Frontend NO tiene hot reload (usa archivos estáticos)"
        print_info "Para cambios en frontend: ./deploy-local-prod.sh rebuild"
        ;;

    stop)
        print_header "Stopping Local Production Build"
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local down
        print_success "Services stopped"
        ;;

    rebuild)
        print_header "Rebuilding Frontend"

        print_info "Rebuilding frontend with production Dockerfile..."
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local build --no-cache frontend

        print_info "Restarting frontend..."
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local up -d frontend

        print_success "Frontend rebuilt and restarted"
        print_info "Access: http://localhost:8080"
        ;;

    logs)
        print_header "Showing Logs"
        docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local logs -f
        ;;

    clean)
        print_header "Cleaning Everything"

        print_warning "This will remove all containers and volumes!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local down -v
            print_success "Cleaned"
        else
            print_info "Cancelled"
        fi
        ;;

    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        echo "Available commands:"
        echo "  start   - Start environment (default)"
        echo "  stop    - Stop environment"
        echo "  rebuild - Rebuild frontend after changes"
        echo "  logs    - Show logs"
        echo "  clean   - Remove everything"
        echo ""
        echo "Flags (for start command):"
        echo "  --rebuild - Force rebuild all images (ignore cache)"
        echo ""
        echo "Examples:"
        echo "  ./deploy-local-prod.sh start"
        echo "  ./deploy-local-prod.sh start --rebuild"
        echo "  ./deploy-local-prod.sh rebuild"
        exit 1
        ;;
esac
