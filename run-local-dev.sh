#!/bin/bash
# ============================================================================
# ContraVento - Local Development Startup Script (SQLite - No Docker)
# ============================================================================
# Quick start development server with SQLite database
# No Docker required - instant startup!
#
# Usage:
#   ./run-local-dev.sh                    # Start backend only
#   ./run-local-dev.sh --with-frontend    # Start backend + frontend
#   ./run-local-dev.sh --setup            # First-time setup
#   ./run-local-dev.sh --reset            # Reset database
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

    # Create admin user
    print_info "Creating admin user..."
    poetry run python scripts/create_admin.py --force || true

    # Load achievements
    print_info "Loading achievements..."
    poetry run python scripts/seed_achievements.py || true

    # Load cycling types
    print_info "Loading cycling types..."
    poetry run python scripts/seed_cycling_types.py || true

    cd ..

    print_success "Setup complete!"
    echo ""
    print_info "Default credentials:"
    print_info "  Admin:  admin / AdminPass123!"
    print_info "  User:   testuser / TestPass123!"
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

    # Create admin user
    print_info "Creating admin user..."
    poetry run python scripts/create_admin.py --force || true

    # Load achievements
    print_info "Loading achievements..."
    poetry run python scripts/seed_achievements.py || true

    # Load cycling types
    print_info "Loading cycling types..."
    poetry run python scripts/seed_cycling_types.py || true

    cd ..

    print_success "Database reset complete!"
    echo ""
    print_info "Default credentials:"
    print_info "  Admin:  admin / AdminPass123!"
    print_info "  User:   testuser / TestPass123!"
}

# Check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Start server
start_server() {
    local with_frontend=$1

    if [ "$with_frontend" = "true" ]; then
        print_header "Starting Backend + Frontend (SQLite Local)"
    else
        print_header "Starting Backend Only (SQLite Local)"
    fi

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

    # Check if backend port is in use
    if check_port 8000; then
        print_error "Port 8000 is already in use!"
        print_info "Kill the process using port 8000:"
        print_info "  lsof -ti:8000 | xargs kill -9"
        cd ..
        exit 1
    fi

    print_success "Starting backend at http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"

    # Start uvicorn with hot reload in background
    poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!

    cd ..

    # Start frontend if requested
    if [ "$with_frontend" = "true" ]; then
        # Check if frontend port is in use
        if check_port 5173; then
            print_error "Port 5173 is already in use!"
            print_info "Kill the process using port 5173:"
            print_info "  lsof -ti:5173 | xargs kill -9"
            print_info "Stopping backend..."
            kill $BACKEND_PID
            exit 1
        fi

        # Check if Node.js is installed
        if ! command -v node &> /dev/null; then
            print_error "Node.js not found. Install from: https://nodejs.org/"
            print_info "Stopping backend..."
            kill $BACKEND_PID
            exit 1
        fi

        # Check if npm is installed
        if ! command -v npm &> /dev/null; then
            print_error "npm not found. Install Node.js from: https://nodejs.org/"
            print_info "Stopping backend..."
            kill $BACKEND_PID
            exit 1
        fi

        cd frontend

        # Check if .env.development exists, create from example if not
        if [ ! -f ".env.development" ]; then
            if [ -f ".env.development.example" ]; then
                print_warning ".env.development not found. Creating from .env.development.example..."
                cp .env.development.example .env.development
                print_success "Created .env.development with default values"
            else
                print_error ".env.development.example not found!"
                cd ..
                kill $BACKEND_PID
                exit 1
            fi
        fi

        # Check if node_modules exists
        if [ ! -d "node_modules" ]; then
            print_warning "node_modules not found. Running npm install..."
            npm install
            print_success "Dependencies installed!"
        fi

        print_success "Starting frontend at http://localhost:5173"
        print_info "Press Ctrl+C to stop both services"
        echo ""

        # Start Vite dev server
        npm run dev &
        FRONTEND_PID=$!

        cd ..

        # Setup cleanup trap to kill both processes on exit
        cleanup() {
            echo ""
            print_info "Stopping services..."
            kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
            print_success "Services stopped"
            exit 0
        }
        trap cleanup EXIT INT TERM

        # Wait for both processes
        wait
    else
        print_info "Press Ctrl+C to stop"
        echo ""

        # Setup cleanup trap for backend only
        cleanup() {
            echo ""
            print_info "Stopping backend..."
            kill $BACKEND_PID 2>/dev/null || true
            print_success "Backend stopped"
            exit 0
        }
        trap cleanup EXIT INT TERM

        # Wait for backend process
        wait $BACKEND_PID
    fi
}

# Main
main() {
    check_directory
    check_poetry

    # Parse arguments
    WITH_FRONTEND=false
    COMMAND="start"

    for arg in "$@"; do
        case "$arg" in
            --with-frontend)
                WITH_FRONTEND=true
                ;;
            --setup|setup)
                COMMAND="setup"
                ;;
            --reset|reset)
                COMMAND="reset"
                ;;
            --help|help|-h)
                COMMAND="help"
                ;;
            start)
                COMMAND="start"
                ;;
        esac
    done

    case "$COMMAND" in
        setup)
            setup
            ;;
        reset)
            reset_db
            ;;
        help)
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  (none)           Start backend only (default)"
            echo "  --with-frontend  Start backend + frontend together"
            echo "  --setup          First-time setup (install deps, create .env, run migrations)"
            echo "  --reset          Reset database (delete and recreate)"
            echo "  --help           Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                        # Start backend only"
            echo "  $0 --with-frontend        # Start backend + frontend"
            echo "  $0 --setup                # Initial setup"
            echo "  $0 --reset                # Reset DB"
            ;;
        start|*)
            start_server "$WITH_FRONTEND"
            ;;
    esac
}

main "$@"
