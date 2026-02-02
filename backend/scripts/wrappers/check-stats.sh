#!/bin/bash
#
# check-stats.sh - Verificar existencia de RouteStatistics para un GPX
#
# DESCRIPCIÓN:
#   Consulta la tabla RouteStatistics para verificar si las estadísticas
#   de ruta han sido calculadas para un archivo GPX específico.
#   Útil para:
#   - Verificar si un GPX tiene estadísticas calculadas
#   - Ver métricas de velocidad, tiempo, gradiente y subidas
#   - Diagnosticar GPX subidos antes de la integración de RouteStatistics
#
# USO:
#   ./check-stats.sh <gpx_file_id>
#
# PARÁMETROS:
#   gpx_file_id    UUID del archivo GPX a verificar (modo database)
#
# EJEMPLOS:
#   ./check-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
#
# SALIDA:
#   Si EXISTE RouteStatistics:
#   - Stats ID y GPX File ID
#   - Métricas de velocidad (avg, max)
#   - Métricas de tiempo (total, moving)
#   - Métricas de gradiente (avg, max)
#   - Lista de top climbs con distancia, ganancia de elevación y gradiente
#
#   Si NO EXISTE RouteStatistics:
#   - Mensaje de error con razón (GPX subido antes de integración)
#   - Soluciones sugeridas (re-upload o backfill script)
#
# NOTAS:
#   - Solo consulta la base de datos (tabla route_statistics)
#   - NO parsea archivos GPX directamente
#   - Requiere que el GPX esté registrado en la tabla gpx_files
#   - Las estadísticas se calculan automáticamente al subir un GPX
#
# MODO DE OPERACIÓN:
#   Modo Database (único modo disponible):
#   - Busca gpx_file_id en tabla route_statistics
#   - Muestra métricas si existen
#   - Muestra mensaje de error si no existen
#   Ejemplo: ./check-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Validate arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: GPX file ID is required${NC}"
    echo ""
    echo "Usage:"
    echo "  $0 <gpx_file_id>"
    echo ""
    echo "Example:"
    echo "  $0 13e24f2f-f792-4873-b636-ad3568861514"
    exit 1
fi

# Parse arguments
GPX_FILE_ID="$1"

# Validate UUID format (basic check)
if ! [[ "$GPX_FILE_ID" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
    echo -e "${YELLOW}Warning: '$GPX_FILE_ID' doesn't look like a valid UUID${NC}"
    echo "Continuing anyway..."
    echo ""
fi

# Print header
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}RouteStatistics Existence Check${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Mode:        Database"
echo "GPX File ID: $GPX_FILE_ID"
echo "Timestamp:   $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Change to backend directory
cd "$PROJECT_ROOT/backend"

# Run check script
echo -e "${GREEN}Checking RouteStatistics...${NC}"
echo ""

poetry run python scripts/analysis/check_route_stats.py "$GPX_FILE_ID"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Check completed successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ Check failed with exit code $exit_code${NC}"
    exit $exit_code
fi
