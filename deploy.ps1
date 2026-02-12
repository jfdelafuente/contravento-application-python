# ============================================================================
# ContraVento - Multi-Environment Deployment Script (PowerShell)
# ============================================================================
# 📖 Documentation: docs/deployment/README.md
#    Complete guide with decision tree, troubleshooting, and mode details
#
# Simplified deployment for all environments:
#   .\deploy.ps1 local                  - Start local development
#   .\deploy.ps1 local -WithFrontend    - Start local + frontend
#   .\deploy.ps1 dev                    - Start development/integration
#   .\deploy.ps1 staging                - Start staging/pre-production
#   .\deploy.ps1 prod                   - Start production
#
# Additional commands:
#   .\deploy.ps1 <env> down  - Stop environment
#   .\deploy.ps1 <env> logs  - View logs
#   .\deploy.ps1 <env> ps    - View running containers
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Environment,

    [Parameter(Mandatory=$false)]
    [string]$Command = "up",

    [Parameter(Mandatory=$false)]
    [switch]$WithFrontend,

    [Parameter(Mandatory=$false)]
    [switch]$PullLatest,

    [Parameter(Mandatory=$false)]
    [string]$PullVersion,

    [Parameter(Mandatory=$false)]
    [string]$RollbackTo
)

# Functions
function Print-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Print-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Print-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""
}

# Pull images from Docker Hub
function Pull-FromDockerHub {
    param(
        [string]$Env,
        [string]$Tag
    )

    Print-Info "🐳 Pulling images from Docker Hub..."
    Write-Host "  - Backend: jfdelafuente/contravento-backend:$Tag"
    Write-Host "  - Frontend: jfdelafuente/contravento-frontend:$Tag"
    Write-Host ""

    # Pull images with specified tag
    docker pull "jfdelafuente/contravento-backend:$Tag"
    if ($LASTEXITCODE -ne 0) {
        Print-Error "Failed to pull backend image with tag: $Tag"
        Print-Info "Make sure the image exists on Docker Hub: https://hub.docker.com/r/jfdelafuente/contravento-backend/tags"
        exit 1
    }

    docker pull "jfdelafuente/contravento-frontend:$Tag"
    if ($LASTEXITCODE -ne 0) {
        Print-Error "Failed to pull frontend image with tag: $Tag"
        Print-Info "Make sure the image exists on Docker Hub: https://hub.docker.com/r/jfdelafuente/contravento-frontend/tags"
        exit 1
    }

    # Re-tag as latest for docker-compose compatibility
    Print-Info "Tagging images as latest for docker-compose..."
    docker tag "jfdelafuente/contravento-backend:$Tag" "jfdelafuente/contravento-backend:latest"
    docker tag "jfdelafuente/contravento-frontend:$Tag" "jfdelafuente/contravento-frontend:latest"

    Print-Success "✅ Images pulled and tagged successfully"
    Write-Host ""
}

# Check if docker-compose is installed
function Check-DockerCompose {
    if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Print-Error "docker-compose not found. Please install Docker Compose."
        exit 1
    }
}

# Validate environment
function Validate-Env {
    param([string]$Env)

    $validEnvs = @("local", "local-minimal", "dev", "staging", "prod")
    if ($validEnvs -notcontains $Env) {
        Print-Error "Invalid environment: $Env"
        Write-Host "Valid environments: local, local-minimal, dev, staging, prod"
        exit 1
    }
}

