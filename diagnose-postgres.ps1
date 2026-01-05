# Diagnóstico completo de PostgreSQL
# Este script verifica exactamente qué está pasando con Docker y PostgreSQL

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Diagnóstico PostgreSQL - ContraVento" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar contenedores Docker
Write-Host "1. Contenedores Docker:" -ForegroundColor Yellow
docker ps -a --filter "name=contravento-db" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 2. Verificar volúmenes Docker
Write-Host "2. Volúmenes Docker:" -ForegroundColor Yellow
docker volume ls | Select-String "postgres"
Write-Host ""

# 3. Verificar variables de entorno en backend/.env
Write-Host "3. Variables en backend/.env:" -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    Write-Host "   Archivo backend\.env existe" -ForegroundColor Green
    Get-Content "backend\.env" | Select-String "POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD|DATABASE_URL" | ForEach-Object {
        $line = $_.Line
        # Ocultar password parcialmente
        if ($line -match "PASSWORD") {
            $line = $line -replace '=.*', '=***'
        }
        Write-Host "   $line" -ForegroundColor White
    }
} else {
    Write-Host "   ⚠️  backend\.env NO existe" -ForegroundColor Red
}
Write-Host ""

# 4. Ver logs del contenedor PostgreSQL
Write-Host "4. Últimos logs de PostgreSQL (init):" -ForegroundColor Yellow
docker logs contravento-db 2>&1 | Select-String "database system is ready|PostgreSQL init|NOTICE|ERROR|FATAL" | Select-Object -Last 10
Write-Host ""

# 5. Verificar qué base de datos y usuarios existen REALMENTE en el contenedor
Write-Host "5. Bases de datos en el contenedor:" -ForegroundColor Yellow
docker exec contravento-db psql -U postgres -c "\l" 2>&1
Write-Host ""

Write-Host "6. Usuarios en el contenedor:" -ForegroundColor Yellow
docker exec contravento-db psql -U postgres -c "\du" 2>&1
Write-Host ""

# 7. Intentar conectar con diferentes usuarios
Write-Host "7. Pruebas de conexión:" -ForegroundColor Yellow

Write-Host "   Probando: postgres (superuser)..." -ForegroundColor Gray
$result1 = docker exec contravento-db psql -U postgres -c "SELECT current_user;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ postgres funciona" -ForegroundColor Green
} else {
    Write-Host "   ❌ postgres falló" -ForegroundColor Red
}

Write-Host "   Probando: contravento_user (default)..." -ForegroundColor Gray
$result2 = docker exec contravento-db psql -U contravento_user -d contravento -c "SELECT current_user;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ contravento_user funciona" -ForegroundColor Green
    Write-Host "   ⚠️  PROBLEMA: El contenedor se creó con usuario DEFAULT, no con contravento_test" -ForegroundColor Red
} else {
    Write-Host "   ❌ contravento_user no existe (esperado si usaste .env)" -ForegroundColor Yellow
}

Write-Host "   Probando: contravento_test (testing)..." -ForegroundColor Gray
$result3 = docker exec contravento-db psql -U contravento_test -d contravento_test -c "SELECT current_user;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ contravento_test funciona - CORRECTO" -ForegroundColor Green
} else {
    Write-Host "   ❌ contravento_test falló" -ForegroundColor Red
    Write-Host "   Error: $result3" -ForegroundColor Red
}
Write-Host ""

# 8. Verificar variables de entorno DENTRO del contenedor
Write-Host "8. Variables de entorno del contenedor PostgreSQL:" -ForegroundColor Yellow
docker exec contravento-db env | Select-String "POSTGRES_"
Write-Host ""

# 9. Recomendaciones
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO COMPLETO" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($result3 -match "contravento_test") {
    Write-Host "✅ PostgreSQL está configurado CORRECTAMENTE" -ForegroundColor Green
    Write-Host ""
    Write-Host "El problema puede ser:" -ForegroundColor Yellow
    Write-Host "1. La PASSWORD está mal en backend/.env" -ForegroundColor White
    Write-Host "2. Alembic está usando una DATABASE_URL diferente" -ForegroundColor White
    Write-Host ""
    Write-Host "Solución:" -ForegroundColor Green
    Write-Host "cd backend" -ForegroundColor Gray
    Write-Host "poetry run python scripts/test-postgres-connection.py" -ForegroundColor Gray
} else {
    Write-Host "❌ PostgreSQL está configurado INCORRECTAMENTE" -ForegroundColor Red
    Write-Host ""
    Write-Host "El contenedor se creó con credenciales DEFAULT." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solución:" -ForegroundColor Green
    Write-Host "1. Detener y eliminar TODO:" -ForegroundColor White
    Write-Host "   docker-compose down -v" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Verificar que backend/.env existe y tiene:" -ForegroundColor White
    Write-Host "   POSTGRES_DB=contravento_test" -ForegroundColor Gray
    Write-Host "   POSTGRES_USER=contravento_test" -ForegroundColor Gray
    Write-Host "   POSTGRES_PASSWORD=test_password" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Recrear con --env-file:" -ForegroundColor White
    Write-Host "   docker-compose --env-file backend/.env up postgres -d" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Esperar 10 segundos y verificar:" -ForegroundColor White
    Write-Host "   docker exec contravento-db psql -U contravento_test -d contravento_test -c 'SELECT current_user;'" -ForegroundColor Gray
}
Write-Host ""
