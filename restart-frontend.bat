@echo off
REM ============================================================================
REM ContraVento - Restart Frontend Script
REM ============================================================================
REM Kills all Node.js processes and starts a fresh frontend dev server
REM ============================================================================

echo.
echo ====================================
echo ContraVento - Restarting Frontend
echo ====================================
echo.

REM Step 1: Kill all Node.js processes
echo [1/3] Stopping all Node.js processes...
taskkill /F /IM node.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo       ✓ Node.js processes stopped
) else (
    echo       ℹ No Node.js processes running
)
echo.

REM Step 2: Wait for processes to terminate
echo [2/3] Waiting for cleanup...
timeout /t 2 /nobreak >nul
echo       ✓ Cleanup complete
echo.

REM Step 3: Start frontend dev server
echo [3/3] Starting frontend dev server...
cd /d "%~dp0frontend"
start "ContraVento Frontend" cmd /k "npm run dev"
echo       ✓ Frontend server starting...
echo.

echo ====================================
echo Frontend restart complete!
echo ====================================
echo.
echo The frontend will open automatically at:
echo http://localhost:3001
echo.
echo Press any key to close this window...
pause >nul
