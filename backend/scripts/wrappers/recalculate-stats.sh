#!/bin/bash
#
# recalculate-stats.sh - Recalcular RouteStatistics para un GPX existente
#
# DESCRIPCIÓN:
#   Recalcula las estadísticas de ruta (RouteStatistics) para un archivo GPX
#   que ya está en la base de datos, sin necesidad de volver a subirlo.
#   Útil para:
#   - Actualizar estadísticas después de cambios en el algoritmo de cálculo
#   - Corregir estadísticas incorrectas o corruptas
#   - Recalcular después de ajustes en los thresholds de stop detection
#   - Backfill de estadísticas para GPX subidos antes de la integración
#
# USO:
#   ./recalculate-stats.sh <gpx_file_id>
#
# PARÁMETROS:
#   gpx_file_id    UUID del archivo GPX a recalcular (modo database)
#
# EJEMPLOS:
#   ./recalculate-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
#
# SALIDA:
#   - Información del GPX file (ID, distancia, file_url)
#   - Información del archivo leído desde storage (tamaño en bytes)
#   - Datos parseados del GPX (total points, distancia, timestamps, elevación)
#   - Mensaje de eliminación del RouteStatistics existente (si existe)
#   - Métricas calculadas:
#     * Velocidad (avg_speed, max_speed)
#     * Tiempo (total_time, moving_time, stopped_time, moving/total ratio)
#     * Gradiente (avg_gradient, max_gradient)
#     * Subidas (top climbs con distancia, ganancia elevación, gradiente)
#   - Stats ID del nuevo RouteStatistics creado
#
# NOTAS:
#   - Requiere que el GPX esté en la base de datos (tabla gpx_files)
#   - Requiere que el GPX esté en el storage (storage_path + file_url)
#   - Requiere que el GPX tenga timestamps (has_timestamps=true)
#   - Elimina el RouteStatistics existente y crea uno nuevo (NO es update in-place)
#   - CUIDADO: Esto sobrescribe las estadísticas existentes sin confirmación
#
# MODO DE OPERACIÓN:
#   Modo Database (único modo disponible):
#   - Busca gpx_file_id en tabla gpx_files
#   - Lee archivo GPX desde storage_path + file_url
#   - Parsea GPX y calcula todas las métricas de ruta
#   - Elimina RouteStatistics existente (si hay)
#   - Crea nuevo RouteStatistics con métricas recalculadas
#   Ejemplo: ./recalculate-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
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
echo -e "${GREEN}RouteStatistics Recalculation${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Mode:        Database"
echo "GPX File ID: $GPX_FILE_ID"
echo "Timestamp:   $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will DELETE existing RouteStatistics and create a new one${NC}"
echo ""

# Change to backend directory
cd "$PROJECT_ROOT/backend"

# Run recalculation script
echo -e "${GREEN}Recalculating RouteStatistics...${NC}"
echo ""

poetry run python scripts/analysis/recalculate_route_stats.py "$GPX_FILE_ID"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Recalculation completed successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ Recalculation failed with exit code $exit_code${NC}"
    exit $exit_code
fi
