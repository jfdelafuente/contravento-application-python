#!/usr/bin/env bash
# ============================================================================
# ContraVento - Jenkins CI/CD Environment Helper Script
# ============================================================================
# Quick commands for managing the Jenkins CI/CD environment
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
#   test      - Run all tests (backend + frontend)
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
COMPOSE_FILE="docker-compose-jenkins.yml"

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

# Command implementations
cmd_start() {
    print_header "Starting Jenkins CI/CD Environment"

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
    echo "  - pgAdmin:   http://localhost:5050 (admin@jenkins.local / jenkins)"
    echo ""
    print_info "Database:"
    echo "  - Host:      localhost:5432"
    echo "  - Database:  contravento_ci"
    echo "  - User:      postgres"
    echo "  - Password:  jenkins_test_password"
}

cmd_stop() {
    print_header "Stopping Jenkins CI/CD Environment"
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Services stopped"
}

cmd_restart() {
    print_header "Restarting Jenkins CI/CD Environment"
    cmd_stop
    cmd_start
}

cmd_logs() {
    print_header "Viewing Service Logs"
    print_info "Press Ctrl+C to exit"
    docker-compose -f "$COMPOSE_FILE" logs -f
}

cmd_status() {
    print_header "Service Status"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    print_info "Health checks:"
    docker-compose -f "$COMPOSE_FILE" exec backend curl -f http://localhost:8000/health 2>/dev/null && print_success "Backend healthy" || print_error "Backend unhealthy"
    docker-compose -f "$COMPOSE_FILE" exec frontend curl -f http://localhost:5173 2>/dev/null && print_success "Frontend healthy" || print_error "Frontend unhealthy"
    docker-compose -f "$COMPOSE_FILE" exec postgres pg_isready -U postgres -d contravento_ci 2>/dev/null && print_success "Database healthy" || print_error "Database unhealthy"
}

cmd_test() {
    print_header "Running All Tests"

    print_info "Running backend tests..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend pytest --cov=src --cov-report=term

    echo ""
    print_info "Running frontend tests..."
    docker-compose -f "$COMPOSE_FILE" exec -T frontend npm test

    print_success "All tests completed!"
}

cmd_clean() {
    print_header "Cleaning Jenkins CI/CD Environment"
    print_info "This will remove all containers and volumes"
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
ContraVento - Jenkins CI/CD Environment Helper

Usage:
  ./run-jenkins-env.sh [command]

Commands:
  start     - Start all services (postgres, backend, frontend, pgadmin)
  stop      - Stop all services
  restart   - Restart all services
  logs      - View all logs (follow mode)
  status    - Check services status and health
  test      - Run all tests (backend + frontend)
  clean     - Stop and remove all volumes
  help      - Show this help message

Examples:
  ./run-jenkins-env.sh start          # Start environment
  ./run-jenkins-env.sh logs           # View logs
  ./run-jenkins-env.sh test           # Run tests
  ./run-jenkins-env.sh clean          # Clean everything

Quick Testing Workflow:
  1. ./run-jenkins-env.sh start       # Start services
  2. ./run-jenkins-env.sh test        # Run tests
  3. ./run-jenkins-env.sh stop        # Stop services

Access URLs:
  - Frontend:  http://localhost:5173
  - Backend:   http://localhost:8000
  - API Docs:  http://localhost:8000/docs
  - pgAdmin:   http://localhost:5050 (admin@jenkins.local / jenkins)

Database Connection:
  - Host:      localhost:5432
  - Database:  contravento_ci
  - User:      postgres
  - Password:  jenkins_test_password
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
        test)
            cmd_test
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
