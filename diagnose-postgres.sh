#!/bin/bash
# Diagnóstico completo de PostgreSQL
# Este script verifica exactamente qué está pasando con Docker y PostgreSQL

set -e

echo "========================================="
echo "Diagnóstico PostgreSQL - ContraVento"
echo "========================================="
echo ""

# 1. Verificar contenedores Docker
echo "1. Contenedores Docker:"
docker ps -a --filter "name=contravento-db" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true
echo ""

# 2. Verificar volúmenes Docker
echo "2. Volúmenes Docker:"
docker volume ls | grep postgres || echo "   No se encontraron volúmenes de postgres"
echo ""

# 3. Verificar variables de entorno en backend/.env
echo "3. Variables en backend/.env:"
if [ -f "backend/.env" ]; then
    echo "   ✅ Archivo backend/.env existe"
    grep -E "POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD|DATABASE_URL" backend/.env | sed 's/PASSWORD=.*/PASSWORD=***/' || true
else
    echo "   ⚠️  backend/.env NO existe"
fi
echo ""

# 4. Ver logs del contenedor PostgreSQL
echo "4. Últimos logs de PostgreSQL (init):"
docker logs contravento-db 2>&1 | grep -E "database system is ready|PostgreSQL init|NOTICE|ERROR|FATAL" | tail -10 || echo "   No se pudieron obtener logs"
echo ""

# 5. Verificar qué base de datos y usuarios existen REALMENTE en el contenedor
echo "5. Bases de datos en el contenedor:"
docker exec contravento-db psql -U postgres -c "\l" 2>&1 || echo "   ⚠️  No se pudo conectar como postgres"
echo ""

echo "6. Usuarios en el contenedor:"
docker exec contravento-db psql -U postgres -c "\du" 2>&1 || echo "   ⚠️  No se pudo conectar como postgres"
echo ""

# 7. Intentar conectar con diferentes usuarios
echo "7. Pruebas de conexión:"

echo "   Probando: postgres (superuser)..."
if docker exec contravento-db psql -U postgres -c "SELECT current_user;" >/dev/null 2>&1; then
    echo "   ✅ postgres funciona"
else
    echo "   ❌ postgres falló"
fi

echo "   Probando: contravento_user (default)..."
if docker exec contravento-db psql -U contravento_user -d contravento -c "SELECT current_user;" >/dev/null 2>&1; then
    echo "   ✅ contravento_user funciona"
    echo "   ⚠️  PROBLEMA: El contenedor se creó con usuario DEFAULT, no con contravento_test"
else
    echo "   ❌ contravento_user no existe (esperado si usaste .env)"
fi

echo "   Probando: contravento_test (testing)..."
if docker exec contravento-db psql -U contravento_test -d contravento_test -c "SELECT current_user;" >/dev/null 2>&1; then
    echo "   ✅ contravento_test funciona - CORRECTO"
    TEST_USER_OK=true
else
    echo "   ❌ contravento_test falló"
    docker exec contravento-db psql -U contravento_test -d contravento_test -c "SELECT current_user;" 2>&1 | head -5
    TEST_USER_OK=false
fi
echo ""

# 8. Verificar variables de entorno DENTRO del contenedor
echo "8. Variables de entorno del contenedor PostgreSQL:"
docker exec contravento-db env | grep "^POSTGRES_" || echo "   No se encontraron variables POSTGRES_*"
echo ""

# 9. Recomendaciones
echo "========================================="
echo "DIAGNÓSTICO COMPLETO"
echo "========================================="
echo ""

if [ "$TEST_USER_OK" = true ]; then
    echo "✅ PostgreSQL está configurado CORRECTAMENTE"
    echo ""
    echo "El problema puede ser:"
    echo "1. La PASSWORD está mal en backend/.env"
    echo "2. Alembic está usando una DATABASE_URL diferente"
    echo ""
    echo "Solución:"
    echo "cd backend"
    echo "poetry run python scripts/test-postgres-connection.py"
else
    echo "❌ PostgreSQL está configurado INCORRECTAMENTE"
    echo ""
    echo "El contenedor se creó con credenciales DEFAULT."
    echo ""
    echo "Solución:"
    echo "1. Detener y eliminar TODO:"
    echo "   docker-compose down -v"
    echo ""
    echo "2. Verificar que backend/.env existe y tiene:"
    echo "   POSTGRES_DB=contravento_test"
    echo "   POSTGRES_USER=contravento_test"
    echo "   POSTGRES_PASSWORD=test_password"
    echo ""
    echo "3. Recrear con --env-file:"
    echo "   docker-compose --env-file backend/.env up postgres -d"
    echo ""
    echo "4. Esperar 10 segundos y verificar:"
    echo "   sleep 10"
    echo "   docker exec contravento-db psql -U contravento_test -d contravento_test -c 'SELECT current_user;'"
fi
echo ""
