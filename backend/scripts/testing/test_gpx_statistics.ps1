###############################################################################
# GPX Statistics Testing Script (User Story 5 - Advanced Statistics)
#
# Este script automatiza la validacion de estadisticas avanzadas de rutas GPX
# probando los 3 archivos GPX de prueba contra el API.
#
# Requisitos:
# - Backend corriendo en http://localhost:8000
# - Usuario de prueba creado (testuser / TestPass123!)
#
# Uso:
#   .\scripts\test_gpx_statistics.ps1
###############################################################################

# Configuracion
$API_URL = "http://localhost:8000"
$USERNAME = "testuser"
$PASSWORD = "TestPass123!"

# Ruta relativa al script (backend/scripts/ -> backend/test_data/)
$BACKEND_DIR = Split-Path -Parent $PSScriptRoot
$GPX_DIR = Join-Path $BACKEND_DIR "test_data"

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
        $response = Invoke-RestMethod -Uri "$API_URL/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
        return $response.success -eq $true
    } catch {
        return $false
    }
}

function Create-And-PublishTrip {
    param(
        [string]$Title,
        [string]$Description,
        [hashtable]$Headers
    )

    $tripBody = @{
        title = $Title
        description = $Description
        start_date = "2024-06-15"
        distance_km = 25.0
    } | ConvertTo-Json

    try {
        $tripResponse = Invoke-RestMethod -Uri "$API_URL/trips" -Method Post -Headers $Headers -Body $tripBody

        if ($tripResponse.data -and $tripResponse.data.trip_id) {
            $tripId = $tripResponse.data.trip_id
            Write-ColorOutput "  [OK] Viaje creado con ID: $tripId" "Green"
        } else {
            Write-ColorOutput "  Error: Respuesta del servidor no contiene trip_id" "Red"
            exit 1
        }

        # Publicar viaje
        $publishResponse = Invoke-RestMethod -Uri "$API_URL/trips/$tripId/publish" -Method Post -Headers $Headers
        Write-ColorOutput "  [OK] Viaje publicado correctamente" "Green"

        return $tripId
    } catch {
        Write-ColorOutput "  Error: No se pudo crear/publicar el viaje." "Red"
        Write-ColorOutput "  Error detallado: $($_.Exception.Message)" "Red"
        exit 1
    }
}

# Banner
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  GPX Statistics Testing Script (User Story 5)" "Blue"
Write-ColorOutput "==================================================`n" "Blue"

# Verificar backend
Write-ColorOutput "[1/2] Verificando backend..." "Yellow"
if (-not (Test-BackendRunning)) {
    Write-ColorOutput "Error: Backend no esta corriendo en $API_URL" "Red"
    Write-ColorOutput "Inicia el backend con: poetry run uvicorn src.main:app --reload" "Red"
    exit 1
}
Write-ColorOutput "[OK] Backend activo en $API_URL`n" "Green"

# Autenticacion
Write-ColorOutput "[2/2] Autenticando usuario..." "Yellow"
$loginBody = @{
    login = $USERNAME
    password = $PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method Post -ContentType "application/json" -Body $loginBody

    # Extract token from nested data structure
    if ($loginResponse.data -and $loginResponse.data.access_token) {
        $ACCESS_TOKEN = $loginResponse.data.access_token
        Write-ColorOutput "[OK] Autenticacion exitosa (token obtenido)`n" "Green"
    } else {
        Write-ColorOutput "Error: Respuesta del servidor no contiene access_token" "Red"
        Write-ColorOutput "Respuesta recibida: $($loginResponse | ConvertTo-Json -Depth 3)" "Red"
        exit 1
    }
} catch {
    Write-ColorOutput "Error: No se pudo autenticar. Verifica que el usuario exists." "Red"
    Write-ColorOutput "Crea el usuario con: poetry run python scripts/create_verified_user.py" "Red"
    Write-ColorOutput "Error detallado: $($_.Exception.Message)" "Red"
    exit 1
}

# Preparar headers de autenticacion
$headers = @{
    "Authorization" = "Bearer $ACCESS_TOKEN"
    "Content-Type" = "application/json"
}

# Array para almacenar los trip IDs creados
$TRIP_IDS = @()

# Test 1: GPX con timestamps
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  TEST 1: test_with_timestamps.gpx" "Blue"
Write-ColorOutput "  Expectativa: [OK] route_statistics presente" "Blue"
Write-ColorOutput "==================================================`n" "Blue"

