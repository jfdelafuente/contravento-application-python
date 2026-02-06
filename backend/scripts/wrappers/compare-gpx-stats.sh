#!/bin/bash

# Compare GPX Statistics: gpxpy vs Application Logic
#
# This script runs two different GPX analysis tools on the same file:
# 1. gpx_stats.py: Uses gpxpy library directly (reference implementation)
# 2. app_gpx_stats.py: Uses application logic (GPXService + RouteStatsService)
#
# Purpose: Validate that our application algorithms produce similar results to gpxpy
#
# Usage:
#   ./scripts/wrappers/compare-gpx-stats.sh <path-to-gpx-file>
#
# Example:
#   ./scripts/wrappers/compare-gpx-stats.sh scripts/datos/QH_2013.gpx

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if file path provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No GPX file specified${NC}"
    echo ""
    echo "Usage: $0 <path-to-gpx-file>"
    echo ""
    echo "Example:"
    echo "  $0 scripts/datos/QH_2013.gpx"
    exit 1
fi

GPX_FILE="$1"

# Check if file exists
if [ ! -f "$GPX_FILE" ]; then
    echo -e "${RED}Error: File '$GPX_FILE' not found${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GPX Statistics Comparison${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "File: ${GREEN}$GPX_FILE${NC}"
echo -e "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Run gpxpy-based analysis
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}1. gpxpy Library (Reference)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
poetry run python scripts/analysis/gpx_stats.py "$GPX_FILE"

echo ""

# Run application logic-based analysis
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}2. Application Logic (Our Implementation)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
poetry run python scripts/analysis/app_gpx_stats.py "$GPX_FILE"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Comparison completed${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Small differences are expected due to:"
echo "  - Trackpoint simplification (Douglas-Peucker algorithm)"
echo "  - Different rounding/precision in calculations"
echo "  - GPS error filtering (our app filters outliers)"
echo ""
echo "Key metrics to compare:"
echo "  - Moving time should be similar (±5%)"
echo "  - Average speed should be similar (±5%)"
echo "  - Total distance should match exactly"
echo ""
