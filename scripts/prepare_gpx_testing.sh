#!/bin/bash
# Script para preparar entorno de testing manual GPX
# Feature 003 - GPS Routes Interactive

set -e

# Colores
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Funciones
setup_user() {
    echo -e "${YELLOW}>>> Creando usuario de prueba...${NC}"

    cd backend
    poetry run python scripts/create_verified_user.py \
        --username "testgpx" \
        --email "testgpx@example.com" \
        --password "TestGPX123!" || echo -e "${YELLOW}⚠️  Usuario ya existe o error${NC}"
    cd ..

    echo -e "${GREEN}✅ Usuario creado: testgpx / TestGPX123!${NC}"
}

copy_files() {
    echo -e "${YELLOW}>>> Copiando archivos GPX de prueba...${NC}"

    # Crear carpeta temporal
    TEST_DIR="test-gpx-files"
    if [ -d "$TEST_DIR" ]; then
        echo -e "${YELLOW}⚠️  Carpeta $TEST_DIR ya existe, limpiando...${NC}"
        rm -rf "$TEST_DIR"
    fi

    mkdir -p "$TEST_DIR"

    # Copiar archivos
    FIXTURES="backend/tests/fixtures/gpx"

    cp "$FIXTURES/short_route.gpx" "$TEST_DIR/"
    cp "$FIXTURES/camino_del_cid.gpx" "$TEST_DIR/"
    cp "$FIXTURES/long_route_5mb.gpx" "$TEST_DIR/"
    cp "$FIXTURES/no_elevation.gpx" "$TEST_DIR/"
    cp "$FIXTURES/invalid_gpx.xml" "$TEST_DIR/"

    echo -e "${GREEN}✅ Archivos copiados a: $TEST_DIR/${NC}"
    ls -lh "$TEST_DIR"
}

check_database() {
    echo -e "${YELLOW}>>> Verificando estado de la base de datos...${NC}"

    cd backend
    poetry run python <<EOF
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
EOF
    cd ..

    echo ""
    echo -e "${GREEN}✅ Base de datos verificada${NC}"
}

create_oversized_file() {
    echo -e "${YELLOW}>>> Creando archivo de prueba >10MB...${NC}"

    TEST_DIR="test-gpx-files"
    mkdir -p "$TEST_DIR"

    # Crear archivo de 11MB
    dd if=/dev/zero of="$TEST_DIR/oversized.gpx" bs=1M count=11 2>/dev/null

    SIZE=$(du -h "$TEST_DIR/oversized.gpx" | cut -f1)
    echo -e "${GREEN}✅ Archivo creado: oversized.gpx ($SIZE)${NC}"
}

show_help() {
    echo -e "${CYAN}Uso:${NC}"
    echo "  ./scripts/prepare_gpx_testing.sh [opción]"
    echo ""
    echo "Opciones:"
    echo "  all           Ejecutar todo"
    echo "  user          Solo crear usuario"
    echo "  files         Solo copiar archivos"
    echo "  db            Solo verificar BD"
    echo "  help          Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  # Preparación completa para testing manual"
    echo "  ./scripts/prepare_gpx_testing.sh all"
    echo ""
    echo "  # Solo copiar archivos GPX de prueba"
    echo "  ./scripts/prepare_gpx_testing.sh files"
    echo ""
}

# Main
echo -e "${CYAN}==================================================${NC}"
echo -e "${CYAN}  GPX Manual Testing - Preparation Script${NC}"
echo -e "${CYAN}==================================================${NC}"
echo ""

case "${1:-help}" in
    all)
        setup_user
        echo ""
        copy_files
        echo ""
        check_database
        ;;
    user)
        setup_user
        ;;
    files)
        copy_files
        ;;
    db)
        check_database
        ;;
    help|*)
        show_help
        ;;
esac

echo ""
echo -e "${CYAN}==================================================${NC}"
echo -e "${GREEN}Siguiente paso: Revisar MANUAL_TESTING.md${NC}"
echo -e "${GRAY}  specs/003-gps-routes/MANUAL_TESTING.md${NC}"
echo -e "${CYAN}==================================================${NC}"
