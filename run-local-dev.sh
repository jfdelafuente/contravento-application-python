#!/bin/bash
# ============================================================================
# ContraVento - Local Development Startup Script (SQLite - No Docker)
# ============================================================================
# Quick start development server with SQLite database
# No Docker required - instant startup!
#
# 📖 Documentation: docs/deployment/modes/local-dev.md
#    For complete guide with troubleshooting and configuration details
#
# Usage:
#   ./run-local-dev.sh                    # Start backend only
#   ./run-local-dev.sh --with-frontend    # Start backend + frontend
#   ./run-local-dev.sh --setup            # First-time setup
#   ./run-local-dev.sh --reset            # Reset database
#   ./run-local-dev.sh --verify           # Check server status
#   ./run-local-dev.sh --stop [target]    # Stop servers (all/backend/frontend)
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

# Verify server status
verify_servers() {
    print_header "Server Status Check"

    # Function to check if port is in use
    check_port() {
        local port=$1
        if command -v lsof &> /dev/null; then
            lsof -i:$port -sTCP:LISTEN -t &> /dev/null
        elif command -v netstat &> /dev/null; then
            netstat -tuln | grep ":$port " &> /dev/null
        else
            # Fallback: try to connect
            timeout 1 bash -c "cat < /dev/null > /dev/tcp/localhost/$port" 2>/dev/null
        fi
        return $?
    }

    # Function to test HTTP endpoint
    test_endpoint() {
        local url=$1
        local timeout=${2:-3}
        if command -v curl &> /dev/null; then
            curl -s -f --max-time $timeout "$url" &> /dev/null
            return $?
        elif command -v wget &> /dev/null; then
            wget -q -T $timeout -O /dev/null "$url" &> /dev/null
            return $?
        else
            print_warning "Neither curl nor wget found, skipping HTTP checks"
            return 1
        fi
    }

    # Get HTTP response
    get_http() {
        local url=$1
        if command -v curl &> /dev/null; then
            curl -s "$url" 2>/dev/null
        elif command -v wget &> /dev/null; then
            wget -q -O - "$url" 2>/dev/null
        fi
    }

    # Check Backend (port 8000)
    echo -e "${BLUE}Backend Server (http://localhost:8000)${NC}"
    echo -n "  Port 8000: "
    if check_port 8000; then
        echo -e "${GREEN}LISTENING${NC}"

        echo -n "  Health check: "
        if test_endpoint "http://localhost:8000/health"; then
            echo -e "${GREEN}OK${NC}"

            # Parse health response
            health_data=$(get_http "http://localhost:8000/health")
            if [ -n "$health_data" ] && command -v jq &> /dev/null; then
                status=$(echo "$health_data" | jq -r '.data.status' 2>/dev/null)
                environment=$(echo "$health_data" | jq -r '.data.environment' 2>/dev/null)
                timestamp=$(echo "$health_data" | jq -r '.data.timestamp' 2>/dev/null)
                echo "    Status: ${GREEN}$status${NC}"
                echo -e "    Environment: ${BLUE}$environment${NC}"
                echo -e "    Timestamp: \033[0;37m$timestamp${NC}"
            elif [ -n "$health_data" ]; then
                echo -e "    ${YELLOW}(Install jq for detailed health info)${NC}"
            fi
        else
            echo -e "${RED}FAILED${NC}"
        fi

        echo -n "  API Docs: "
        if test_endpoint "http://localhost:8000/docs"; then
            echo -e "${GREEN}AVAILABLE${NC}"
        else
            echo -e "${YELLOW}NOT AVAILABLE${NC}"
        fi

        echo -n "  Database: "
        if [ -f "backend/contravento_dev.db" ]; then
            db_size=$(du -h backend/contravento_dev.db | cut -f1)
            echo -e "${GREEN}EXISTS ($db_size)${NC}"
        else
            echo -e "${YELLOW}NOT FOUND${NC}"
        fi
    else
        echo -e "${RED}NOT RUNNING${NC}"
        echo -e "    \033[0;37mStart with: ./run-local-dev.sh${NC}"
    fi

    echo ""

    # Check Frontend (port 5173)
    echo -e "${BLUE}Frontend Server (http://localhost:5173)${NC}"
    echo -n "  Port 5173: "
    if check_port 5173; then
        echo -e "${GREEN}LISTENING${NC}"

        echo -n "  HTTP check: "
        if test_endpoint "http://localhost:5173"; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${RED}FAILED${NC}"
        fi

        echo -n "  Config: "
        if [ -f "frontend/.env.development" ]; then
            echo -e "${GREEN}EXISTS${NC}"
        else
            echo -e "${YELLOW}MISSING (.env.development)${NC}"
        fi

        echo -n "  node_modules: "
        if [ -d "frontend/node_modules" ]; then
            echo -e "${GREEN}EXISTS${NC}"
        else
            echo -e "${YELLOW}NOT INSTALLED${NC}"
        fi
    else
        echo -e "${RED}NOT RUNNING${NC}"
        echo -e "    \033[0;37mStart with: ./run-local-dev.sh --with-frontend${NC}"
        echo -e "    \033[0;37mOr manually: cd frontend && npm run dev${NC}"
    fi

    echo ""

    # Summary
    echo -e "${BLUE}Summary:${NC}"
    echo -n "  Backend:  "
    if check_port 8000; then
        echo -e "${GREEN}RUNNING${NC}"
        backend_running=true
    else
        echo -e "${RED}STOPPED${NC}"
        backend_running=false
    fi

    echo -n "  Frontend: "
    if check_port 5173; then
        echo -e "${GREEN}RUNNING${NC}"
        frontend_running=true
    else
        echo -e "${RED}STOPPED${NC}"
        frontend_running=false
    fi

    echo ""

    # Exit with appropriate message
    if $backend_running && $frontend_running; then
        print_success "Both servers are running!"
    elif $backend_running || $frontend_running; then
        print_warning "Only one server is running"
    else
        print_info "No servers are currently running"
    fi
}

