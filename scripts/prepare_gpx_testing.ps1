# Script para preparar entorno de testing manual GPX
# Feature 003 - GPS Routes Interactive

param(
    [switch]$SetupUser,
    [switch]$CopyFiles,
    [switch]$CheckDatabase,
    [switch]$All
)

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  GPX Manual Testing - Preparation Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Función para crear usuario de prueba
function Setup-TestUser {
    Write-Host ">>> Creando usuario de prueba..." -ForegroundColor Yellow

    Push-Location backend
    try {
        poetry run python scripts/create_verified_user.py `
            --username "testgpx" `
            --email "testgpx@example.com" `
            --password "TestGPX123!"

        Write-Host "✅ Usuario creado: testgpx / TestGPX123!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Usuario ya existe o error: $_" -ForegroundColor Yellow
    } finally {
        Pop-Location
    }
}

# Función para copiar archivos GPX
function Copy-TestFiles {
    Write-Host ">>> Copiando archivos GPX de prueba..." -ForegroundColor Yellow

    # Crear carpeta temporal
    $testDir = "test-gpx-files"
    if (Test-Path $testDir) {
        Write-Host "⚠️  Carpeta $testDir ya existe, limpiando..." -ForegroundColor Yellow
        Remove-Item $testDir -Recurse -Force
    }

    New-Item -ItemType Directory -Path $testDir | Out-Null

    # Copiar archivos
    $fixtures = "backend\tests\fixtures\gpx"

    Copy-Item "$fixtures\short_route.gpx" "$testDir\" -Force
    Copy-Item "$fixtures\camino_del_cid.gpx" "$testDir\" -Force
    Copy-Item "$fixtures\long_route_5mb.gpx" "$testDir\" -Force
    Copy-Item "$fixtures\no_elevation.gpx" "$testDir\" -Force
    Copy-Item "$fixtures\invalid_gpx.xml" "$testDir\" -Force

    Write-Host "✅ Archivos copiados a: $testDir\" -ForegroundColor Green
    Get-ChildItem $testDir | Format-Table Name, @{Name="Size";Expression={"{0:N2} KB" -f ($_.Length/1KB)}}
}

# Función para verificar base de datos
function Check-Database {
    Write-Host ">>> Verificando estado de la base de datos..." -ForegroundColor Yellow

    Push-Location backend
    try {
        $script = @"
from src.database import get_sync_db
from src.models.gpx import GPXFile, TrackPoint
from src.models.trip import Trip
from src.models.user import User

db = next(get_sync_db())

# Contar registros
users = db.execute('SELECT COUNT(*) FROM users').scalar()
trips = db.execute('SELECT COUNT(*) FROM trips').scalar()
gpx_files = db.execute('SELECT COUNT(*) FROM gpx_files').scalar()
track_points = db.execute('SELECT COUNT(*) FROM track_points').scalar()

print(f'📊 Estado de la Base de Datos')
print(f'   Usuarios: {users}')
print(f'   Viajes: {trips}')
print(f'   Archivos GPX: {gpx_files}')
print(f'   Track Points: {track_points}')

# Listar GPX files con detalles
if gpx_files > 0:
    print(f'\n📁 Archivos GPX:')
    result = db.execute('''
        SELECT g.file_name, g.distance_km, g.processing_status, t.title
        FROM gpx_files g
        JOIN trips t ON g.trip_id = t.trip_id
    ''')
    for row in result:
        print(f'   - {row[3]}: {row[0]} ({row[1]} km) - Status: {row[2]}')
"@

        $script | poetry run python
        Write-Host ""
        Write-Host "✅ Base de datos verificada" -ForegroundColor Green

    } catch {
        Write-Host "❌ Error al verificar BD: $_" -ForegroundColor Red
    } finally {
        Pop-Location
    }
}

# Función para crear archivo de prueba grande (>10MB)
function Create-OversizedFile {
    Write-Host ">>> Creando archivo de prueba >10MB..." -ForegroundColor Yellow

    $testDir = "test-gpx-files"
    if (-not (Test-Path $testDir)) {
        New-Item -ItemType Directory -Path $testDir | Out-Null
    }

    $oversizedFile = "$testDir\oversized.gpx"

    # Crear archivo de 11MB con contenido GPX inválido
    $content = "<?xml version='1.0'?><gpx>" + ("x" * 11MB) + "</gpx>"
    $content | Out-File -FilePath $oversizedFile -Encoding UTF8

    $size = (Get-Item $oversizedFile).Length / 1MB
    Write-Host "✅ Archivo creado: oversized.gpx ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
}

# Ejecutar acciones según parámetros
if ($All -or $SetupUser) {
    Setup-TestUser
    Write-Host ""
}

if ($All -or $CopyFiles) {
    Copy-TestFiles
    Write-Host ""
}

if ($All -or $CheckDatabase) {
    Check-Database
    Write-Host ""
}

# Si no se especificó ningún parámetro, mostrar ayuda
if (-not ($SetupUser -or $CopyFiles -or $CheckDatabase -or $All)) {
    Write-Host "Uso:" -ForegroundColor Cyan
    Write-Host "  .\scripts\prepare_gpx_testing.ps1 -All              # Ejecutar todo"
    Write-Host "  .\scripts\prepare_gpx_testing.ps1 -SetupUser        # Solo crear usuario"
    Write-Host "  .\scripts\prepare_gpx_testing.ps1 -CopyFiles        # Solo copiar archivos"
    Write-Host "  .\scripts\prepare_gpx_testing.ps1 -CheckDatabase    # Solo verificar BD"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Yellow
    Write-Host "  # Preparación completa para testing manual"
    Write-Host "  .\scripts\prepare_gpx_testing.ps1 -All"
    Write-Host ""
    Write-Host "  # Solo copiar archivos GPX de prueba"
    Write-Host "  .\scripts\prepare_gpx_testing.ps1 -CopyFiles"
    Write-Host ""
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Siguiente paso: Revisar MANUAL_TESTING.md" -ForegroundColor Green
Write-Host "  specs/003-gps-routes/MANUAL_TESTING.md" -ForegroundColor Gray
Write-Host "==================================================" -ForegroundColor Cyan