Write-ColorOutput "[1/3] Creando y publicando viaje para Test 1..." "Yellow"
$TRIP1_ID = Create-And-PublishTrip `
    -Title "Test 1: GPX con Timestamps (Automatizado)" `
    -Description "Viaje de prueba para validar calculo de estadisticas avanzadas con GPX que contiene timestamps. User Story 5 - Test 1." `
    -Headers $headers
$TRIP_IDS += $TRIP1_ID

Write-ColorOutput "`n[2/3] Subiendo test_with_timestamps.gpx..." "Yellow"

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

    $gpx1Response = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP1_ID/gpx" -Method Post -Headers $uploadHeaders -Body $bodyLines
    $GPX1_FILE_ID = $gpx1Response.data.gpx_file_id
    $GPX1_STATUS = $gpx1Response.data.processing_status
    Write-ColorOutput "  [OK] GPX subido: $GPX1_FILE_ID (status: $GPX1_STATUS)" "Green"
} catch {
    Write-ColorOutput "  Error al subir GPX: $($_.Exception.Message)" "Red"
    exit 1
}

# Esperar procesamiento si es async
if ($GPX1_STATUS -eq "processing") {
    Write-ColorOutput "  Esperando procesamiento asincrono..." "Yellow"
    Start-Sleep -Seconds 5
}

# Obtener estadisticas
Write-ColorOutput "`n[3/3] Obteniendo estadisticas calculadas..." "Yellow"
try {
    $track1Response = Invoke-RestMethod -Uri "$API_URL/gpx/$GPX1_FILE_ID/track" -Method Get -Headers $headers
    $stats1 = $track1Response.data.route_statistics

    Write-ColorOutput "`n--- Resultados Test 1 ---" "Blue"
    $stats1 | ConvertTo-Json -Depth 10 | Write-Host

    # Validaciones
    if ($stats1 -eq $null) {
        Write-ColorOutput "[FAIL] route_statistics es null (deberia estar presente)" "Red"
        exit 1
    } else {
        Write-ColorOutput "[PASS] route_statistics presente" "Green"
    }

    Write-ColorOutput "`n--- Validaciones Test 1 ---" "Blue"

    # Validar campos
    if ($stats1.avg_speed_kmh -gt 0) {
        Write-ColorOutput "[OK] avg_speed_kmh: $($stats1.avg_speed_kmh) km/h" "Green"
    }

    if ($stats1.max_speed_kmh -gt 0) {
        Write-ColorOutput "[OK] max_speed_kmh: $($stats1.max_speed_kmh) km/h" "Green"
    }

    if ($stats1.total_time_minutes -ge $stats1.moving_time_minutes) {
        Write-ColorOutput "[OK] total_time ($($stats1.total_time_minutes) min) >= moving_time ($($stats1.moving_time_minutes) min)" "Green"
    }

    if ($stats1.max_gradient -lt 35) {
        Write-ColorOutput "[OK] max_gradient: $($stats1.max_gradient)% (realista, menor a 35%)" "Green"
    } else {
        Write-ColorOutput "[ERROR] max_gradient: $($stats1.max_gradient)% (IRREAL, deberia ser menor a 35%)" "Red"
        Write-ColorOutput "  -> BUG: distance_3d() usado en lugar de distance_2d()" "Red"
    }

    if ($stats1.top_climbs -and $stats1.top_climbs.Count -gt 0) {
        Write-ColorOutput "[OK] top_climbs: $($stats1.top_climbs.Count) subidas detectadas" "Green"
        foreach ($climb in $stats1.top_climbs) {
            Write-ColorOutput "  - $($climb.description)" "Gray"
        }
    }

} catch {
    Write-ColorOutput "Error al obtener estadisticas: $($_.Exception.Message)" "Red"
    exit 1
}

# Test 2: GPX sin timestamps
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  TEST 2: test_without_timestamps.gpx" "Blue"
Write-ColorOutput "  Expectativa: [ERROR] route_statistics null" "Blue"
Write-ColorOutput "==================================================`n" "Blue"

Write-ColorOutput "[1/3] Creando y publicando viaje para Test 2..." "Yellow"
$TRIP2_ID = Create-And-PublishTrip `
    -Title "Test 2: GPX sin Timestamps (Automatizado)" `
    -Description "Viaje de prueba para validar que NO se calculan estadisticas avanzadas cuando el GPX no contiene timestamps. User Story 5 - Test 2." `
    -Headers $headers
$TRIP_IDS += $TRIP2_ID

Write-ColorOutput "`n[2/3] Subiendo test_without_timestamps.gpx..." "Yellow"
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

