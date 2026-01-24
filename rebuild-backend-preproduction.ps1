# Script PowerShell para reconstruir la imagen del backend en modo preproduction
# con los cambios temporales para seeding

$COMPOSE_FILES = "-f", "docker-compose.preproduction.yml", "-f", "docker-compose.preproduction.build.yml"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🔧 Reconstruyendo Backend - Modo Preproduction" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Detener contenedores actuales
Write-Host "1️⃣ Deteniendo contenedores actuales..." -ForegroundColor Yellow
docker compose -f docker-compose.preproduction.yml down
Write-Host "✅ Contenedores detenidos" -ForegroundColor Green
Write-Host ""

# Paso 2: Reconstruir imagen backend (sin caché para forzar cambios)
Write-Host "2️⃣ Reconstruyendo imagen del backend..." -ForegroundColor Yellow
Write-Host "   - Usando overlay: docker-compose.preproduction.build.yml" -ForegroundColor Gray
Write-Host "   - Copiando pyproject.toml y poetry.lock" -ForegroundColor Gray
Write-Host "   - Habilitando init_dev_data.py en production" -ForegroundColor Gray
& docker compose @COMPOSE_FILES build --no-cache backend
Write-Host "✅ Imagen reconstruida" -ForegroundColor Green
Write-Host ""

# Paso 3: Iniciar servicios
Write-Host "3️⃣ Iniciando servicios..." -ForegroundColor Yellow
& docker compose @COMPOSE_FILES up -d
Write-Host "✅ Servicios iniciados" -ForegroundColor Green
Write-Host ""

# Paso 4: Esperar a que los servicios estén listos
Write-Host "4️⃣ Esperando a que los servicios estén saludables (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host ""

# Paso 5: Verificar estado
Write-Host "5️⃣ Estado de los servicios:" -ForegroundColor Yellow
docker compose -f docker-compose.preproduction.yml ps
Write-Host ""

# Paso 6: Mostrar logs del backend (últimas 50 líneas)
Write-Host "6️⃣ Logs del backend (últimas 50 líneas):" -ForegroundColor Yellow
docker compose -f docker-compose.preproduction.yml logs --tail=50 backend
Write-Host ""

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "✅ Reconstrucción completada" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Cambios aplicados:" -ForegroundColor White
Write-Host "   ✓ pyproject.toml y poetry.lock copiados a /app" -ForegroundColor Green
Write-Host "   ✓ init_dev_data.py se ejecutará en APP_ENV=production" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Acceso:" -ForegroundColor White
Write-Host "   - Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   - pgAdmin: http://localhost:5050" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  RECORDATORIO: Revertir cambios temporales después de pruebas" -ForegroundColor Yellow
Write-Host "   - backend/Dockerfile líneas 98-99" -ForegroundColor Gray
Write-Host "   - backend/scripts/docker-entrypoint.sh línea 18" -ForegroundColor Gray
Write-Host "   - backend/scripts/init_dev_data.py líneas 37-42" -ForegroundColor Gray
Write-Host ""
Write-Host "📝 Comandos útiles:" -ForegroundColor White
Write-Host "   Ver logs en tiempo real:" -ForegroundColor Gray
Write-Host "     docker compose -f docker-compose.preproduction.yml logs -f backend" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   Reiniciar solo backend:" -ForegroundColor Gray
Write-Host "     docker compose -f docker-compose.preproduction.yml restart backend" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   Ejecutar script manualmente dentro del contenedor:" -ForegroundColor Gray
Write-Host "     docker compose -f docker-compose.preproduction.yml exec backend python scripts/init_dev_data.py" -ForegroundColor DarkGray
Write-Host ""
