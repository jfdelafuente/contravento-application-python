# Script to get access token for ContraVento API testing
# Usage: .\get-token.ps1

$BaseUrl = if ($env:BACKEND_URL) { $env:BACKEND_URL } else { "http://localhost:8000" }
$Username = "testuser"
$Password = "TestPass123!"

Write-Host "=== ContraVento - Getting Access Token ===" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
try {
    $null = Invoke-WebRequest -Uri "$BaseUrl/docs" -Method GET -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Backend server is not running at $BaseUrl" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start the backend server first:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  .\run-local-dev.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Login and get token
Write-Host "Logging in as $Username..." -ForegroundColor Cyan

$body = @{
    login = $Username
    password = $Password
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop

    if ($response.success -eq $true) {
        $token = $response.data.access_token
        $userId = $response.data.user.user_id
        $username = $response.data.user.username

        Write-Host "✅ Login successful" -ForegroundColor Green
        Write-Host ""
        Write-Host "User: $username (ID: $userId)" -ForegroundColor White
        Write-Host "Access Token (first 40 chars): $($token.Substring(0, 40))..." -ForegroundColor White
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "Token has been automatically saved to environment variable!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Environment variable set:" -ForegroundColor Yellow
        Write-Host "  `$env:ACCESS_TOKEN = `"$token`"" -ForegroundColor White
        Write-Host ""
        Write-Host "You can now use it in curl commands:" -ForegroundColor Yellow
        Write-Host '  curl -H "Authorization: Bearer $env:ACCESS_TOKEN" ...' -ForegroundColor White
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Token expires in 1 hour. Re-run this script to refresh." -ForegroundColor Gray
        Write-Host ""

        # Auto-set the environment variable
        $env:ACCESS_TOKEN = $token

    } else {
        Write-Host "❌ Login failed" -ForegroundColor Red
        Write-Host ""
        Write-Host "Response:" -ForegroundColor Yellow
        $response | ConvertTo-Json -Depth 10
    }

} catch {
    Write-Host "❌ Login request failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Make sure the test user exists. Create it with:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  poetry run python scripts/create_verified_user.py" -ForegroundColor Yellow
    exit 1
}
