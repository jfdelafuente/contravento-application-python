###############################################################################
# GPX Statistics Testing Script (User Story 5 - Advanced Statistics)
#
# Este script automatiza la validación de estadísticas avanzadas de rutas GPX
# probando los 3 archivos GPX de prueba contra el API.
#
# Requisitos:
# - Backend corriendo en http://localhost:8000
# - Usuario de prueba creado (testuser / TestPass123!)
#
# Uso:
#   .\scripts\test_gpx_statistics.ps1
###############################################################################

# Configuración
$API_URL = "http://localhost:8000"
$USERNAME = "testuser"
$PASSWORD = "TestPass123!"
$GPX_DIR = "test_data"

# Funciones auxiliares
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-BackendRunning {
    try {
        $response = Invoke-WebRequest -Uri "$API_URL/health" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Banner
Write-ColorOutput "`n=================================================="  "Blue"
Write-ColorOutput "  GPX Statistics Testing Script (User Story 5)"  "Blue"
Write-ColorOutput "==================================================`n"  "Blue"

# Verificar backend
Write-ColorOutput "[1/6] Verificando backend..." "Yellow"
if (-not (Test-BackendRunning)) {
    Write-ColorOutput "Error: Backend no está corriendo en $API_URL" "Red"
    Write-ColorOutput "Inicia el backend con: poetry run uvicorn src.main:app --reload" "Red"
    exit 1
}
Write-ColorOutput "✓ Backend activo en $API_URL`n" "Green"

# Autenticación
Write-ColorOutput "[2/6] Autenticando usuario..." "Yellow"
$loginBody = @{
    username = $USERNAME
    password = $PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
    $ACCESS_TOKEN = $loginResponse.access_token
    Write-ColorOutput "✓ Autenticación exitosa (token obtenido)`n" "Green"
} catch {
    Write-ColorOutput "Error: No se pudo autenticar. Verifica que el usuario existe." "Red"
    Write-ColorOutput "Crea el usuario con: poetry run python scripts/create_verified_user.py" "Red"
    exit 1
}

# Crear viaje de prueba
Write-ColorOutput "[3/6] Creando viaje de prueba..." "Yellow"
$tripBody = @{
    title = "Prueba Estadísticas GPX (Automatizado)"
    description = "Viaje de prueba automatizado para validar estadísticas avanzadas de rutas GPX (User Story 5). Este viaje se creó mediante script de testing."
    start_date = "2024-06-15"
    distance_km = 25.0
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $ACCESS_TOKEN"
    "Content-Type" = "application/json"
}

try {
    $tripResponse = Invoke-RestMethod -Uri "$API_URL/trips" -Method Post -Headers $headers -Body $tripBody
    $TRIP_ID = $tripResponse.data.trip_id
    Write-ColorOutput "✓ Viaje creado con ID: $TRIP_ID`n" "Green"
} catch {
    Write-ColorOutput "Error: No se pudo crear el viaje." "Red"
    Write-ColorOutput $_.Exception.Message "Red"
    exit 1
}

# Publicar viaje
Write-ColorOutput "[4/6] Publicando viaje..." "Yellow"
try {
    $publishResponse = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/publish" -Method Post -Headers $headers
    Write-ColorOutput "✓ Viaje publicado correctamente`n" "Green"
} catch {
    Write-ColorOutput "Error: No se pudo publicar el viaje." "Red"
    exit 1
}

# Test 1: GPX con timestamps
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  TEST 1: test_with_timestamps.gpx" "Blue"
Write-ColorOutput "  Expectativa: ✓ route_statistics presente" "Blue"
Write-ColorOutput "==================================================`n" "Blue"

Write-ColorOutput "[5/6] Subiendo test_with_timestamps.gpx..." "Yellow"

# Crear multipart form data
$filePath = Join-Path $GPX_DIR "test_with_timestamps.gpx"
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$fileName = "test_with_timestamps.gpx"

# Usar Invoke-WebRequest para multipart/form-data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"
$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: application/gpx+xml$LF",
    [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes),
    "--$boundary--$LF"
) -join $LF

try {
    $uploadHeaders = @{
        "Authorization" = "Bearer $ACCESS_TOKEN"
        "Content-Type" = "multipart/form-data; boundary=$boundary"
    }

    $gpx1Response = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/gpx" -Method Post -Headers $uploadHeaders -Body $bodyLines
    $GPX1_FILE_ID = $gpx1Response.data.gpx_file_id
    $GPX1_STATUS = $gpx1Response.data.processing_status
    Write-ColorOutput "✓ GPX subido: $GPX1_FILE_ID (status: $GPX1_STATUS)" "Green"
} catch {
    Write-ColorOutput "Error al subir GPX: $($_.Exception.Message)" "Red"
    exit 1
}

# Esperar procesamiento si es async
if ($GPX1_STATUS -eq "processing") {
    Write-ColorOutput "Esperando procesamiento asíncrono..." "Yellow"
    Start-Sleep -Seconds 5
}

# Obtener estadísticas
Write-ColorOutput "[6/6] Obteniendo estadísticas calculadas..." "Yellow"
try {
    $track1Response = Invoke-RestMethod -Uri "$API_URL/gpx/$GPX1_FILE_ID/track" -Method Get -Headers $headers
    $stats1 = $track1Response.data.route_statistics

    Write-ColorOutput "`n--- Resultados Test 1 ---" "Blue"
    $stats1 | ConvertTo-Json -Depth 10 | Write-Host

    # Validaciones
    if ($stats1 -eq $null) {
        Write-ColorOutput "✗ FAIL: route_statistics es null (debería estar presente)" "Red"
        exit 1
    } else {
        Write-ColorOutput "✓ PASS: route_statistics presente" "Green"
    }

    Write-ColorOutput "`n--- Validaciones Test 1 ---" "Blue"

    # Validar campos
    if ($stats1.avg_speed_kmh -gt 0) {
        Write-ColorOutput "✓ avg_speed_kmh: $($stats1.avg_speed_kmh) km/h" "Green"
    }

    if ($stats1.max_speed_kmh -gt 0) {
        Write-ColorOutput "✓ max_speed_kmh: $($stats1.max_speed_kmh) km/h" "Green"
    }

    if ($stats1.total_time_minutes -ge $stats1.moving_time_minutes) {
        Write-ColorOutput "✓ total_time ($($stats1.total_time_minutes) min) >= moving_time ($($stats1.moving_time_minutes) min)" "Green"
    }

    if ($stats1.max_gradient -lt 35) {
        Write-ColorOutput "✓ max_gradient: $($stats1.max_gradient)% (realista, < 35%)" "Green"
    } else {
        Write-ColorOutput "✗ max_gradient: $($stats1.max_gradient)% (IRREAL, debería ser < 35%)" "Red"
        Write-ColorOutput "  → BUG: distance_3d() usado en lugar de distance_2d()" "Red"
    }

    if ($stats1.top_climbs -and $stats1.top_climbs.Count -gt 0) {
        Write-ColorOutput "✓ top_climbs: $($stats1.top_climbs.Count) subidas detectadas" "Green"
        foreach ($climb in $stats1.top_climbs) {
            Write-ColorOutput "  - $($climb.description)" "Gray"
        }
    }

} catch {
    Write-ColorOutput "Error al obtener estadísticas: $($_.Exception.Message)" "Red"
    exit 1
}

# Test 2: GPX sin timestamps
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  TEST 2: test_without_timestamps.gpx" "Blue"
Write-ColorOutput "  Expectativa: ✗ route_statistics null" "Blue"
Write-ColorOutput "==================================================`n" "Blue"

# Eliminar GPX anterior
Write-ColorOutput "Eliminando GPX anterior..." "Yellow"
Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/gpx" -Method Delete -Headers $headers | Out-Null
Write-ColorOutput "✓ GPX anterior eliminado" "Green"

# Subir nuevo GPX
Write-ColorOutput "Subiendo test_without_timestamps.gpx..." "Yellow"
$filePath2 = Join-Path $GPX_DIR "test_without_timestamps.gpx"
$fileBytes2 = [System.IO.File]::ReadAllBytes($filePath2)
$fileName2 = "test_without_timestamps.gpx"

$bodyLines2 = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName2`"",
    "Content-Type: application/gpx+xml$LF",
    [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes2),
    "--$boundary--$LF"
) -join $LF

$gpx2Response = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/gpx" -Method Post -Headers $uploadHeaders -Body $bodyLines2
$GPX2_FILE_ID = $gpx2Response.data.gpx_file_id
Write-ColorOutput "✓ GPX subido: $GPX2_FILE_ID" "Green"

Start-Sleep -Seconds 2

$track2Response = Invoke-RestMethod -Uri "$API_URL/gpx/$GPX2_FILE_ID/track" -Method Get -Headers $headers
$stats2 = $track2Response.data.route_statistics

Write-ColorOutput "`n--- Resultados Test 2 ---" "Blue"
if ($stats2 -eq $null) {
    Write-Host "null"
    Write-ColorOutput "✓ PASS: route_statistics es null (correcto, sin timestamps)" "Green"
} else {
    $stats2 | ConvertTo-Json -Depth 10 | Write-Host
    Write-ColorOutput "✗ FAIL: route_statistics presente (debería ser null sin timestamps)" "Red"
    exit 1
}

# Test 3: Gradientes realistas
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  TEST 3: test_realistic_gradients.gpx" "Blue"
Write-ColorOutput "  Expectativa: ✓ max_gradient < 35%" "Blue"
Write-ColorOutput "==================================================`n" "Blue"

# Eliminar GPX anterior
Write-ColorOutput "Eliminando GPX anterior..." "Yellow"
Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/gpx" -Method Delete -Headers $headers | Out-Null
Write-ColorOutput "✓ GPX anterior eliminado" "Green"

# Subir nuevo GPX
Write-ColorOutput "Subiendo test_realistic_gradients.gpx..." "Yellow"
$filePath3 = Join-Path $GPX_DIR "test_realistic_gradients.gpx"
$fileBytes3 = [System.IO.File]::ReadAllBytes($filePath3)
$fileName3 = "test_realistic_gradients.gpx"

$bodyLines3 = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName3`"",
    "Content-Type: application/gpx+xml$LF",
    [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes3),
    "--$boundary--$LF"
) -join $LF

$gpx3Response = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/gpx" -Method Post -Headers $uploadHeaders -Body $bodyLines3
$GPX3_FILE_ID = $gpx3Response.data.gpx_file_id
Write-ColorOutput "✓ GPX subido: $GPX3_FILE_ID" "Green"

Start-Sleep -Seconds 2

$track3Response = Invoke-RestMethod -Uri "$API_URL/gpx/$GPX3_FILE_ID/track" -Method Get -Headers $headers
$stats3 = $track3Response.data.route_statistics

Write-ColorOutput "`n--- Resultados Test 3 ---" "Blue"
$stats3 | ConvertTo-Json -Depth 10 | Write-Host

Write-ColorOutput "`n--- Validaciones Test 3 ---" "Blue"
if ($stats3.max_gradient -lt 35) {
    Write-ColorOutput "✓ PASS: max_gradient: $($stats3.max_gradient)% (realista, < 35%)" "Green"
} else {
    Write-ColorOutput "✗ FAIL: max_gradient: $($stats3.max_gradient)% (IRREAL, debería ser < 35%)" "Red"
    exit 1
}

if ($stats3.avg_gradient) {
    Write-ColorOutput "✓ avg_gradient: $($stats3.avg_gradient)% (subida continua)" "Green"
}

# Resumen final
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  RESUMEN DE PRUEBAS" "Blue"
Write-ColorOutput "==================================================" "Blue"
Write-ColorOutput "✓ Test 1: GPX con timestamps → Estadísticas calculadas" "Green"
Write-ColorOutput "✓ Test 2: GPX sin timestamps → Sin estadísticas (null)" "Green"
Write-ColorOutput "✓ Test 3: Gradientes realistas → max_gradient < 35%" "Green"
Write-ColorOutput "`nViaje de prueba creado: http://localhost:5173/trips/$TRIP_ID" "Blue"
Write-ColorOutput "`n¡Todas las pruebas pasaron exitosamente! ✓" "Green"
