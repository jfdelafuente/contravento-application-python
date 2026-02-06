#!/bin/bash
#
# delete-stats.sh - Eliminar RouteStatistics corruptas o no deseadas
#
# DESCRIPCIÓN:
#   Elimina el registro RouteStatistics de un archivo GPX específico.
#   Originalmente creado para eliminar registros corruptos con moving_time > total_time,
#   pero puede usarse para eliminar cualquier RouteStatistics que necesite ser removido.
#   Útil para:
#   - Eliminar estadísticas corruptas (moving_time > total_time)
#   - Limpiar estadísticas incorrectas antes de recalcular
#   - Eliminar estadísticas de GPX que serán re-procesados
#   - Preparar para backfill de estadísticas
#
# USO:
#   ./delete-stats.sh <gpx_file_id>
#
# PARÁMETROS:
#   gpx_file_id    UUID del archivo GPX cuyas RouteStatistics se eliminarán
#
# EJEMPLOS:
#   ./delete-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
#
# SALIDA:
#   Si existe RouteStatistics:
#   - Información del registro (Stats ID, GPX File ID, Total Time, Moving Time)
#   - Mensaje de error si datos corruptos detectados
#   - Confirmación de eliminación exitosa
#
#   Si NO existe RouteStatistics:
#   - Mensaje informativo (no hay registro para eliminar)
#
# NOTAS:
#   - Solo elimina de tabla route_statistics (NO elimina GPX file ni trackpoints)
#   - Muestra información del registro antes de eliminar
#   - Hace commit inmediato (NO hay prompt de confirmación)
#   - Usa recalculate-stats.sh para recrear estadísticas después de eliminar
#   - CUIDADO: Operación destructiva sin opción de deshacer
#
# MODO DE OPERACIÓN:
#   Modo Database (único modo disponible):
#   - Busca gpx_file_id en tabla route_statistics
#   - Si existe, muestra información y elimina registro
#   - Hace commit de la transacción
#   - NO requiere que el GPX file exista en storage
#   Ejemplo: ./delete-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
#
# WORKFLOW TÍPICO:
#   1. ./delete-stats.sh <gpx_file_id>        # Eliminar estadísticas corruptas
#   2. ./recalculate-stats.sh <gpx_file_id>   # Recalcular estadísticas correctas
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
echo -e "${GREEN}RouteStatistics Deletion${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Mode:        Database"
echo "GPX File ID: $GPX_FILE_ID"
echo "Timestamp:   $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo -e "${RED}⚠️  WARNING: This will PERMANENTLY DELETE RouteStatistics (no undo!)${NC}"
echo ""

# Change to backend directory
cd "$PROJECT_ROOT/backend"

# Run deletion script
echo -e "${GREEN}Deleting RouteStatistics...${NC}"
echo ""

poetry run python scripts/analysis/delete_corrupt_stats.py "$GPX_FILE_ID"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Deletion completed successfully${NC}"
    echo ""
    echo "Next steps:"
    echo "  - To recreate statistics: ./scripts/wrappers/recalculate-stats.sh $GPX_FILE_ID"
else
    echo ""
    echo -e "${RED}✗ Deletion failed with exit code $exit_code${NC}"
    exit $exit_code
fi
