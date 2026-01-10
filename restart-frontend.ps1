# ============================================================================
# ContraVento - Restart Frontend Script (PowerShell)
# ============================================================================
# Kills all Node.js processes and starts a fresh frontend dev server
# ============================================================================

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "ContraVento - Restarting Frontend" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill all Node.js processes
Write-Host "[1/3] Stopping all Node.js processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $nodeProcesses | Stop-Process -Force
    Write-Host "      ✓ Stopped $($nodeProcesses.Count) Node.js process(es)" -ForegroundColor Green
} else {
    Write-Host "      ℹ No Node.js processes running" -ForegroundColor Gray
}
Write-Host ""

# Step 2: Wait for processes to terminate
Write-Host "[2/3] Waiting for cleanup..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Write-Host "      ✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

# Step 3: Start frontend dev server
Write-Host "[3/3] Starting frontend dev server..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendPath
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
Write-Host "      ✓ Frontend server starting..." -ForegroundColor Green
Write-Host ""

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Frontend restart complete!" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The frontend will open automatically at:" -ForegroundColor White
Write-Host "http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
