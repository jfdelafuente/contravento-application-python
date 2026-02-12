#!/bin/bash
# ============================================================================
# ContraVento - Backend Server Manager
# ============================================================================
# Manages the FastAPI backend server (port 8000)
#
# Usage:
#   ./run_backend.sh          # Start backend server (default)
#   ./run_backend.sh start    # Start backend server
#   ./run_backend.sh stop     # Stop backend server
#   ./run_backend.sh restart  # Restart backend server
#   ./run_backend.sh verify   # Check backend status
# ============================================================================

set -e

# Allow port configuration via environment variable
PORT=${BACKEND_PORT:-8000}
SERVER_NAME="Backend"
COMMAND="${1:-start}"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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

get_process_on_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        lsof -i:$port -sTCP:LISTEN -t 2>/dev/null | head -1
    elif command -v netstat &> /dev/null && command -v awk &> /dev/null; then
        netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1
    else
        echo ""
    fi
}

stop_server() {
    echo ""
    echo -e "\033[36mStopping $SERVER_NAME server (port $PORT)...\033[0m"

    if ! check_port $PORT; then
        echo -e "\033[33m[INFO] $SERVER_NAME is not running\033[0m"
        return 0
    fi

    local pid=$(get_process_on_port $PORT)
    if [ -z "$pid" ]; then
        echo -e "\033[33m[WARNING] Port $PORT is in use but cannot find process\033[0m"
        return 1
    fi

    if kill -9 $pid 2>/dev/null; then
        sleep 2
        if check_port $PORT; then
            echo -e "\033[31m[ERROR] Failed to stop $SERVER_NAME (PID: $pid)\033[0m"
            return 1
        else
            echo -e "\033[32m[SUCCESS] $SERVER_NAME stopped successfully\033[0m"
            return 0
        fi
    else
        echo -e "\033[31m[ERROR] Failed to kill process $pid\033[0m"
        return 1
    fi
}

start_server() {
    echo ""
    echo -e "\033[36mStarting $SERVER_NAME server...\033[0m"

    # Check if already running
    if check_port $PORT; then
        echo -e "\033[31m[ERROR] Port $PORT is already in use!\033[0m"
        echo -e "\033[34m[INFO] Run: ./run_backend.sh stop\033[0m"
        exit 1
    fi

    # Check if we're in project root
    if [ ! -d "backend" ]; then
        echo -e "\033[31m[ERROR] Must run from project root directory\033[0m"
        exit 1
    fi

    # Check if poetry is installed
    if ! command -v poetry &> /dev/null; then
        echo -e "\033[31m[ERROR] Poetry not found. Install with: pip install poetry\033[0m"
        exit 1
    fi

    cd backend

    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo -e "\033[31m[ERROR] .env not found!\033[0m"
        echo -e "\033[34m[INFO] Run: ./run-local-dev.sh --setup\033[0m"
        cd ..
        exit 1
    fi

    # Check if database exists
    if [ ! -f "contravento_dev.db" ]; then
        echo -e "\033[33m[WARNING] Database not found. Running migrations...\033[0m"
        poetry run alembic upgrade head
        echo -e "\033[32m[SUCCESS] Database created!\033[0m"
    fi

    echo -e "\033[32m[SUCCESS] Starting backend at http://localhost:$PORT\033[0m"
    echo -e "\033[34m[INFO] API Docs: http://localhost:$PORT/docs\033[0m"
    echo -e "\033[37m[INFO] Press Ctrl+C to stop\033[0m"
    echo ""

    # Start server in foreground
    poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port $PORT

    cd ..
}

verify_server() {
    echo ""
    echo -e "\033[34m============================================\033[0m"
    echo -e "\033[34m  $SERVER_NAME Server Status\033[0m"
    echo -e "\033[34m============================================\033[0m"
    echo ""

    echo -n "Port $PORT: "
    if check_port $PORT; then
        echo -e "\033[32mLISTENING\033[0m"

        # Try to get process info
        local pid=$(get_process_on_port $PORT)
        if [ -n "$pid" ]; then
            echo -e "\033[37m  Process: PID $pid\033[0m"
            if command -v ps &> /dev/null; then
                local proc_name=$(ps -p $pid -o comm= 2>/dev/null)
                echo -e "\033[37m  Name: $proc_name\033[0m"
            fi
        fi

        # Try health check
        echo ""
        echo -n "Health check: "
        if command -v curl &> /dev/null; then
            response=$(curl -s -w "\n%{http_code}" http://localhost:$PORT/health 2>/dev/null || echo "000")
            http_code=$(echo "$response" | tail -1)
            if [ "$http_code" = "200" ]; then
                echo -e "\033[32mOK (HTTP $http_code)\033[0m"
                body=$(echo "$response" | head -n -1)
                if command -v jq &> /dev/null; then
                    status=$(echo "$body" | jq -r '.status' 2>/dev/null)
                    env=$(echo "$body" | jq -r '.environment' 2>/dev/null)
                    echo -e "\033[37m  Status: $status\033[0m"
                    echo -e "\033[37m  Environment: $env\033[0m"
                fi
            else
                echo -e "\033[31mFAILED (HTTP $http_code)\033[0m"
            fi
        else
            echo -e "\033[33mSKIPPED (curl not found)\033[0m"
        fi

        # Check API docs
        echo ""
        echo -n "API Docs: "
        if command -v curl &> /dev/null; then
            http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/docs 2>/dev/null)
            if [ "$http_code" = "200" ]; then
                echo -e "\033[32mAVAILABLE (HTTP $http_code)\033[0m"
            else
                echo -e "\033[33mNOT AVAILABLE\033[0m"
            fi
        else
            echo -e "\033[33mSKIPPED (curl not found)\033[0m"
        fi

        # Check database
        echo ""
        echo -n "Database: "
        if [ -f "backend/contravento_dev.db" ]; then
            db_size=$(du -h "backend/contravento_dev.db" | cut -f1)
            echo -e "\033[32mEXISTS ($db_size)\033[0m"
        else
            echo -e "\033[33mNOT FOUND\033[0m"
        fi

        echo ""
        echo -e "\033[32m[SUCCESS] $SERVER_NAME is running!\033[0m"
    else
        echo -e "\033[31mNOT RUNNING\033[0m"
        echo ""
        echo -e "\033[34m[INFO] Start with: ./run_backend.sh start\033[0m"
    fi

    echo ""
}

restart_server() {
    echo ""
    echo -e "\033[36mRestarting $SERVER_NAME server...\033[0m"

    if stop_server; then
        sleep 1
        start_server
    else
        echo -e "\033[31m[ERROR] Cannot restart - failed to stop server\033[0m"
        exit 1
    fi
}

# ============================================================================
# MAIN
# ============================================================================

case "$COMMAND" in
    start)
        start_server
        ;;
    stop)
        stop_server
        echo ""
        ;;
    verify)
        verify_server
        ;;
    restart)
        restart_server
        ;;
    *)
        echo -e "\033[31m[ERROR] Invalid command: $COMMAND\033[0m"
        echo ""
        echo "Usage: ./run_backend.sh [start|stop|verify|restart]"
        echo "  Default: start"
        exit 1
        ;;
esac
