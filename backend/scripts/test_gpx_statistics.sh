#!/bin/bash

###############################################################################
# GPX Statistics Testing Script (User Story 5 - Advanced Statistics)
#
# Este script automatiza la validación de estadísticas avanzadas de rutas GPX
# probando los 3 archivos GPX de prueba contra el API.
#
# Requisitos:
# - Backend corriendo en http://localhost:8000
# - Usuario de prueba creado (testuser / TestPass123!)
# - jq instalado (para parsear JSON)
#
# Uso:
#   bash scripts/test_gpx_statistics.sh
###############################################################################

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
API_URL="http://localhost:8000"
USERNAME="testuser"
PASSWORD="TestPass123!"
GPX_DIR="test_data"

# Función auxiliar para crear y publicar viajes
create_and_publish_trip() {
    local title=$1
    local description=$2

    TRIP_RESPONSE=$(curl -s -X POST "$API_URL/trips" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"title\": \"$title\",
        \"description\": \"$description\",
        \"start_date\": \"2024-06-15\",
        \"distance_km\": 25.0
      }")

    TRIP_ID=$(echo "$TRIP_RESPONSE" | jq -r '.data.trip_id')

    if [ "$TRIP_ID" == "null" ]; then
        echo -e "${RED}  Error: No se pudo crear el viaje.${NC}"
        exit 1
    fi

    echo -e "${GREEN}  ✓ Viaje creado con ID: $TRIP_ID${NC}"

    # Publicar viaje
    PUBLISH_RESPONSE=$(curl -s -X POST "$API_URL/trips/$TRIP_ID/publish" \
      -H "Authorization: Bearer $ACCESS_TOKEN")

    PUBLISH_STATUS=$(echo "$PUBLISH_RESPONSE" | jq -r '.data.status')

    if [ "$PUBLISH_STATUS" != "published" ]; then
        echo -e "${RED}  Error: No se pudo publicar el viaje.${NC}"
        exit 1
    fi

    echo -e "${GREEN}  ✓ Viaje publicado correctamente${NC}"
    echo "$TRIP_ID"
}

# Banner
echo -e "${BLUE}"
echo "=================================================="
echo "  GPX Statistics Testing Script (User Story 5)"
echo "=================================================="
echo -e "${NC}"

# Verificar dependencias
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq no está instalado. Instala con: apt install jq (Linux) o brew install jq (Mac)${NC}"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl no está instalado.${NC}"
    exit 1
fi

# Verificar que el backend está corriendo
echo -e "${YELLOW}[1/2] Verificando backend...${NC}"
if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}Error: Backend no está corriendo en $API_URL${NC}"
    echo "Inicia el backend con: poetry run uvicorn src.main:app --reload"
    exit 1
fi
echo -e "${GREEN}✓ Backend activo en $API_URL${NC}"

# Autenticación
echo -e "${YELLOW}[2/2] Autenticando usuario...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"login\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

if [ -z "$LOGIN_RESPONSE" ]; then
    echo -e "${RED}Error: No se pudo autenticar. Verifica que el usuario existe.${NC}"
    echo "Crea el usuario con: poetry run python scripts/create_verified_user.py"
    exit 1
fi

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.access_token')

if [ "$ACCESS_TOKEN" == "null" ]; then
    echo -e "${RED}Error: Login falló. Respuesta del servidor:${NC}"
    echo "$LOGIN_RESPONSE" | jq '.'
    exit 1
fi

echo -e "${GREEN}✓ Autenticación exitosa (token obtenido)${NC}"

# Array para almacenar los trip IDs creados
TRIP_IDS=()

# Test 1: GPX con timestamps (debe generar estadísticas)
echo ""
echo -e "${BLUE}=================================================="
echo "  TEST 1: test_with_timestamps.gpx"
echo "  Expectativa: ✓ route_statistics presente"
echo -e "==================================================${NC}"

echo -e "${YELLOW}[1/3] Creando y publicando viaje para Test 1...${NC}"
TRIP1_ID=$(create_and_publish_trip "Test 1: GPX con Timestamps (Automatizado)" "Viaje de prueba para validar calculo de estadisticas avanzadas con GPX que contiene timestamps. User Story 5 - Test 1.")
TRIP_IDS+=("$TRIP1_ID")

