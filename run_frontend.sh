#!/bin/bash
# ============================================================================
# ContraVento - Frontend Server Manager
# ============================================================================
# Manages the Vite frontend server (port 5173)
#
# Usage:
#   ./run_frontend.sh          # Start frontend server (default)
#   ./run_frontend.sh start    # Start frontend server
#   ./run_frontend.sh stop     # Stop frontend server
#   ./run_frontend.sh restart  # Restart frontend server
#   ./run_frontend.sh verify   # Check frontend status
# ============================================================================

set -e

PORT=5173
SERVER_NAME="Frontend"
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
        echo -e "\033[34m[INFO] Run: ./run_frontend.sh stop\033[0m"
        exit 1
    fi

    # Check if we're in project root
    if [ ! -d "frontend" ]; then
        echo -e "\033[31m[ERROR] Must run from project root directory\033[0m"
        exit 1
    fi

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo -e "\033[31m[ERROR] Node.js not found. Install from: https://nodejs.org/\033[0m"
        exit 1
    fi

    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo -e "\033[31m[ERROR] npm not found. Install Node.js from: https://nodejs.org/\033[0m"
        exit 1
    fi

    cd frontend

    # Check if .env.development exists
    if [ ! -f ".env.development" ]; then
        if [ -f ".env.development.example" ]; then
            echo -e "\033[33m[WARNING] .env.development not found. Creating from example...\033[0m"
            cp .env.development.example .env.development
            echo -e "\033[32m[SUCCESS] Created .env.development\033[0m"
        else
            echo -e "\033[31m[ERROR] .env.development.example not found!\033[0m"
            cd ..
            exit 1
        fi
    fi

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "\033[33m[WARNING] node_modules not found. Running npm install...\033[0m"
        npm install
        echo -e "\033[32m[SUCCESS] Dependencies installed!\033[0m"
    fi

    echo -e "\033[32m[SUCCESS] Starting frontend at http://localhost:$PORT\033[0m"
    echo -e "\033[37m[INFO] Press Ctrl+C to stop\033[0m"
    echo ""

    # Start server in foreground
    npm run dev

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

        # Try HTTP check
        echo ""
        echo -n "HTTP check: "
        if command -v curl &> /dev/null; then
            http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:$PORT 2>/dev/null)
            if [ "$http_code" = "200" ]; then
                echo -e "\033[32mOK (HTTP $http_code)\033[0m"
            else
                echo -e "\033[33mTIMEOUT (Vite dev server doesn't respond to simple GET)\033[0m"
            fi
        else
            echo -e "\033[33mSKIPPED (curl not found)\033[0m"
        fi

        # Check config
        echo ""
        echo -n "Config: "
        if [ -f "frontend/.env.development" ]; then
            echo -e "\033[32mEXISTS (.env.development)\033[0m"
        else
            echo -e "\033[33mMISSING (.env.development)\033[0m"
        fi

        # Check node_modules
        echo -n "Dependencies: "
        if [ -d "frontend/node_modules" ]; then
            echo -e "\033[32mINSTALLED\033[0m"
        else
            echo -e "\033[33mNOT INSTALLED\033[0m"
        fi

        echo ""
        echo -e "\033[32m[SUCCESS] $SERVER_NAME is running!\033[0m"
    else
        echo -e "\033[31mNOT RUNNING\033[0m"
        echo ""
        echo -e "\033[34m[INFO] Start with: ./run_frontend.sh start\033[0m"
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
        echo "Usage: ./run_frontend.sh [start|stop|verify|restart]"
        echo "  Default: start"
        exit 1
        ;;
esac
