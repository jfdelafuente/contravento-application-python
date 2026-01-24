#!/bin/bash
# Script para reconstruir la imagen del backend en modo preproduction
# con los cambios temporales para seeding

set -e

COMPOSE_FILES="-f docker-compose.preproduction.yml -f docker-compose.preproduction.build.yml"

echo "=========================================================="
echo "🔧 Reconstruyendo Backend - Modo Preproduction"
echo "=========================================================="
echo ""

# Paso 1: Detener contenedores actuales
echo "1️⃣ Deteniendo contenedores actuales..."
docker compose -f docker-compose.preproduction.yml down
echo "✅ Contenedores detenidos"
echo ""

# Paso 2: Reconstruir imagen backend (sin caché para forzar cambios)
echo "2️⃣ Reconstruyendo imagen del backend..."
echo "   - Usando overlay: docker-compose.preproduction.build.yml"
echo "   - Copiando pyproject.toml y poetry.lock"
echo "   - Habilitando init_dev_data.py en production"
docker compose $COMPOSE_FILES build --no-cache backend
echo "✅ Imagen reconstruida"
echo ""

# Paso 3: Iniciar servicios
echo "3️⃣ Iniciando servicios..."
docker compose $COMPOSE_FILES up -d
echo "✅ Servicios iniciados"
echo ""

# Paso 4: Esperar a que los servicios estén listos
echo "4️⃣ Esperando a que los servicios estén saludables (30s)..."
sleep 30
echo ""

# Paso 5: Verificar estado
echo "5️⃣ Estado de los servicios:"
docker compose -f docker-compose.preproduction.yml ps
echo ""

# Paso 6: Mostrar logs del backend (últimas 50 líneas)
echo "6️⃣ Logs del backend (últimas 50 líneas):"
docker compose -f docker-compose.preproduction.yml logs --tail=50 backend
echo ""

echo "=========================================================="
echo "✅ Reconstrucción completada"
echo "=========================================================="
echo ""
echo "📋 Cambios aplicados:"
echo "   ✓ pyproject.toml y poetry.lock copiados a /app"
echo "   ✓ init_dev_data.py se ejecutará en APP_ENV=production"
echo ""
echo "🌐 Acceso:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - pgAdmin: http://localhost:5050"
echo ""
echo "⚠️  RECORDATORIO: Revertir cambios temporales después de pruebas"
echo "   - backend/Dockerfile líneas 98-99"
echo "   - backend/scripts/docker-entrypoint.sh línea 18"
echo "   - backend/scripts/init_dev_data.py líneas 37-42"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs en tiempo real:"
echo "     docker compose -f docker-compose.preproduction.yml logs -f backend"
echo ""
echo "   Reiniciar solo backend:"
echo "     docker compose -f docker-compose.preproduction.yml restart backend"
echo ""
echo "   Ejecutar script manualmente dentro del contenedor:"
echo "     docker compose -f docker-compose.preproduction.yml exec backend python scripts/init_dev_data.py"
echo ""
