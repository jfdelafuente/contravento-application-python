#!/bin/bash
# ============================================================================
# ContraVento - Restart Frontend Script (Linux/Mac)
# ============================================================================
# Kills all Node.js processes and starts a fresh frontend dev server
# ============================================================================

echo ""
echo "===================================="
echo "ContraVento - Restarting Frontend"
echo "===================================="
echo ""

# Step 1: Kill all Node.js processes
echo "[1/3] Stopping all Node.js processes..."
if pkill -f "node.*vite" 2>/dev/null; then
    echo "      ✓ Node.js processes stopped"
else
    echo "      ℹ No Node.js processes running"
fi
echo ""

# Step 2: Wait for processes to terminate
echo "[2/3] Waiting for cleanup..."
sleep 2
echo "      ✓ Cleanup complete"
echo ""

# Step 3: Start frontend dev server
echo "[3/3] Starting frontend dev server..."
cd "$(dirname "$0")/frontend"
npm run dev &
echo "      ✓ Frontend server starting..."
echo ""

echo "===================================="
echo "Frontend restart complete!"
echo "===================================="
echo ""
echo "The frontend will open automatically at:"
echo "http://localhost:3001"
echo ""
