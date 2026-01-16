#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Performance Test Runner for ContraVento
#
# Runs benchmarks and load tests with various configurations.
#
# Usage:
#   ./scripts/run_performance_tests.sh benchmark       # Run pytest benchmarks
#   ./scripts/run_performance_tests.sh load            # Run Locust load test
#   ./scripts/run_performance_tests.sh load-heavy      # Run heavy load test
#   ./scripts/run_performance_tests.sh all             # Run all performance tests

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
BACKEND_DIR="backend"

# Helper functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_info() {
    echo -e "${YELLOW}ℹ  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_server() {
    print_info "Checking if backend server is running at $API_URL..."

    if curl -s "$API_URL/health" > /dev/null; then
        print_success "Backend server is running"
        return 0
    else
        print_error "Backend server is not running at $API_URL"
        echo ""
        echo "Please start the backend server first:"
        echo "  ./run_backend.sh  # or .\run_backend.ps1 on Windows"
        echo ""
        exit 1
    fi
}

run_benchmarks() {
    print_header "Running pytest Benchmarks"

    check_server

    cd "$BACKEND_DIR"

    print_info "Running API endpoint benchmarks..."
    poetry run pytest tests/performance/test_api_benchmarks.py \
        --benchmark-only \
        --benchmark-verbose \
        --benchmark-columns=min,max,mean,stddev,median,ops \
        -v

    print_success "Benchmarks completed!"

    # Optionally save results
    print_info "Saving benchmark results to benchmark-results.json..."
    poetry run pytest tests/performance/test_api_benchmarks.py \
        --benchmark-only \
        --benchmark-json=benchmark-results.json \
        -q

    cd ..
}

run_load_test() {
    print_header "Running Locust Load Test"

    check_server

    cd "$BACKEND_DIR"

    local users="${1:-50}"
    local spawn_rate="${2:-10}"
    local run_time="${3:-2m}"

    print_info "Load test configuration:"
    echo "  Users: $users"
    echo "  Spawn rate: $spawn_rate users/second"
    echo "  Duration: $run_time"
    echo "  Host: $API_URL"
    echo ""

    print_info "Starting load test..."
    poetry run locust -f tests/performance/locustfile.py \
        --host="$API_URL" \
        --users="$users" \
        --spawn-rate="$spawn_rate" \
        --run-time="$run_time" \
        --headless \
        --html=load-test-report.html \
        --csv=load-test

    print_success "Load test completed!"
    print_info "HTML report: backend/load-test-report.html"
    print_info "CSV results: backend/load-test_*.csv"

    cd ..
}

run_heavy_load_test() {
    print_header "Running Heavy Load Test (Stress Test)"

    print_info "This will test the system under heavy load (200 users)"
    print_info "Make sure you are running with PostgreSQL (not SQLite)"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Heavy load test cancelled"
        exit 0
    fi

    run_load_test 200 20 5m
}

run_all_tests() {
    print_header "Running All Performance Tests"

    run_benchmarks

    print_info "Waiting 5 seconds before load test..."
    sleep 5

    run_load_test
}

show_usage() {
    echo "Performance Test Runner for ContraVento"
    echo ""
    echo "Usage:"
    echo "  $0 benchmark        Run pytest benchmarks"
    echo "  $0 load             Run Locust load test (50 users, 2 minutes)"
    echo "  $0 load-heavy       Run heavy load test (200 users, 5 minutes)"
    echo "  $0 all              Run all performance tests"
    echo ""
    echo "Environment variables:"
    echo "  API_URL             Backend URL (default: http://localhost:8000)"
    echo ""
    echo "Examples:"
    echo "  $0 benchmark"
    echo "  API_URL=https://staging.contravento.com $0 load"
    echo ""
}

# Main
case "${1:-}" in
    benchmark)
        run_benchmarks
        ;;
    load)
        run_load_test
        ;;
    load-heavy)
        run_heavy_load_test
        ;;
    all)
        run_all_tests
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Invalid command: ${1:-}"
        echo ""
        show_usage
        exit 1
        ;;
esac

print_success "All performance tests completed successfully!"
