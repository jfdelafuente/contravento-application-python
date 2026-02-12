#!/usr/bin/env bash
# ============================================================================
# ContraVento - Preproduction Environment Helper Script
# ============================================================================
# Quick commands for managing the preproduction/Jenkins environment
#
# Usage:
#   ./run-jenkins-env.sh [command]
#
# Commands:
#   start     - Start all services
#   stop      - Stop all services
#   restart   - Restart all services
#   logs      - View all logs
#   status    - Check services status
#   pull      - Pull latest images from Docker Hub
#   clean     - Stop and remove volumes
#   help      - Show this help message
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Compose file
COMPOSE_FILE="docker-compose.preproduction.dev.yml"

# Functions
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Command implementations
cmd_start() {
    print_header "Starting Preproduction Environment"

    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    print_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d

    print_info "Waiting for services to be healthy (30s)..."
    sleep 30

    print_success "Services started successfully!"
    echo ""
    print_info "Access URLs:"
    echo "  - Frontend:  http://localhost:5173"
    echo "  - Backend:   http://localhost:8000"
    echo "  - API Docs:  http://localhost:8000/docs"
    echo "  - pgAdmin:   http://localhost:5050 (admin@example.com / jenkins)"
    echo ""
    print_info "Database:"
    echo "  - Host:      localhost:5432"
    echo "  - Database:  contravento_jenkins"
    echo "  - User:      postgres"
    echo "  - Password:  jenkins_test_password"
    echo ""
    print_warning "This environment uses PRE-BUILT images from Docker Hub"
    print_info "To update images, run: ./run-jenkins-env.sh pull"
}

cmd_stop() {
    print_header "Stopping Preproduction Environment"
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Services stopped"
}

cmd_restart() {
    print_header "Restarting Preproduction Environment"
    cmd_stop
    echo ""
    cmd_start
}

cmd_logs() {
    print_header "Viewing Service Logs"
    print_info "Press Ctrl+C to exit"
    echo ""
    docker-compose -f "$COMPOSE_FILE" logs -f
}

cmd_status() {
    print_header "Service Status"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    print_info "Health checks:"

    # Backend health check
    if docker-compose -f "$COMPOSE_FILE" exec -T backend curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend healthy"
    else
        print_error "Backend unhealthy"
    fi

    # Frontend check (nginx doesn't have curl, just check if container is running)
    if docker-compose -f "$COMPOSE_FILE" ps frontend | grep -q "Up"; then
        print_success "Frontend running"
    else
        print_error "Frontend not running"
    fi

    # Database health check
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U postgres -d contravento_jenkins > /dev/null 2>&1; then
        print_success "Database healthy"
    else
        print_error "Database unhealthy"
    fi

    # pgAdmin check
    if docker-compose -f "$COMPOSE_FILE" ps pgadmin | grep -q "Up"; then
        print_success "pgAdmin running"
    else
        print_error "pgAdmin not running"
    fi
}

cmd_pull() {
    print_header "Pulling Latest Images from Docker Hub"

    print_info "Pulling backend image..."
    docker-compose -f "$COMPOSE_FILE" pull backend

    print_info "Pulling frontend image..."
    docker-compose -f "$COMPOSE_FILE" pull frontend

    print_success "Images updated successfully!"
    echo ""
    print_warning "To apply updates, restart the environment:"
    print_info "  ./run-jenkins-env.sh restart"
}

cmd_clean() {
    print_header "Cleaning Preproduction Environment"
    print_warning "This will remove all containers and volumes"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" down -v
        print_success "Environment cleaned"
    else
        print_info "Cancelled"
    fi
}

cmd_help() {
    cat << EOF
ContraVento - Preproduction Environment Helper

Usage:
  ./run-jenkins-env.sh [command]

Commands:
  start     - Start all services (postgres, backend, frontend, pgadmin)
  stop      - Stop all services
  restart   - Restart all services
  logs      - View all logs (follow mode)
  status    - Check services status and health
  pull      - Pull latest images from Docker Hub
  clean     - Stop and remove all volumes
  help      - Show this help message

Examples:
  ./run-jenkins-env.sh start          # Start environment
  ./run-jenkins-env.sh logs           # View logs
  ./run-jenkins-env.sh pull           # Update images
  ./run-jenkins-env.sh restart        # Restart with new images
  ./run-jenkins-env.sh clean          # Clean everything

Quick Workflow:
  1. ./run-jenkins-env.sh start       # Start services
  2. Test manually via browser
  3. ./run-jenkins-env.sh logs        # Check logs if needed
  4. ./run-jenkins-env.sh stop        # Stop services

Update Workflow:
  1. ./run-jenkins-env.sh pull        # Pull latest images from Docker Hub
  2. ./run-jenkins-env.sh restart     # Restart with new images

Access URLs:
  - Frontend:  http://localhost:5173
  - Backend:   http://localhost:8000
  - API Docs:  http://localhost:8000/docs
  - pgAdmin:   http://localhost:5050 (admin@example.com / jenkins)

Database Connection:
  - Host:      localhost:5432
  - Database:  contravento_jenkins
  - User:      postgres
  - Password:  jenkins_test_password

Notes:
  - This environment uses PRE-BUILT images from Docker Hub
  - Images are built by GitHub Actions or Jenkins
  - VITE_* variables are hardcoded at build-time (immutable)
  - For local development, use ./deploy.sh local instead
EOF
}

# Main
main() {
    case "${1:-help}" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        logs)
            cmd_logs
            ;;
        status)
            cmd_status
            ;;
        pull)
            cmd_pull
            ;;
        clean)
            cmd_clean
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
