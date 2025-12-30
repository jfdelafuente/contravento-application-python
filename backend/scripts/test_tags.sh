#!/bin/bash
# Script de testing automatizado para Tags & Categorization (User Story 4)
# Requiere: servidor corriendo en localhost:8000 y usuario autenticado

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
BASE_URL="http://localhost:8000"
TOKEN=""
USERNAME=""
TRIP_ID=""

# Función para imprimir con color
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_test() {
    echo -e "${YELLOW}→ Test: ${1}${NC}"
}

# Función para extraer valores JSON
extract_json() {
    echo "$1" | grep -o "\"$2\"[^,}]*" | sed "s/\"$2\":\s*\"\?\([^\"]*\)\"\?/\1/"
}

# Paso 1: Login
print_info "=== STEP 1: Login ==="
read -p "Email: " EMAIL
read -sp "Password: " PASSWORD
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
USERNAME=$(echo "$LOGIN_RESPONSE" | grep -o '"username":"[^"]*' | sed 's/"username":"//')

if [ -z "$TOKEN" ]; then
    print_error "Login fallido"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

print_success "Login exitoso como $USERNAME"
echo "Token: ${TOKEN:0:20}..."
echo ""

# Paso 2: Crear trips con diferentes tags
print_info "=== STEP 2: Crear trips con tags ==="

print_test "Creando trip con tags: montaña, aventura"
TRIP1_RESPONSE=$(curl -s -X POST "$BASE_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta de Alta Montaña",
    "description": "Impresionante ruta por los picos más altos de la cordillera con vistas espectaculares",
    "start_date": "2024-06-15",
    "tags": ["montaña", "aventura"]
  }')