echo ""
echo -e "${YELLOW}[2/3] Subiendo test_with_timestamps.gpx...${NC}"
GPX1_RESPONSE=$(curl -s -X POST "$API_URL/trips/$TRIP1_ID/gpx" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@$GPX_DIR/test_with_timestamps.gpx")

GPX1_FILE_ID=$(echo "$GPX1_RESPONSE" | jq -r '.data.gpx_file_id')
GPX1_STATUS=$(echo "$GPX1_RESPONSE" | jq -r '.data.processing_status')

echo -e "${GREEN}✓ GPX subido: $GPX1_FILE_ID (status: $GPX1_STATUS)${NC}"

# Esperar procesamiento (si es async)
if [ "$GPX1_STATUS" == "processing" ]; then
    echo -e "${YELLOW}Esperando procesamiento asíncrono...${NC}"
    sleep 5
fi

# Obtener trackdata con estadísticas
echo ""
echo -e "${YELLOW}[3/3] Obteniendo estadísticas calculadas...${NC}"
TRACK1_RESPONSE=$(curl -s -X GET "$API_URL/gpx/$GPX1_FILE_ID/track" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

STATS1=$(echo "$TRACK1_RESPONSE" | jq '.data.route_statistics')

echo ""
echo -e "${BLUE}--- Resultados Test 1 ---${NC}"
echo "$STATS1" | jq '.'

# Validaciones Test 1
HAS_STATS=$(echo "$STATS1" | jq 'type')
if [ "$HAS_STATS" == "null" ]; then
    echo -e "${RED}✗ FAIL: route_statistics es null (debería estar presente)${NC}"
    exit 1
else
    echo -e "${GREEN}✓ PASS: route_statistics presente${NC}"
fi

# Validar campos individuales
AVG_SPEED=$(echo "$STATS1" | jq -r '.avg_speed_kmh')
MAX_SPEED=$(echo "$STATS1" | jq -r '.max_speed_kmh')
TOTAL_TIME=$(echo "$STATS1" | jq -r '.total_time_minutes')
MOVING_TIME=$(echo "$STATS1" | jq -r '.moving_time_minutes')
MAX_GRADIENT=$(echo "$STATS1" | jq -r '.max_gradient')
TOP_CLIMBS=$(echo "$STATS1" | jq '.top_climbs | length')

echo ""
echo -e "${BLUE}--- Validaciones Test 1 ---${NC}"

# Validar avg_speed_kmh
if [ "$AVG_SPEED" != "null" ] && [ "$(echo "$AVG_SPEED > 0" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓ avg_speed_kmh: $AVG_SPEED km/h${NC}"
else
    echo -e "${RED}✗ avg_speed_kmh inválido: $AVG_SPEED${NC}"
fi

# Validar max_speed_kmh
if [ "$MAX_SPEED" != "null" ] && [ "$(echo "$MAX_SPEED > 0" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓ max_speed_kmh: $MAX_SPEED km/h${NC}"
else
    echo -e "${RED}✗ max_speed_kmh inválido: $MAX_SPEED${NC}"
fi

# Validar total_time > moving_time
if [ "$(echo "$TOTAL_TIME >= $MOVING_TIME" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓ total_time ($TOTAL_TIME min) >= moving_time ($MOVING_TIME min)${NC}"
else
    echo -e "${RED}✗ total_time ($TOTAL_TIME) < moving_time ($MOVING_TIME) - INVÁLIDO${NC}"
fi

# Validar max_gradient realista (< 35%)
if [ "$MAX_GRADIENT" != "null" ] && [ "$(echo "$MAX_GRADIENT < 35" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓ max_gradient: $MAX_GRADIENT% (realista, < 35%)${NC}"
else
    echo -e "${RED}✗ max_gradient: $MAX_GRADIENT% (IRREAL, debería ser < 35%)${NC}"
    echo -e "${RED}  → BUG: distance_3d() usado en lugar de distance_2d()${NC}"
fi

# Validar top_climbs
if [ "$TOP_CLIMBS" != "null" ] && [ "$TOP_CLIMBS" -gt 0 ]; then
    echo -e "${GREEN}✓ top_climbs: $TOP_CLIMBS subidas detectadas${NC}"
    echo "$STATS1" | jq -r '.top_climbs[] | "  - \(.description)"'
else
    echo -e "${YELLOW}⚠ top_climbs: ninguna subida detectada${NC}"
fi

# Test 2: GPX sin timestamps (NO debe generar estadísticas)
echo ""
echo -e "${BLUE}=================================================="
echo "  TEST 2: test_without_timestamps.gpx"
echo "  Expectativa: ✗ route_statistics null"
echo -e "==================================================${NC}"

echo -e "${YELLOW}[1/3] Creando y publicando viaje para Test 2...${NC}"
TRIP2_ID=$(create_and_publish_trip "Test 2: GPX sin Timestamps (Automatizado)" "Viaje de prueba para validar que NO se calculan estadisticas avanzadas cuando el GPX no contiene timestamps. User Story 5 - Test 2.")
TRIP_IDS+=("$TRIP2_ID")

echo ""
echo -e "${YELLOW}[2/3] Subiendo test_without_timestamps.gpx...${NC}"
GPX2_RESPONSE=$(curl -s -X POST "$API_URL/trips/$TRIP2_ID/gpx" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@$GPX_DIR/test_without_timestamps.gpx")

GPX2_FILE_ID=$(echo "$GPX2_RESPONSE" | jq -r '.data.gpx_file_id')
GPX2_STATUS=$(echo "$GPX2_RESPONSE" | jq -r '.data.processing_status')

echo -e "${GREEN}✓ GPX subido: $GPX2_FILE_ID (status: $GPX2_STATUS)${NC}"

# Esperar procesamiento
if [ "$GPX2_STATUS" == "processing" ]; then
    echo -e "${YELLOW}Esperando procesamiento asíncrono...${NC}"
    sleep 5
fi

# Obtener trackdata
echo ""
echo -e "${YELLOW}[3/3] Obteniendo estadísticas...${NC}"
TRACK2_RESPONSE=$(curl -s -X GET "$API_URL/gpx/$GPX2_FILE_ID/track" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

STATS2=$(echo "$TRACK2_RESPONSE" | jq '.data.route_statistics')

echo ""
echo -e "${BLUE}--- Resultados Test 2 ---${NC}"
echo "$STATS2" | jq '.'

# Validación Test 2
HAS_STATS2=$(echo "$STATS2" | jq 'type')
if [ "$HAS_STATS2" == "null" ]; then
    echo -e "${GREEN}✓ PASS: route_statistics es null (correcto, sin timestamps)${NC}"
else
    echo -e "${RED}✗ FAIL: route_statistics presente (debería ser null sin timestamps)${NC}"
    exit 1
fi

# Test 3: GPX con gradientes realistas
echo ""
echo -e "${BLUE}=================================================="
echo "  TEST 3: test_realistic_gradients.gpx"
echo "  Expectativa: ✓ max_gradient < 35%"
echo -e "==================================================${NC}"

echo -e "${YELLOW}[1/3] Creando y publicando viaje para Test 3...${NC}"
TRIP3_ID=$(create_and_publish_trip "Test 3: Gradientes Realistas (Automatizado)" "Viaje de prueba para validar que los gradientes calculados son realistas (<35%). Puerto de Navacerrada. User Story 5 - Test 3.")
TRIP_IDS+=("$TRIP3_ID")

echo ""
echo -e "${YELLOW}[2/3] Subiendo test_realistic_gradients.gpx...${NC}"
GPX3_RESPONSE=$(curl -s -X POST "$API_URL/trips/$TRIP3_ID/gpx" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@$GPX_DIR/test_realistic_gradients.gpx")

GPX3_FILE_ID=$(echo "$GPX3_RESPONSE" | jq -r '.data.gpx_file_id')
GPX3_STATUS=$(echo "$GPX3_RESPONSE" | jq -r '.data.processing_status')

echo -e "${GREEN}✓ GPX subido: $GPX3_FILE_ID (status: $GPX3_STATUS)${NC}"

# Esperar procesamiento
if [ "$GPX3_STATUS" == "processing" ]; then
    echo -e "${YELLOW}Esperando procesamiento asíncrono...${NC}"
    sleep 5
fi

# Obtener trackdata
echo ""
echo -e "${YELLOW}[3/3] Obteniendo estadísticas...${NC}"
TRACK3_RESPONSE=$(curl -s -X GET "$API_URL/gpx/$GPX3_FILE_ID/track" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

STATS3=$(echo "$TRACK3_RESPONSE" | jq '.data.route_statistics')

echo ""
echo -e "${BLUE}--- Resultados Test 3 ---${NC}"
echo "$STATS3" | jq '.'

# Validación Test 3
MAX_GRADIENT3=$(echo "$STATS3" | jq -r '.max_gradient')
AVG_GRADIENT3=$(echo "$STATS3" | jq -r '.avg_gradient')

echo ""
echo -e "${BLUE}--- Validaciones Test 3 ---${NC}"

if [ "$MAX_GRADIENT3" != "null" ] && [ "$(echo "$MAX_GRADIENT3 < 35" | bc)" -eq 1 ]; then
    echo -e "${GREEN}✓ PASS: max_gradient: $MAX_GRADIENT3% (realista, < 35%)${NC}"
else
    echo -e "${RED}✗ FAIL: max_gradient: $MAX_GRADIENT3% (IRREAL, debería ser < 35%)${NC}"
    exit 1
fi

if [ "$AVG_GRADIENT3" != "null" ]; then
    echo -e "${GREEN}✓ avg_gradient: $AVG_GRADIENT3% (subida continua)${NC}"
fi

# Resumen final
echo ""
echo -e "${BLUE}=================================================="
echo "  RESUMEN DE PRUEBAS"
echo -e "==================================================${NC}"
echo -e "${GREEN}✓ Test 1: GPX con timestamps → Estadísticas calculadas${NC}"
echo -e "${GREEN}✓ Test 2: GPX sin timestamps → Sin estadísticas (null)${NC}"
echo -e "${GREEN}✓ Test 3: Gradientes realistas → max_gradient < 35%${NC}"
echo ""
echo -e "${BLUE}Viajes de prueba creados:${NC}"
echo -e "${CYAN}  Test 1: http://localhost:5173/trips/${TRIP_IDS[0]}${NC}"
echo -e "${CYAN}  Test 2: http://localhost:5173/trips/${TRIP_IDS[1]}${NC}"
echo -e "${CYAN}  Test 3: http://localhost:5173/trips/${TRIP_IDS[2]}${NC}"
echo ""
echo -e "${GREEN}¡Todas las pruebas pasaron exitosamente! ✓${NC}"
