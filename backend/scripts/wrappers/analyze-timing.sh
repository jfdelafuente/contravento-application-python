#!/bin/bash
#
# analyze-timing.sh - Analizar espaciado entre puntos GPS
#
# DESCRIPCIÓN:
#   Analiza el espaciado de distancia entre puntos GPS consecutivos.
#   Útil para detectar:
#   - Gaps grandes (>0.5km) que pueden indicar datos perdidos
#   - Densidad de puntos GPS (avg distance/point)
#   - Calidad del tracking GPS
#
# USO:
#   ./analyze-timing.sh <gpx_file_id>
#   ./analyze-timing.sh --file-path <ruta>
#
# PARÁMETROS:
#   gpx_file_id    UUID del archivo GPX a analizar (modo database)
#   --file-path    Ruta al archivo GPX (modo archivo directo)
#
# EJEMPLOS:
#   # Modo 1: Buscar en base de datos y storage
#   ./analyze-timing.sh 13e24f2f-f792-4873-b636-ad3568861514
#
#   # Modo 2: Usar archivo en ubicación personalizada
#   ./analyze-timing.sh --file-path /tmp/my-route.gpx
#
# SALIDA:
#   - Total de puntos GPS analizados
#   - Muestra de espaciado entre primeros y últimos 20 puntos
#   - Estadísticas: promedio, mínimo, máximo de distancia entre puntos
#   - Alertas de gaps grandes (>0.5km)
#
# NOTAS:
#   - Útil para validar calidad del tracking GPS
#   - Gaps grandes pueden indicar túneles, pérdida de señal, etc.
#   - Un avg distance/point bajo indica buen tracking GPS
#
# MODOS DE OPERACIÓN:
#   1. Modo Database (solo gpx_file_id):
#      - Busca gpx_file_id en tabla gpx_files
#      - Lee trackpoints desde tabla track_points
#      - Requiere que el GPX esté cargado en la base de datos
#      Ejemplo: ./analyze-timing.sh 13e24f2f-f792-4873-b636-ad3568861514
#
#   2. Modo File Path (solo --file-path):
#      - Lee archivo directamente desde la ruta especificada
#      - Parsea GPX y analiza spacing sin consultar DB
#      - NO requiere gpx_file_id
#      - Útil para analizar GPX sin cargarlos en la base de datos
#      Ejemplo: ./analyze-timing.sh --file-path /tmp/my-route.gpx
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
    echo -e "${RED}Error: GPX file ID or --file-path is required${NC}"
    echo ""
    echo "Usage:"
    echo "  $0 <gpx_file_id>"
    echo "  $0 --file-path <ruta>"
    echo ""
    echo "Examples:"
    echo "  # Modo 1: Buscar en base de datos"
    echo "  $0 13e24f2f-f792-4873-b636-ad3568861514"
    echo ""
    echo "  # Modo 2: Usar archivo personalizado"
    echo "  $0 --file-path /tmp/my-route.gpx"
    exit 1
fi

# Parse arguments
GPX_FILE_ID=""
FILE_PATH=""

# Check if first argument is --file-path
if [ "$1" = "--file-path" ]; then
    if [ -z "$2" ]; then
        echo -e "${RED}Error: --file-path requires a path argument${NC}"
        exit 1
    fi
    FILE_PATH="$2"
else
    # First argument is gpx_file_id
    GPX_FILE_ID="$1"

    # Validate UUID format (basic check)
    if ! [[ "$GPX_FILE_ID" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
        echo -e "${YELLOW}Warning: '$GPX_FILE_ID' doesn't look like a valid UUID${NC}"
        echo "Continuing anyway..."
        echo ""
    fi
fi

# Print header
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GPS Point Spacing Analysis${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
if [ -n "$FILE_PATH" ]; then
    echo "Mode:        File Path"
    echo "File Path:   $FILE_PATH"
else
    echo "Mode:        Database"
    echo "GPX File ID: $GPX_FILE_ID"
fi
echo "Timestamp:   $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Change to backend directory
cd "$PROJECT_ROOT/backend"

# Run analysis script
echo -e "${GREEN}Running analysis...${NC}"
echo ""

if [ -n "$FILE_PATH" ]; then
    poetry run python scripts/analysis/analyze_gpx_timing.py --file-path "$FILE_PATH"
else
    poetry run python scripts/analysis/analyze_gpx_timing.py "$GPX_FILE_ID"
fi

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Analysis completed successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ Analysis failed with exit code $exit_code${NC}"
    exit $exit_code
fi
