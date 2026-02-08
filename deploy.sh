#!/bin/bash
# ============================================================================
# ContraVento - Multi-Environment Deployment Script
# ============================================================================
# 📖 Documentation: docs/deployment/README.md
#    Complete guide with decision tree, troubleshooting, and mode details
#
# Simplified deployment for all environments:
#   ./deploy.sh local                   - Start local development
#   ./deploy.sh local --with-frontend   - Start local + frontend
#   ./deploy.sh local --rebuild         - Force rebuild (ignore cache)
#   ./deploy.sh dev                     - Start development/integration
#   ./deploy.sh staging                 - Start staging/pre-production
#   ./deploy.sh prod                    - Start production
#
# Additional commands:
#   ./deploy.sh <env> down  - Stop environment
#   ./deploy.sh <env> logs  - View logs
#   ./deploy.sh <env> ps    - View running containers
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# Check if docker-compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found. Please install Docker Compose."
        exit 1
    fi
}

# Validate environment
validate_env() {
    local env=$1
    case $env in
        local|local-minimal|dev|staging|prod)
            return 0
            ;;
        *)
            print_error "Invalid environment: $env"
            echo "Valid environments: local, local-minimal, dev, staging, prod"
            exit 1
            ;;
    esac
}

# Check if .env file exists
check_env_file() {
    local env=$1
    local env_file=".env.${env}"

    if [ ! -f "$env_file" ]; then
        print_warning ".env file not found: $env_file"
        print_info "Creating from example file..."

        if [ -f "${env_file}.example" ]; then
            cp "${env_file}.example" "$env_file"

            # Auto-generate SECRET_KEY for local/local-minimal environments only
            if [ "$env" = "local" ] || [ "$env" = "local-minimal" ]; then
                print_info "Auto-generating SECRET_KEY for local development..."

                # Generate a random SECRET_KEY using Python
                if command -v python3 &> /dev/null; then
                    local secret_key=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || echo "")
                elif command -v python &> /dev/null; then
                    local secret_key=$(python -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || echo "")
                else
                    print_warning "Python not found, using default SECRET_KEY"
                    local secret_key=""
                fi

                # Replace SECRET_KEY in .env file if generated successfully
                if [ -n "$secret_key" ]; then
                    if [[ "$OSTYPE" == "darwin"* ]]; then
                        # macOS
                        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=${secret_key}/" "$env_file"
                    else
                        # Linux
                        sed -i "s/SECRET_KEY=.*/SECRET_KEY=${secret_key}/" "$env_file"
                    fi
                    print_success "Auto-generated SECRET_KEY for local development"
                fi

                print_success "Created $env_file with auto-generated SECRET_KEY"
            else
                # For staging/prod, require manual configuration
                print_warning "⚠️  IMPORTANT: Edit $env_file and configure all variables!"
                print_warning "⚠️  Generate strong SECRET_KEY with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                print_warning "⚠️  Press Ctrl+C to abort, or Enter to continue with example values (NOT RECOMMENDED)"
                read -p ""
            fi
        else
            print_error "Example file not found: ${env_file}.example"
            exit 1
        fi
    fi
}

