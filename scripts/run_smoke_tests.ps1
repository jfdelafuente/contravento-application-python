# Smoke Tests for ContraVento Application (PowerShell version)
#
# Tests all 4 deployment modes to verify the application starts correctly
# and critical endpoints respond.
#
# Usage:
#   .\scripts\run_smoke_tests.ps1 -Mode <mode>
#
# Modes:
#   local-dev      - SQLite local development (http://localhost:8000)
#   local-minimal  - PostgreSQL minimal Docker (http://localhost:8000)
#   local-full     - Full Docker stack (http://localhost:8000)
#   staging        - Staging environment (https://staging.contravento.com)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('local-dev', 'local-minimal', 'local-full', 'staging')]
    [string]$Mode
)

# Test counters
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:TestsTotal = 0

# Configuration
$Timeout = 30
$BaseUrl = switch ($Mode) {
    'local-dev'      { 'http://localhost:8000' }
    'local-minimal'  { 'http://localhost:8000' }
    'local-full'     { 'http://localhost:8000' }
    'staging'        { 'https://staging.contravento.com' }
}

# Helper functions
function Print-Header {
    param([string]$Text)
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  ContraVento Smoke Tests - $Text" -ForegroundColor Blue
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host ""
}

function Print-Test {
    param([string]$Name)
    Write-Host "▶ Running: $Name" -ForegroundColor Yellow
}

function Print-Pass {
    param([string]$Message)
    Write-Host "✅ PASS - $Message" -ForegroundColor Green
    $script:TestsPassed++
    $script:TestsTotal++
}

function Print-Fail {
    param(
        [string]$Message,
        [string]$Error
    )
    Write-Host "❌ FAIL - $Message" -ForegroundColor Red
    Write-Host "   Error: $Error" -ForegroundColor Red
    $script:TestsFailed++
    $script:TestsTotal++
}

function Print-Summary {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  Test Summary" -ForegroundColor Blue
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  Total Tests: $script:TestsTotal"
    Write-Host "  Passed: $script:TestsPassed" -ForegroundColor Green
    Write-Host "  Failed: $script:TestsFailed" -ForegroundColor Red
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
}

# Start tests
$StartTime = Get-Date
Print-Header "Mode: $Mode"
Write-Host "Base URL: $BaseUrl"
Write-Host "Timeout: ${Timeout}s"
Write-Host ""

# Test 1: Health check endpoint
Print-Test "Health check - GET /health"
try {
    $Response = Invoke-WebRequest -Uri "$BaseUrl/health" -TimeoutSec $Timeout -UseBasicParsing
    if ($Response.StatusCode -eq 200) {
        $Body = $Response.Content
        if ($Body -match '"status"') {
            Print-Pass "Health endpoint returned 200 OK"
        } else {
            Print-Fail "Health endpoint missing 'status' field" "Response: $Body"
        }
    } else {
        Print-Fail "Health endpoint returned HTTP $($Response.StatusCode)" "Expected 200"
    }
} catch {
    Print-Fail "Health endpoint request failed" $_.Exception.Message
}

# Test 2: Auth endpoint - Invalid login (should return 401)
Print-Test "Auth endpoint - POST /auth/login (invalid credentials)"
try {
    $Body = @{
        login = "invalid_user"
        password = "wrong_password"
    } | ConvertTo-Json

    $Response = Invoke-WebRequest -Uri "$BaseUrl/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $Body `
        -TimeoutSec $Timeout `
        -UseBasicParsing `
        -SkipHttpErrorCheck

    if ($Response.StatusCode -eq 401) {
        Print-Pass "Auth endpoint correctly rejects invalid credentials (401)"
    } else {
        Print-Fail "Auth endpoint returned HTTP $($Response.StatusCode)" "Expected 401 for invalid credentials"
    }
} catch {
    Print-Fail "Auth endpoint request failed" $_.Exception.Message
}

# Test 3: Protected endpoint - GET /auth/me without token (should return 401)
Print-Test "Protected endpoint - GET /auth/me (no token)"
try {
    $Response = Invoke-WebRequest -Uri "$BaseUrl/auth/me" `
        -TimeoutSec $Timeout `
        -UseBasicParsing `
        -SkipHttpErrorCheck

    if ($Response.StatusCode -eq 401) {
        Print-Pass "Protected endpoint correctly requires authentication (401)"
    } else {
        Print-Fail "Protected endpoint returned HTTP $($Response.StatusCode)" "Expected 401 without token"
    }
} catch {
    Print-Fail "Protected endpoint request failed" $_.Exception.Message
}

# Test 4: Database connectivity (via Python script)
Print-Test "Database connectivity check"
try {
    $DbCheckOutput = python scripts/check_db.py $Mode 2>&1
    if ($DbCheckOutput -match "Database connection successful") {
        Print-Pass "Database connection verified"
    } else {
        Print-Fail "Database connection failed" "See check_db.py output for details"
    }
} catch {
    Print-Fail "Database check script failed" $_.Exception.Message
}

# Test 5: Static files (only for full/staging with frontend)
if ($Mode -eq 'local-full' -or $Mode -eq 'staging') {
    Print-Test "Static files - GET / (frontend)"
    try {
        $Response = Invoke-WebRequest -Uri "$BaseUrl/" -TimeoutSec $Timeout -UseBasicParsing
        if ($Response.StatusCode -eq 200) {
            $Body = $Response.Content
            if ($Body -match "<html") {
                Print-Pass "Frontend static files served (200 OK)"
            } else {
                Print-Fail "Frontend returned 200 but no HTML" "Response may be malformed"
            }
        } else {
            Print-Fail "Frontend returned HTTP $($Response.StatusCode)" "Expected 200"
        }
    } catch {
        Print-Fail "Frontend request failed" $_.Exception.Message
    }
}

# Calculate duration
$EndTime = Get-Date
$Duration = ($EndTime - $StartTime).TotalSeconds

# Print summary
Print-Summary
Write-Host ""
Write-Host "Duration: $([math]::Round($Duration, 2))s"
Write-Host ""

# Exit with appropriate code
if ($script:TestsFailed -eq 0) {
    Write-Host "✅ All smoke tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ $script:TestsFailed test(s) failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "  1. Verify the application is running for mode: $Mode"
    Write-Host "  2. Check application logs for errors"
    Write-Host "  3. Verify database is accessible"
    Write-Host "  4. Check network connectivity to $BaseUrl"
    exit 1
}
