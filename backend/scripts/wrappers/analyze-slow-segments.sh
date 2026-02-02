#!/bin/bash
#
# analyze-slow-segments.sh - Analizar distribución de duración de segmentos lentos
#
# DESCRIPCIÓN:
#   Genera un histograma de duración de segmentos lentos (< 3 km/h) en un GPX.
#   Clasifica los segmentos en rangos de duración:
#   - 0-30 segundos (semáforos, cruces)
#   - 30-60 segundos (semáforos largos)
#   - 1-2 minutos (paradas breves)
#   - 2-5 minutos (paradas cortas)
#   - >5 minutos (paradas largas)
#
# USO:
#   ./analyze-slow-segments.sh <gpx_file_id>
#   ./analyze-slow-segments.sh --file-path <ruta>
#
# PARÁMETROS:
#   gpx_file_id    UUID del archivo GPX a analizar (modo database)
#   --file-path    Ruta al archivo GPX (modo archivo directo)
#
# EJEMPLOS:
#   # Modo 1: Buscar en base de datos y storage
#   ./analyze-slow-segments.sh 13e24f2f-f792-4873-b636-ad3568861514
#
#   # Modo 2: Usar archivo en ubicación personalizada
#   ./analyze-slow-segments.sh --file-path /tmp/my-route.gpx
#
# SALIDA:
#   - Total de segmentos lentos y tiempo total
#   - Estadísticas: promedio, máximo, mínimo de duración
#   - Histograma de duración por rango
#   - TOP 10 segmentos lentos más largos
#
# NOTAS:
#   - Requiere que el GPX tenga timestamps (has_timestamps=true)
#   - Solo analiza segmentos con velocidad < 3 km/h
#   - Útil para entender distribución de paradas (semáforos vs paradas largas)
#
# MODOS DE OPERACIÓN:
#   1. Modo Database (solo gpx_file_id):
#      - Busca gpx_file_id en tabla gpx_files
#      - Lee archivo desde storage_path + file_url
#      - Requiere que el GPX esté cargado en la base de datos
#      Ejemplo: ./analyze-slow-segments.sh 13e24f2f-f792-4873-b636-ad3568861514
#
#   2. Modo File Path (solo --file-path):
#      - Lee archivo directamente desde la ruta especificada
#      - NO consulta la base de datos
#      - NO requiere gpx_file_id
#      - Útil para analizar GPX sin cargarlos en la base de datos
#      Ejemplo: ./analyze-slow-segments.sh --file-path /tmp/my-route.gpx
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
echo -e "${GREEN}Slow Segments Duration Analysis${NC}"
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
    poetry run python scripts/analysis/analyze_slow_segments.py --file-path "$FILE_PATH"
else
    poetry run python scripts/analysis/analyze_slow_segments.py "$GPX_FILE_ID"
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