# Start environment
start_env() {
    local env=$1
    local with_frontend=$2  # --with-frontend flag
    local rebuild=$3        # --rebuild flag
    local compose_file="docker-compose.${env}.yml"

    print_header "Starting $env environment"

    check_env_file "$env"

    print_info "Using configuration:"
    echo "  - Base: docker-compose.yml"
    echo "  - Overlay: $compose_file"
    echo "  - Env file: .env.${env}"
    if [ "$with_frontend" = "true" ]; then
        echo "  - Frontend: ENABLED (Vite dev server)"
    fi
    echo ""

    # Confirmation for production
    if [ "$env" = "prod" ]; then
        print_warning "⚠️  You are about to deploy to PRODUCTION!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            print_info "Deployment cancelled"
            exit 0
        fi
    fi

    # Build frontend for staging/prod environments
    if [ "$env" = "staging" ] || [ "$env" = "prod" ]; then
        print_info "Building frontend for $env..."
        cd frontend

        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            print_warning "node_modules not found, running npm install..."
            npm install
        fi

        # Run production build
        if [ "$env" = "staging" ]; then
            npm run build:staging
        else
            npm run build:prod
        fi

        cd ..
        print_success "Frontend build complete!"
    fi

    # Pull latest images
    print_info "Pulling latest images..."
    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" pull

    # Build services
    if [ "$rebuild" = "true" ]; then
        print_info "Building services (--no-cache - forced rebuild)..."
        docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" build --no-cache
    else
        print_info "Building services..."
        docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" build
    fi

    # Start services (enable frontend if flag is set)
    print_info "Starting services..."
    if [ "$with_frontend" = "true" ]; then
        # Scale frontend to 1 replica to enable it
        docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" up -d --scale frontend=1
    else
        docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" up -d
    fi

    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 10

    # Show status
    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" ps

    print_success "$env environment started successfully!"

    # Get backend port (priority: env var > .env file > default 8000)
    local backend_port=${BACKEND_PORT:-}

    # If not set via environment variable, read from .env file
    if [ -z "$backend_port" ] && [ -f ".env.${env}" ]; then
        backend_port=$(grep "^BACKEND_PORT=" ".env.${env}" 2>/dev/null | cut -d'=' -f2 | tr -d ' "' || echo "")
    fi

    # Fallback to 8000 if still not set
    backend_port=${backend_port:-8000}

    # Environment-specific messages
    case $env in
        local-minimal)
            echo ""
            print_info "Access your minimal local environment:"
            echo "  Backend API:     http://localhost:${backend_port}"
            echo "  API Docs:        http://localhost:${backend_port}/docs"
            if [ "$with_frontend" = "true" ]; then
                echo "  Frontend:        http://localhost:5173"
            fi
            echo "  PostgreSQL:      localhost:5432 (use DBeaver, psql, etc.)"
            echo ""
            if [ "$with_frontend" = "true" ]; then
                print_info "Frontend + Backend + PostgreSQL running"
            else
                print_warning "ℹ️  Minimal setup (PostgreSQL + Backend only)"
                print_info "Add frontend with: ./deploy.sh local-minimal --with-frontend"
            fi
            print_info "For MailHog, Redis, pgAdmin → use: ./deploy.sh local"
            ;;
        local)
            echo ""
            print_info "Access your full local environment:"
            echo "  Backend API:     http://localhost:${backend_port}"
            echo "  API Docs:        http://localhost:${backend_port}/docs"
            if [ "$with_frontend" = "true" ]; then
                echo "  Frontend:        http://localhost:5173"
            fi
            echo "  MailHog UI:      http://localhost:8025"
            echo "  pgAdmin:         http://localhost:5050"
            echo "  PostgreSQL:      localhost:5432"
            echo "  Redis:           localhost:6379"
            echo ""
            if [ "$with_frontend" = "true" ]; then
                print_info "Frontend + Backend + All Services running"
            else
                print_warning "ℹ️  Full setup without frontend"
                print_info "Add frontend with: ./deploy.sh local --with-frontend"
            fi
            print_info "For lighter setup → use: ./deploy.sh local-minimal"
            ;;
        dev)
            echo ""
            print_info "Access your dev environment:"
            echo "  Backend API:     http://dev.contravento.local:${backend_port}"
            echo "  API Docs:        http://dev.contravento.local:${backend_port}/docs"
            ;;
        staging)
            echo ""
            print_info "Access your staging environment:"
            echo "  Backend API:     https://staging.contravento.com"
            echo "  Monitoring:      http://localhost:3000"
            ;;
        prod)
            echo ""
            print_success "Production deployment complete!"
            echo "  Backend API:     https://api.contravento.com"
            echo "  Monitoring:      https://monitoring.contravento.com"
            ;;
    esac

    echo ""
    print_info "View logs with: ./deploy.sh $env logs"
    print_info "Stop with: ./deploy.sh $env down"
}

# Stop environment
stop_env() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"

    print_header "Stopping $env environment"

    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" down

    print_success "$env environment stopped"
}

# View logs
view_logs() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"

    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" logs -f
}

# Show running containers
show_ps() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"

    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" ps
}

# Restart environment
restart_env() {
    local env=$1

    print_header "Restarting $env environment"

    stop_env "$env"
    sleep 2
    start_env "$env"
}

# Main
main() {
    check_docker_compose

    if [ $# -eq 0 ]; then
        print_error "Usage: $0 <environment> [command]"
        echo ""
        echo "Environments:"
        echo "  local-minimal  - Minimal local (PostgreSQL + Backend only) ⚡ FASTEST"
        echo "  local          - Full local (+ Redis, MailHog, pgAdmin)"
        echo "  dev            - Development/Integration (production-like)"
        echo "  staging        - Staging/Pre-production (production mirror)"
        echo "  prod           - Production (maximum security)"
        echo ""
        echo "Commands:"
        echo "  (default)      - Start environment"
        echo "  --with-frontend - Start with frontend (local-minimal and local only)"
        echo "  --rebuild      - Force rebuild images (ignore cache)"
        echo "  down           - Stop environment"
        echo "  logs           - View logs (follow mode)"
        echo "  ps             - Show running containers"
        echo "  restart        - Restart environment"
        echo ""
        echo "Examples:"
        echo "  $0 local-minimal                   # Start minimal local (backend only)"
        echo "  $0 local-minimal --with-frontend   # Start minimal local + frontend"
        echo "  $0 local --rebuild                 # Force rebuild all images"
        echo "  $0 local                           # Start full local with all tools"
        echo "  $0 local-minimal logs              # View logs"
        echo "  $0 prod down                       # Stop production"
        exit 1
    fi

    # Parse arguments
    local env=$1
    local with_frontend=false
    local rebuild=false
    local command="up"

    # Check for flags in any position
    shift  # Remove first argument (env)
    for arg in "$@"; do
        case "$arg" in
            --with-frontend)
                with_frontend=true
                ;;
            --rebuild)
                rebuild=true
                ;;
            up|start|down|stop|logs|ps|status|restart)
                command="$arg"
                ;;
        esac
    done

    validate_env "$env"

    case $command in
        up|start)
            start_env "$env" "$with_frontend" "$rebuild"
            ;;
        down|stop)
            stop_env "$env"
            ;;
        logs)
            view_logs "$env"
            ;;
        ps|status)
            show_ps "$env"
            ;;
        restart)
            restart_env "$env"
            ;;
        *)
            print_error "Invalid command: $command"
            echo "Valid commands: up, down, logs, ps, restart"
            exit 1
            ;;
    esac
}

main "$@"