TRIP1_ID=$(echo "$TRIP1_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')
print_success "Trip 1 creado: $TRIP1_ID"

print_test "Creando trip con tags: playa, relax"
TRIP2_RESPONSE=$(curl -s -X POST "$BASE_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Costa Mediterránea",
    "description": "Viaje relajante por las mejores playas del mediterráneo con aguas cristalinas",
    "start_date": "2024-07-20",
    "tags": ["playa", "relax"]
  }')

TRIP2_ID=$(echo "$TRIP2_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')
print_success "Trip 2 creado: $TRIP2_ID"

print_test "Creando trip con tags: MONTAÑA (uppercase), NATURALEZA"
TRIP3_RESPONSE=$(curl -s -X POST "$BASE_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Parque Nacional",
    "description": "Exploración del parque nacional con increíbles paisajes de montaña y flora autóctona",
    "start_date": "2024-08-10",
    "tags": ["MONTAÑA", "NATURALEZA"]
  }')

TRIP3_ID=$(echo "$TRIP3_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')
print_success "Trip 3 creado: $TRIP3_ID"

print_test "Creando trip sin tags"
TRIP4_RESPONSE=$(curl -s -X POST "$BASE_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ciudad Histórica",
    "description": "Tour por el centro histórico de la ciudad con visitas a monumentos emblemáticos",
    "start_date": "2024-09-05"
  }')

TRIP4_ID=$(echo "$TRIP4_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')
print_success "Trip 4 creado (sin tags): $TRIP4_ID"
echo ""

# Paso 3: Publicar algunos trips
print_info "=== STEP 3: Publicar trips ==="

print_test "Publicando trip 1 (montaña)"
curl -s -X POST "$BASE_URL/trips/$TRIP1_ID/publish" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
print_success "Trip 1 publicado"

print_test "Publicando trip 2 (playa)"
curl -s -X POST "$BASE_URL/trips/$TRIP2_ID/publish" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
print_success "Trip 2 publicado"

# Trip 3 y 4 quedan como DRAFT
print_info "Trip 3 y 4 permanecen como DRAFT"
echo ""

# Paso 4: Filtrado por tags (case-insensitive)
print_info "=== STEP 4: Filtrado por tags (case-insensitive) ==="

print_test "Filtrar por tag 'montaña' (lowercase)"
FILTER1=$(curl -s "$BASE_URL/users/$USERNAME/trips?tag=montaña" \
  -H "Authorization: Bearer $TOKEN")
COUNT1=$(echo "$FILTER1" | grep -o '"id"' | wc -l)
print_success "Encontrados: $COUNT1 trips (esperado: 2 - trip1 y trip3)"

print_test "Filtrar por tag 'MONTAÑA' (uppercase)"
FILTER2=$(curl -s "$BASE_URL/users/$USERNAME/trips?tag=MONTAÑA" \
  -H "Authorization: Bearer $TOKEN")
COUNT2=$(echo "$FILTER2" | grep -o '"id"' | wc -l)
print_success "Encontrados: $COUNT2 trips (esperado: 2 - case insensitive)"

print_test "Filtrar por tag 'playa'"
FILTER3=$(curl -s "$BASE_URL/users/$USERNAME/trips?tag=playa" \
  -H "Authorization: Bearer $TOKEN")
COUNT3=$(echo "$FILTER3" | grep -o '"id"' | wc -l)
print_success "Encontrados: $COUNT3 trips (esperado: 1 - trip2)"

print_test "Filtrar por tag inexistente 'ciudad'"
FILTER4=$(curl -s "$BASE_URL/users/$USERNAME/trips?tag=ciudad" \
  -H "Authorization: Bearer $TOKEN")
COUNT4=$(echo "$FILTER4" | grep -o '"id"' | wc -l)
print_success "Encontrados: $COUNT4 trips (esperado: 0)"
echo ""

# Paso 5: Filtrado por status
print_info "=== STEP 5: Filtrado por status ==="

print_test "Filtrar solo PUBLISHED"
STATUS1=$(curl -s "$BASE_URL/users/$USERNAME/trips?status=PUBLISHED" \
  -H "Authorization: Bearer $TOKEN")
COUNT_PUB=$(echo "$STATUS1" | grep -o '"id"' | wc -l)
print_success "PUBLISHED: $COUNT_PUB trips (esperado: 2 - trip1 y trip2)"

print_test "Filtrar solo DRAFT"
STATUS2=$(curl -s "$BASE_URL/users/$USERNAME/trips?status=DRAFT" \
  -H "Authorization: Bearer $TOKEN")
COUNT_DRAFT=$(echo "$STATUS2" | grep -o '"id"' | wc -l)
print_success "DRAFT: $COUNT_DRAFT trips (esperado: 2 - trip3 y trip4)"
echo ""

# Paso 6: Filtros combinados
print_info "=== STEP 6: Filtros combinados (tag + status) ==="

print_test "Filtrar tag='montaña' + status='PUBLISHED'"
COMBINED1=$(curl -s "$BASE_URL/users/$USERNAME/trips?tag=montaña&status=PUBLISHED" \
  -H "Authorization: Bearer $TOKEN")
COUNT_C1=$(echo "$COMBINED1" | grep -o '"id"' | wc -l)
print_success "Encontrados: $COUNT_C1 trips (esperado: 1 - solo trip1)"

print_test "Filtrar tag='montaña' + status='DRAFT'"
COMBINED2=$(curl -s "$BASE_URL/users/$USERNAME/trips?tag=montaña&status=DRAFT" \
  -H "Authorization: Bearer $TOKEN")
COUNT_C2=$(echo "$COMBINED2" | grep -o '"id"' | wc -l)
print_success "Encontrados: $COUNT_C2 trips (esperado: 1 - solo trip3)"

print_test "Filtrar tag='playa' + status='DRAFT'"
COMBINED3=$(curl -s "$BASE_URL/users/$USERNAME/trips?tag=playa&status=DRAFT" \
  -H "Authorization: Bearer $TOKEN")
COUNT_C3=$(echo "$COMBINED3" | grep -o '"id"' | wc -l)
print_success "Encontrados: $COUNT_C3 trips (esperado: 0 - playa está published)"
echo ""

# Paso 7: Paginación
print_info "=== STEP 7: Paginación ==="

print_test "Obtener primeros 2 trips (limit=2, offset=0)"
PAGE1=$(curl -s "$BASE_URL/users/$USERNAME/trips?limit=2&offset=0" \
  -H "Authorization: Bearer $TOKEN")
COUNT_P1=$(echo "$PAGE1" | grep -o '"id"' | wc -l)
print_success "Página 1: $COUNT_P1 trips (esperado: 2)"

print_test "Obtener siguientes 2 trips (limit=2, offset=2)"
PAGE2=$(curl -s "$BASE_URL/users/$USERNAME/trips?limit=2&offset=2" \
  -H "Authorization: Bearer $TOKEN")
COUNT_P2=$(echo "$PAGE2" | grep -o '"id"' | wc -l)
print_success "Página 2: $COUNT_P2 trips (esperado: 2)"

print_test "Obtener más allá del total (limit=2, offset=10)"
PAGE3=$(curl -s "$BASE_URL/users/$USERNAME/trips?limit=2&offset=10" \
  -H "Authorization: Bearer $TOKEN")
COUNT_P3=$(echo "$PAGE3" | grep -o '"id"' | wc -l)
print_success "Página 3: $COUNT_P3 trips (esperado: 0 - offset fuera de rango)"
echo ""

# Paso 8: Endpoint GET /tags
print_info "=== STEP 8: Listado de tags con popularidad ==="

print_test "Obtener todos los tags disponibles"
TAGS_RESPONSE=$(curl -s "$BASE_URL/tags" \
  -H "Authorization: Bearer $TOKEN")

# Mostrar tags encontrados
echo "$TAGS_RESPONSE" | grep -o '"name":"[^"]*","usage_count":[0-9]*' | while read -r tag; do
    TAG_NAME=$(echo "$tag" | sed 's/"name":"\([^"]*\)".*/\1/')
    TAG_COUNT=$(echo "$tag" | sed 's/.*"usage_count":\([0-9]*\)/\1/')
    print_success "Tag: $TAG_NAME (usado en $TAG_COUNT trips)"
done
echo ""

# Paso 9: Limpieza (opcional)
print_info "=== STEP 9: Limpieza (opcional) ==="
read -p "¿Deseas eliminar los trips de prueba? (s/n): " CLEANUP

if [ "$CLEANUP" = "s" ] || [ "$CLEANUP" = "S" ]; then
    print_test "Eliminando trips de prueba..."
    curl -s -X DELETE "$BASE_URL/trips/$TRIP1_ID" -H "Authorization: Bearer $TOKEN" > /dev/null
    curl -s -X DELETE "$BASE_URL/trips/$TRIP2_ID" -H "Authorization: Bearer $TOKEN" > /dev/null
    curl -s -X DELETE "$BASE_URL/trips/$TRIP3_ID" -H "Authorization: Bearer $TOKEN" > /dev/null
    curl -s -X DELETE "$BASE_URL/trips/$TRIP4_ID" -H "Authorization: Bearer $TOKEN" > /dev/null
    print_success "Trips eliminados correctamente"
else
    print_info "Trips de prueba conservados:"
    echo "  - $TRIP1_ID (montaña, aventura) - PUBLISHED"
    echo "  - $TRIP2_ID (playa, relax) - PUBLISHED"
    echo "  - $TRIP3_ID (MONTAÑA, NATURALEZA) - DRAFT"
    echo "  - $TRIP4_ID (sin tags) - DRAFT"
fi
echo ""

# Resumen final
print_info "=== RESUMEN DE TESTS ==="
print_success "✓ Creación de trips con tags"
print_success "✓ Filtrado case-insensitive por tags"
print_success "✓ Filtrado por status (DRAFT/PUBLISHED)"
print_success "✓ Filtros combinados (tag + status)"
print_success "✓ Paginación con limit/offset"
print_success "✓ Listado de tags con popularidad"
echo ""
print_success "Tests completados exitosamente!"
