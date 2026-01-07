#!/bin/bash
# ============================================================================
# ContraVento - Multi-Environment Deployment Script
# ============================================================================
# Simplified deployment for all environments:
#   ./deploy.sh local       - Start local development
#   ./deploy.sh dev         - Start development/integration
#   ./deploy.sh staging     - Start staging/pre-production
#   ./deploy.sh prod        - Start production
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
        local|dev|staging|prod)
            return 0
            ;;
        *)
            print_error "Invalid environment: $env"
            echo "Valid environments: local, dev, staging, prod"
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
            print_warning "⚠️  IMPORTANT: Edit $env_file and configure all variables!"
            print_warning "⚠️  Generate strong SECRET_KEY with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            read -p "Press Enter after configuring $env_file to continue..."
        else
            print_error "Example file not found: ${env_file}.example"
            exit 1
        fi
    fi
}

# Start environment
start_env() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"

    print_header "Starting $env environment"

    check_env_file "$env"

    print_info "Using configuration:"
    echo "  - Base: docker-compose.yml"
    echo "  - Overlay: $compose_file"
    echo "  - Env file: .env.${env}"
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

    # Pull latest images
    print_info "Pulling latest images..."
    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" pull

    # Build services
    print_info "Building services..."
    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" build

    # Start services
    print_info "Starting services..."
    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" up -d

    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 10

    # Show status
    docker-compose -f docker-compose.yml -f "$compose_file" --env-file ".env.${env}" ps

    print_success "$env environment started successfully!"

    # Environment-specific messages
    case $env in
        local)
            echo ""
            print_info "Access your local environment:"
            echo "  Backend API:     http://localhost:8000"
            echo "  API Docs:        http://localhost:8000/docs"
            echo "  MailHog UI:      http://localhost:8025"
            echo "  pgAdmin:         http://localhost:5050"
            ;;
        dev)
            echo ""
            print_info "Access your dev environment:"
            echo "  Backend API:     http://dev.contravento.local:8000"
            echo "  API Docs:        http://dev.contravento.local:8000/docs"
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
        echo "  local      - Local development (hot reload, MailHog, pgAdmin)"
        echo "  dev        - Development/Integration (production-like)"
        echo "  staging    - Staging/Pre-production (production mirror)"
        echo "  prod       - Production (maximum security)"
        echo ""
        echo "Commands:"
        echo "  (default)  - Start environment"
        echo "  down       - Stop environment"
        echo "  logs       - View logs (follow mode)"
        echo "  ps         - Show running containers"
        echo "  restart    - Restart environment"
        echo ""
        echo "Examples:"
        echo "  $0 local           # Start local development"
        echo "  $0 local logs      # View local logs"
        echo "  $0 prod down       # Stop production"
        exit 1
    fi

    local env=$1
    local command=${2:-up}

    validate_env "$env"

    case $command in
        up|start)
            start_env "$env"
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