# Stop servers
stop_servers() {
    local target=${1:-all}

    # Normalize target
    target=$(echo "$target" | tr '[:upper:]' '[:lower:]')

    # Validate target
    if [[ ! "$target" =~ ^(all|backend|frontend)$ ]]; then
        print_error "Invalid target: $1"
        print_info "Valid targets: all, backend, frontend"
        exit 1
    fi

    print_header "Stop Servers"

    # Function to check if port is in use
    check_port() {
        local port=$1
        if command -v lsof &> /dev/null; then
            lsof -i:$port -sTCP:LISTEN -t &> /dev/null
        elif command -v netstat &> /dev/null; then
            netstat -tuln | grep ":$port " &> /dev/null
        else
            timeout 1 bash -c "cat < /dev/null > /dev/tcp/localhost/$port" 2>/dev/null
        fi
        return $?
    }

    # Function to stop process on port
    stop_process_on_port() {
        local port=$1
        local server_name=$2

        if check_port $port; then
            local pid=""

            # Get PID using available tools
            if command -v lsof &> /dev/null; then
                pid=$(lsof -i:$port -sTCP:LISTEN -t 2>/dev/null | head -1)
            elif command -v netstat &> /dev/null && command -v awk &> /dev/null; then
                # Try to extract PID from netstat (works on Linux)
                pid=$(netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1)
            fi

            if [ -n "$pid" ]; then
                if kill -9 $pid 2>/dev/null; then
                    # Wait a bit and verify
                    sleep 0.5

                    if ! check_port $port; then
                        print_success "$server_name stopped (port $port)"
                        return 0
                    else
                        print_warning "$server_name may still be running on port $port"
                        return 1
                    fi
                else
                    print_error "Failed to stop $server_name on port $port (PID: $pid)"
                    return 1
                fi
            else
                print_warning "Could not find PID for $server_name on port $port"
                print_info "Try manually: lsof -i:$port -sTCP:LISTEN | grep LISTEN | awk '{print \$2}' | xargs kill -9"
                return 1
            fi
        else
            print_info "$server_name is not running on port $port"
            return 0
        fi
    }

    # Stop servers based on target
    backend_stopped=true
    frontend_stopped=true

    if [[ "$target" == "all" || "$target" == "backend" ]]; then
        echo -e "${BLUE}Stopping backend server...${NC}"
        if stop_process_on_port 8000 "Backend"; then
            backend_stopped=true
        else
            backend_stopped=false
        fi
        echo ""
    fi

    if [[ "$target" == "all" || "$target" == "frontend" ]]; then
        echo -e "${BLUE}Stopping frontend server...${NC}"
        if stop_process_on_port 5173 "Frontend"; then
            frontend_stopped=true
        else
            frontend_stopped=false
        fi
        echo ""
    fi

    # Summary
    echo -e "${BLUE}Summary:${NC}"

    if [[ "$target" == "all" || "$target" == "backend" ]]; then
        echo -n "  Backend:  "
        if $backend_stopped; then
            echo -e "${GREEN}STOPPED${NC}"
        else
            echo -e "${RED}FAILED${NC}"
        fi
    fi

    if [[ "$target" == "all" || "$target" == "frontend" ]]; then
        echo -n "  Frontend: "
        if $frontend_stopped; then
            echo -e "${GREEN}STOPPED${NC}"
        else
            echo -e "${RED}FAILED${NC}"
        fi
    fi

    echo ""

    # Exit with appropriate code
    if $backend_stopped && $frontend_stopped; then
        print_success "All requested servers stopped!"
        exit 0
    else
        print_warning "Some servers failed to stop"
        exit 1
    fi
}