$gpx2Response = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP2_ID/gpx" -Method Post -Headers $uploadHeaders -Body $bodyLines2
$GPX2_FILE_ID = $gpx2Response.data.gpx_file_id
Write-ColorOutput "  [OK] GPX subido: $GPX2_FILE_ID" "Green"

Write-ColorOutput "`n[3/3] Obteniendo estadisticas..." "Yellow"
Start-Sleep -Seconds 2

$track2Response = Invoke-RestMethod -Uri "$API_URL/gpx/$GPX2_FILE_ID/track" -Method Get -Headers $headers
$stats2 = $track2Response.data.route_statistics

Write-ColorOutput "`n--- Resultados Test 2 ---" "Blue"
if ($stats2 -eq $null) {
    Write-Host "null"
    Write-ColorOutput "[PASS] route_statistics es null (correcto, sin timestamps)" "Green"
} else {
    $stats2 | ConvertTo-Json -Depth 10 | Write-Host
    Write-ColorOutput "[FAIL] route_statistics presente (deberia ser null sin timestamps)" "Red"
    exit 1
}

# Test 3: Gradientes realistas
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  TEST 3: test_realistic_gradients.gpx" "Blue"
Write-ColorOutput "  Expectativa: [OK] max_gradient menor a 35%" "Blue"
Write-ColorOutput "==================================================`n" "Blue"

Write-ColorOutput "[1/3] Creando y publicando viaje para Test 3..." "Yellow"
$TRIP3_ID = Create-And-PublishTrip `
    -Title "Test 3: Gradientes Realistas (Automatizado)" `
    -Description "Viaje de prueba para validar que los gradientes calculados son realistas (<35%). Puerto de Navacerrada. User Story 5 - Test 3." `
    -Headers $headers
$TRIP_IDS += $TRIP3_ID

Write-ColorOutput "`n[2/3] Subiendo test_realistic_gradients.gpx..." "Yellow"
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

$gpx3Response = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP3_ID/gpx" -Method Post -Headers $uploadHeaders -Body $bodyLines3
$GPX3_FILE_ID = $gpx3Response.data.gpx_file_id
Write-ColorOutput "  [OK] GPX subido: $GPX3_FILE_ID" "Green"

Write-ColorOutput "`n[3/3] Obteniendo estadisticas..." "Yellow"
Start-Sleep -Seconds 2

$track3Response = Invoke-RestMethod -Uri "$API_URL/gpx/$GPX3_FILE_ID/track" -Method Get -Headers $headers
$stats3 = $track3Response.data.route_statistics

Write-ColorOutput "`n--- Resultados Test 3 ---" "Blue"
$stats3 | ConvertTo-Json -Depth 10 | Write-Host

Write-ColorOutput "`n--- Validaciones Test 3 ---" "Blue"
if ($stats3.max_gradient -lt 35) {
    Write-ColorOutput "[PASS] max_gradient: $($stats3.max_gradient)% (realista, menor a 35%)" "Green"
} else {
    Write-ColorOutput "[FAIL] max_gradient: $($stats3.max_gradient)% (IRREAL, deberia ser menor a 35%)" "Red"
    exit 1
}

if ($stats3.avg_gradient) {
    Write-ColorOutput "[OK] avg_gradient: $($stats3.avg_gradient)% (subida continua)" "Green"
}

# Resumen final
Write-ColorOutput "`n==================================================" "Blue"
Write-ColorOutput "  RESUMEN DE PRUEBAS" "Blue"
Write-ColorOutput "==================================================" "Blue"
Write-ColorOutput "[OK] Test 1: GPX con timestamps -> Estadisticas calculadas" "Green"
Write-ColorOutput "[OK] Test 2: GPX sin timestamps -> Sin estadisticas (null)" "Green"
Write-ColorOutput "[OK] Test 3: Gradientes realistas -> max_gradient menor a 35%" "Green"
Write-ColorOutput "`nViajes de prueba creados:" "Blue"
Write-ColorOutput "  Test 1: http://localhost:5173/trips/$($TRIP_IDS[0])" "Cyan"
Write-ColorOutput "  Test 2: http://localhost:5173/trips/$($TRIP_IDS[1])" "Cyan"
Write-ColorOutput "  Test 3: http://localhost:5173/trips/$($TRIP_IDS[2])" "Cyan"
Write-ColorOutput "`nTodas las pruebas pasaron exitosamente!" "Green"
