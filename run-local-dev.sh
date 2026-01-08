#!/bin/bash
# ============================================================================
# ContraVento - Local Development Startup Script (SQLite - No Docker)
# ============================================================================
# Quick start development server with SQLite database
# No Docker required - instant startup!
#
# Usage:
#   ./run-local-dev.sh           # Start server
#   ./run-local-dev.sh --setup   # First-time setup
#   ./run-local-dev.sh --reset   # Reset database
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

# Check if we're in the project root
check_directory() {
    if [ ! -d "backend" ]; then
        print_error "Must run from project root directory"
        exit 1
    fi
}

# Check if poetry is installed
check_poetry() {
    if ! command -v poetry &> /dev/null; then
        print_error "Poetry not found. Install with: pip install poetry"
        exit 1
    fi
}

# Setup environment
setup() {
    print_header "First-Time Setup"

    cd backend

    # Check if .env exists
    if [ -f ".env" ]; then
        print_warning ".env already exists"
        read -p "Overwrite with .env.dev.example? (y/N): " confirm
        if [ "$confirm" != "y" ]; then
            print_info "Keeping existing .env"
        else
            cp .env.dev.example .env
            print_success "Created .env from template"
        fi
    else
        cp .env.dev.example .env
        print_success "Created .env from template"
    fi

    # Install dependencies
    print_info "Installing dependencies with Poetry..."
    poetry install

    # Generate SECRET_KEY
    print_info "Generating SECRET_KEY..."
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

    # Update .env with generated key (cross-platform sed)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi

    print_success "Generated and saved SECRET_KEY"

    # Run migrations
    print_info "Running database migrations..."
    poetry run alembic upgrade head
    print_success "Database ready!"

    # Create test user
    print_info "Creating test user..."
    poetry run python scripts/create_verified_user.py || true

    # Load achievements
    print_info "Loading achievements..."
    poetry run python scripts/seed_achievements.py || true

    cd ..

    print_success "Setup complete!"
    echo ""
    print_info "Start development server with: ./run-local-dev.sh"
}

# Reset database
reset_db() {
    print_header "Reset Database"

    cd backend

    if [ -f "contravento_dev.db" ]; then
        print_warning "This will delete all data!"
        read -p "Continue? (y/N): " confirm
        if [ "$confirm" != "y" ]; then
            print_info "Reset cancelled"
            cd ..
            exit 0
        fi

        rm contravento_dev.db
        print_success "Deleted database file"
    else
        print_info "Database file not found (already clean)"
    fi

    # Recreate database
    print_info "Running migrations..."
    poetry run alembic upgrade head
    print_success "Database recreated!"

    # Create test user
    print_info "Creating test user..."
    poetry run python scripts/create_verified_user.py || true

    # Load achievements
    print_info "Loading achievements..."
    poetry run python scripts/seed_achievements.py || true

    cd ..

    print_success "Database reset complete!"
}

# Start server
start_server() {
    print_header "Starting Local Development Server"

    cd backend

    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_error ".env not found!"
        print_info "Run: ./run-local-dev.sh --setup"
        cd ..
        exit 1
    fi

    # Check if database exists
    if [ ! -f "contravento_dev.db" ]; then
        print_warning "Database not found. Running migrations..."
        poetry run alembic upgrade head
        print_success "Database created!"
    fi

    print_success "Starting server at http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"
    print_info "Press Ctrl+C to stop"
    echo ""

    # Start uvicorn with hot reload
    poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
}

# Main
main() {
    check_directory
    check_poetry

    case "${1:-start}" in
        --setup|setup)
            setup
            ;;
        --reset|reset)
            reset_db
            ;;
        --help|help|-h)
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  (none)     Start development server (default)"
            echo "  --setup    First-time setup (install deps, create .env, run migrations)"
            echo "  --reset    Reset database (delete and recreate)"
            echo "  --help     Show this help"
            echo ""
            echo "Examples:"
            echo "  $0              # Start server"
            echo "  $0 --setup      # Initial setup"
            echo "  $0 --reset      # Reset DB"
            ;;
        start|*)
            start_server
            ;;
    esac
}

main "$@"