# Main
main() {
    check_directory
    check_poetry

    # Parse arguments
    WITH_FRONTEND=false
    COMMAND="start"
    STOP_TARGET=""

    # Process arguments
    prev_arg=""
    for arg in "$@"; do
        # Check if previous arg was --stop
        if [ "$prev_arg" = "--stop" ]; then
            STOP_TARGET="$arg"
            prev_arg=""
            continue
        fi

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
            --verify|verify)
                COMMAND="verify"
                ;;
            --stop|stop)
                COMMAND="stop"
                prev_arg="--stop"
                ;;
            --help|help|-h)
                COMMAND="help"
                ;;
            start)
                COMMAND="start"
                ;;
        esac
    done

    # If --stop was specified without target, default to "all"
    if [ "$COMMAND" = "stop" ] && [ -z "$STOP_TARGET" ]; then
        STOP_TARGET="all"
    fi

    case "$COMMAND" in
        setup)
            setup
            ;;
        reset)
            reset_db
            ;;
        verify)
            verify_servers
            ;;
        stop)
            stop_servers "$STOP_TARGET"
            ;;
        help)
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  (none)           Start backend only (default)"
            echo "  --with-frontend  Start backend + frontend together"
            echo "  --setup          First-time setup (install deps, create .env, run migrations)"
            echo "  --reset          Reset database (delete and recreate)"
            echo "  --verify         Check backend and frontend server status"
            echo "  --stop [target]  Stop running servers (all/backend/frontend, default: all)"
            echo "  --help           Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                        # Start backend only"
            echo "  $0 --with-frontend        # Start backend + frontend"
            echo "  $0 --setup                # Initial setup"
            echo "  $0 --reset                # Reset DB"
            echo "  $0 --verify               # Check server status"
            echo "  $0 --stop                 # Stop all servers"
            echo "  $0 --stop backend         # Stop backend only"
            echo "  $0 --stop frontend        # Stop frontend only"
            ;;
        start|*)
            start_server "$WITH_FRONTEND"
            ;;
    esac
}

main "$@"
