# Script para crear viajes de prueba en ContraVento
# Uso: .\create_test_trips.ps1

# Backend URL (configurable via env var)
$BaseUrl = if ($env:BACKEND_URL) { $env:BACKEND_URL } else { "http://localhost:8000" }

Write-Host "🔐 Iniciando sesión como testuser..." -ForegroundColor Cyan

# Login
$loginBody = @{
    username = "testuser"
    password = "TestPass123!"
} | ConvertTo-Json

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$loginResponse = Invoke-WebRequest `
    -Uri "$BaseUrl/auth/login" `
    -Method POST `
    -Body $loginBody `
    -ContentType "application/json" `
    -WebSession $session `
    -ErrorAction Stop

Write-Host "✅ Sesión iniciada`n" -ForegroundColor Green

# Viaje 1
Write-Host "📝 Creando viaje 1: Vía Verde del Aceite..." -ForegroundColor Yellow
$trip1 = @{
    title = "Vía Verde del Aceite - Jaén a Córdoba"
    description = @"
Un recorrido espectacular por la antigua vía del tren del aceite.

Esta ruta atraviesa olivares centenarios, puentes históricos y túneles excavados en roca. El paisaje es impresionante durante todo el año, pero especialmente hermoso en primavera cuando los olivos están en flor.

Incluye paradas en pueblos con encanto como Alcaudete, Luque y Baena. La ruta es mayormente llana y asfaltada, perfecta para ciclistas de todos los niveles.
"@
    start_date = "2025-11-10"
    end_date = "2025-11-12"
    distance_km = 128.5
    difficulty = "moderate"
    tags = @("vías verdes", "aceite", "andalucía")
} | ConvertTo-Json

$response1 = Invoke-RestMethod `
    -Uri "$BaseUrl/trips" `
    -Method POST `
    -Body $trip1 `
    -ContentType "application/json; charset=utf-8" `
    -WebSession $session

Write-Host "  ✓ Creado: $($response1.data.trip.title)" -ForegroundColor Green
$trip1Id = $response1.data.trip.trip_id

# Publicar viaje 1
Invoke-RestMethod `
    -Uri "$BaseUrl/trips/$trip1Id/publish" `
    -Method POST `
    -WebSession $session | Out-Null
Write-Host "  ✓ Publicado`n" -ForegroundColor Green

# Viaje 2
Write-Host "📝 Creando viaje 2: Ruta Bikepacking Pirineos..." -ForegroundColor Yellow
$trip2 = @{
    title = "Ruta Bikepacking Pirineos - Valle de Ordesa"
    description = @"
Aventura de 5 días por el corazón de los Pirineos aragoneses con acampada libre.

El Valle de Ordesa es uno de los lugares más espectaculares de España para hacer bikepacking. Esta ruta combina senderos técnicos, pistas forestales y carreteras secundarias de montaña.

Dificultad técnica alta debido a los desniveles acumulados (+8000m) y algunas secciones de sendero expuesto. Recomendado solo para ciclistas con experiencia en montaña.
"@
    start_date = "2025-10-15"
    end_date = "2025-10-19"
    distance_km = 320.0
    difficulty = "difficult"
    tags = @("bikepacking", "montaña", "pirineos")
} | ConvertTo-Json

$response2 = Invoke-RestMethod `
    -Uri "$BaseUrl/trips" `
    -Method POST `
    -Body $trip2 `
    -ContentType "application/json; charset=utf-8" `
    -WebSession $session

Write-Host "  ✓ Creado: $($response2.data.trip.title)" -ForegroundColor Green
$trip2Id = $response2.data.trip.trip_id

# Publicar viaje 2
Invoke-RestMethod `
    -Uri "$BaseUrl/trips/$trip2Id/publish" `
    -Method POST `
    -WebSession $session | Out-Null
Write-Host "  ✓ Publicado`n" -ForegroundColor Green

# Viaje 3
Write-Host "📝 Creando viaje 3: Camino de Santiago..." -ForegroundColor Yellow
$trip3 = @{
    title = "Camino de Santiago en Bici - Etapa León a Astorga"
    description = @"
Primera etapa de mi Camino Francés en bicicleta. Salida desde la catedral de León hasta Astorga.

Ruta bien señalizada siguiendo las flechas amarillas del Camino. Terreno mixto: asfalto, pista de tierra y algún tramo de sendero.

Conocí peregrinos de todo el mundo. La energía del Camino es única, diferente a cualquier otra ruta ciclista.
"@
    start_date = "2025-12-25"
    end_date = "2025-12-25"
    distance_km = 52.0
    difficulty = "easy"
    tags = @("camino de santiago", "cultural")
} | ConvertTo-Json

$response3 = Invoke-RestMethod `
    -Uri "$BaseUrl/trips" `
    -Method POST `
    -Body $trip3 `
    -ContentType "application/json; charset=utf-8" `
    -WebSession $session

Write-Host "  ✓ Creado: $($response3.data.trip.title)" -ForegroundColor Green
$trip3Id = $response3.data.trip.trip_id

# Publicar viaje 3
Invoke-RestMethod `
    -Uri "$BaseUrl/trips/$trip3Id/publish" `
    -Method POST `
    -WebSession $session | Out-Null
Write-Host "  ✓ Publicado`n" -ForegroundColor Green

# Viaje 4 (borrador)
Write-Host "📝 Creando viaje 4: Borrador Transpirenaica..." -ForegroundColor Yellow
$trip4 = @{
    title = "Borrador: Planificando la Transpirenaica"
    description = "Proyecto en desarrollo para cruzar los Pirineos de mar a mar. Aproximadamente 800km."
    start_date = "2026-06-01"
    end_date = "2026-06-15"
    distance_km = 800.0
    difficulty = "extreme"
    tags = @("transpirenaica", "proyecto")
} | ConvertTo-Json

$response4 = Invoke-RestMethod `
    -Uri "$BaseUrl/trips" `
    -Method POST `
    -Body $trip4 `
    -ContentType "application/json; charset=utf-8" `
    -WebSession $session

Write-Host "  ✓ Creado (BORRADOR): $($response4.data.trip.title)`n" -ForegroundColor Gray

Write-Host "✅ ¡Viajes creados exitosamente!" -ForegroundColor Green
Write-Host "🌐 Ver en: http://localhost:3001/trips" -ForegroundColor Cyan
Write-Host ""
Write-Host "IDs de los viajes:" -ForegroundColor Yellow
Write-Host "  1. $trip1Id" -ForegroundColor White
Write-Host "  2. $trip2Id" -ForegroundColor White
Write-Host "  3. $trip3Id" -ForegroundColor White
Write-Host "  4. $($response4.data.trip.trip_id)" -ForegroundColor Gray