# Check if .env file exists
function Check-EnvFile {
    param([string]$Env)

    $envFile = ".env.$Env"

    if (!(Test-Path $envFile)) {
        Print-Warning ".env file not found: $envFile"
        Print-Info "Creating from example file..."

        $exampleFile = "$envFile.example"
        if (Test-Path $exampleFile) {
            Copy-Item $exampleFile $envFile

            # Auto-generate SECRET_KEY for local/local-minimal environments only
            if ($Env -eq "local" -or $Env -eq "local-minimal") {
                Print-Info "Auto-generating SECRET_KEY for local development..."

                # Generate a random SECRET_KEY using Python
                $secretKey = $null
                try {
                    if (Get-Command python3 -ErrorAction SilentlyContinue) {
                        $secretKey = python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>$null
                    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
                        $secretKey = python -c "import secrets; print(secrets.token_urlsafe(64))" 2>$null
                    }
                } catch {
                    Print-Warning "Python not found, using default SECRET_KEY"
                }

                # Replace SECRET_KEY in .env file if generated successfully
                if ($secretKey) {
                    (Get-Content $envFile) -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey" | Set-Content $envFile
                    Print-Success "Auto-generated SECRET_KEY for local development"
                }

                Print-Success "Created $envFile with auto-generated SECRET_KEY"
            } else {
                # For staging/prod, require manual configuration
                Print-Warning "IMPORTANT: Edit $envFile and configure all variables!"
                Print-Warning "Generate strong SECRET_KEY with: python -c `"import secrets; print(secrets.token_urlsafe(64))`""
                Print-Warning "Press Ctrl+C to abort, or Enter to continue with example values (NOT RECOMMENDED)"
                Read-Host ""
            }
        } else {
            Print-Error "Example file not found: $exampleFile"
            exit 1
        }
    }
}

# Start environment
function Start-Env {
    param(
        [string]$Env,
        [bool]$WithFrontend,
        [bool]$PullLatest,
        [string]$PullVersion,
        [string]$RollbackTo
    )

    $composeFile = "docker-compose.$Env.yml"

    Print-Header "Starting $Env environment"

    Check-EnvFile $Env

    # Handle Docker Hub pull options for staging/prod
    $pullOption = $null
    $version = $null

    if ($PullLatest) {
        $pullOption = "pull-latest"
        if ($Env -eq "staging") {
            Pull-FromDockerHub -Env $Env -Tag "staging-latest"
        } elseif ($Env -eq "prod") {
            Print-Error "❌ Error: Use -PullVersion for production deployments"
            Print-Info "Example: .\deploy.ps1 prod -PullVersion v1.3.0"
            exit 1
        } else {
            Print-Warning "ℹ️  -PullLatest is only for staging/prod environments"
            Print-Info "Ignoring flag for $Env environment"
        }
    }

    if ($PullVersion) {
        $pullOption = "pull-version"
        $version = $PullVersion
        if ($Env -eq "prod" -or $Env -eq "staging") {
            Pull-FromDockerHub -Env $Env -Tag $PullVersion
        } else {
            Print-Warning "ℹ️  -PullVersion is only for staging/prod environments"
            Print-Info "Ignoring flag for $Env environment"
        }
    }

    if ($RollbackTo) {
        $pullOption = "rollback"
        $version = $RollbackTo
        if ($Env -eq "prod" -or $Env -eq "staging") {
            Print-Warning "⚠️  ROLLBACK: Deploying version $RollbackTo"
            Pull-FromDockerHub -Env $Env -Tag $RollbackTo
        } else {
            Print-Warning "ℹ️  -RollbackTo is only for staging/prod environments"
            Print-Info "Ignoring flag for $Env environment"
        }
    }

    Print-Info "Using configuration:"
    Write-Host "  - Base: docker-compose.yml"
    Write-Host "  - Overlay: $composeFile"
    Write-Host "  - Env file: .env.$Env"
    if ($WithFrontend) {
        Write-Host "  - Frontend: ENABLED (Vite dev server)"
    }
    if ($pullOption) {
        Write-Host "  - Deploy mode: Docker Hub ($pullOption)"
    }
    Write-Host ""

    # Confirmation for production
    if ($Env -eq "prod") {
        Print-Warning "⚠️  You are about to deploy to PRODUCTION!"
        if ($version) {
            Print-Info "Version: $version"
        }
        $confirm = Read-Host "Are you sure? (yes/no)"
        if ($confirm -ne "yes") {
            Print-Info "Deployment cancelled"
            exit 0
        }
    }

    # Build frontend for staging/prod environments (skip if pulling from Docker Hub)
    if (!$pullOption -and ($Env -eq "staging" -or $Env -eq "prod")) {
        Print-Info "Building frontend for $Env..."
        Set-Location frontend

        # Install dependencies if needed
        if (!(Test-Path "node_modules")) {
            Print-Warning "node_modules not found, running npm install..."
            npm install
        }

        # Run production build
        if ($Env -eq "staging") {
            npm run build:staging
        } else {
            npm run build:prod
        }

        Set-Location ..
        Print-Success "Frontend build complete!"
    }

    # Pull latest images (skip if already pulled from Docker Hub)
    if (!$pullOption) {
        Print-Info "Pulling latest images..."
        docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" pull
    }

    # Build services (skip if using Docker Hub images)
    if (!$pullOption) {
        Print-Info "Building services..."
        docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" build
    } else {
        Print-Info "Skipping build (using pre-built images from Docker Hub)"
    }

    # Start services (enable frontend if flag is set)
    Print-Info "Starting services..."
    if ($WithFrontend) {
        # Scale frontend to 1 replica to enable it
        docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" up -d --scale frontend=1
    } else {
        docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" up -d
    }

    # Wait for services to be healthy
    Print-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 10

    # Show status
    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" ps

    Print-Success "$Env environment started successfully!"

    # Environment-specific messages
    switch ($Env) {
        "local-minimal" {
            Write-Host ""
            Print-Info "Access your minimal local environment:"
            Write-Host "  Backend API:     http://localhost:8000"
            Write-Host "  API Docs:        http://localhost:8000/docs"
            if ($WithFrontend) {
                Write-Host "  Frontend:        http://localhost:5173"
            }
            Write-Host "  PostgreSQL:      localhost:5432 (use DBeaver, psql, etc.)"
            Write-Host ""
            if ($WithFrontend) {
                Print-Info "Frontend + Backend + PostgreSQL running"
            } else {
                Print-Warning "Minimal setup (PostgreSQL + Backend only)"
                Print-Info "Add frontend with: .\deploy.ps1 local-minimal -WithFrontend"
            }
            Print-Info "For MailHog, Redis, pgAdmin use: .\deploy.ps1 local"
        }
        "local" {
            Write-Host ""
            Print-Info "Access your full local environment:"
            Write-Host "  Backend API:     http://localhost:8000"
            Write-Host "  API Docs:        http://localhost:8000/docs"
            if ($WithFrontend) {
                Write-Host "  Frontend:        http://localhost:5173"
            }
            Write-Host "  MailHog UI:      http://localhost:8025"
            Write-Host "  pgAdmin:         http://localhost:5050"
            Write-Host "  PostgreSQL:      localhost:5432"
            Write-Host "  Redis:           localhost:6379"
            Write-Host ""
            if ($WithFrontend) {
                Print-Info "Frontend + Backend + All Services running"
            } else {
                Print-Warning "Full setup without frontend"
                Print-Info "Add frontend with: .\deploy.ps1 local -WithFrontend"
            }
            Print-Info "For lighter setup use: .\deploy.ps1 local-minimal"
        }
        "dev" {
            Write-Host ""
            Print-Info "Access your dev environment:"
            Write-Host "  Backend API:     http://dev.contravento.local:8000"
            Write-Host "  API Docs:        http://dev.contravento.local:8000/docs"
        }
        "staging" {
            Write-Host ""
            Print-Info "Access your staging environment:"
            Write-Host "  Backend API:     https://staging.contravento.com"
            Write-Host "  Monitoring:      http://localhost:3000"
        }
        "prod" {
            Write-Host ""
            Print-Success "Production deployment complete!"
            Write-Host "  Backend API:     https://api.contravento.com"
            Write-Host "  Monitoring:      https://monitoring.contravento.com"
        }
    }

    Write-Host ""
    Print-Info "View logs with: .\deploy.ps1 $Env logs"
    Print-Info "Stop with: .\deploy.ps1 $Env down"
}

# Stop environment
function Stop-Env {
    param([string]$Env)

    $composeFile = "docker-compose.$Env.yml"

    Print-Header "Stopping $Env environment"

    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" down

    Print-Success "$Env environment stopped"
}

# View logs
function View-Logs {
    param([string]$Env)

    $composeFile = "docker-compose.$Env.yml"

    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" logs -f
}

# Show running containers
function Show-Ps {
    param([string]$Env)

    $composeFile = "docker-compose.$Env.yml"

    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" ps
}

# Restart environment
function Restart-Env {
    param(
        [string]$Env,
        [bool]$WithFrontend,
        [bool]$PullLatest,
        [string]$PullVersion,
        [string]$RollbackTo
    )

    Print-Header "Restarting $Env environment"

    Stop-Env $Env
    Start-Sleep -Seconds 2
    Start-Env -Env $Env -WithFrontend $WithFrontend -PullLatest $PullLatest -PullVersion $PullVersion -RollbackTo $RollbackTo
}

# Main
Check-DockerCompose
Validate-Env $Environment

switch ($Command.ToLower()) {
    {$_ -in "up", "start"} {
        Start-Env -Env $Environment -WithFrontend $WithFrontend.IsPresent -PullLatest $PullLatest.IsPresent -PullVersion $PullVersion -RollbackTo $RollbackTo
    }
    {$_ -in "down", "stop"} {
        Stop-Env $Environment
    }
    "logs" {
        View-Logs $Environment
    }
    {$_ -in "ps", "status"} {
        Show-Ps $Environment
    }
    "restart" {
        Restart-Env -Env $Environment -WithFrontend $WithFrontend.IsPresent -PullLatest $PullLatest.IsPresent -PullVersion $PullVersion -RollbackTo $RollbackTo
    }
    default {
        Print-Error "Invalid command: $Command"
        Write-Host "Valid commands: up, down, logs, ps, restart"
        exit 1
    }
}
