#!/bin/bash

# Script de limpieza de archivos temporales para ContraVento
# Uso: ./cleanup-temp.sh

echo ""
echo "========================================"
echo " Limpieza de Archivos Temporales"
echo "========================================"
echo ""

# Archivos de log
echo "[1/7] Eliminando archivos de log..."
count=$(find . -name "*.log" -type f 2>/dev/null | wc -l)
if [ "$count" -gt 0 ]; then
    find . -name "*.log" -type f -delete 2>/dev/null
    echo "      -> $count archivo(s) eliminado(s)"
else
    echo "      -> No se encontraron archivos"
fi

# Cache de Python
echo "[2/7] Eliminando cache de Python..."
pycache=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
pyc=$(find . -name "*.pyc" -type f 2>/dev/null | wc -l)
pyo=$(find . -name "*.pyo" -type f 2>/dev/null | wc -l)
total_py=$((pycache + pyc + pyo))
if [ "$total_py" -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -type f -delete 2>/dev/null
    find . -name "*.pyo" -type f -delete 2>/dev/null
    echo "      -> $total_py elemento(s) eliminado(s)"
else
    echo "      -> No se encontraron archivos"
fi

# Cache de pytest
echo "[3/7] Eliminando cache de pytest..."
count=$(find . -type d -name ".pytest_cache" 2>/dev/null | wc -l)
if [ "$count" -gt 0 ]; then
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
    echo "      -> $count directorio(s) eliminado(s)"
else
    echo "      -> No se encontraron directorios"
fi

# Cache de mypy
echo "[4/7] Eliminando cache de mypy..."
count=$(find . -type d -name ".mypy_cache" 2>/dev/null | wc -l)
if [ "$count" -gt 0 ]; then
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
    echo "      -> $count directorio(s) eliminado(s)"
else
    echo "      -> No se encontraron directorios"
fi

# Archivos de coverage
echo "[5/7] Eliminando archivos de coverage..."
coverage=$(find . -name ".coverage" -type f 2>/dev/null | wc -l)
coverage_xml=$(find . -name "coverage.xml" -type f 2>/dev/null | wc -l)
htmlcov=$(find . -type d -name "htmlcov" 2>/dev/null | wc -l)
total_cov=$((coverage + coverage_xml + htmlcov))
if [ "$total_cov" -gt 0 ]; then
    find . -name ".coverage" -type f -delete 2>/dev/null
    find . -name "coverage.xml" -type f -delete 2>/dev/null
    find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null
    echo "      -> $total_cov elemento(s) eliminado(s)"
else
    echo "      -> No se encontraron archivos"
fi

# Egg info y archivos temporales de Claude
echo "[6/7] Eliminando egg-info y temporales..."
egg_info=$(find . -type d -name "*.egg-info" 2>/dev/null | wc -l)
tmpclaude=$(find . -name "tmpclaude-*" 2>/dev/null | wc -l)
total_temp=$((egg_info + tmpclaude))
if [ "$total_temp" -gt 0 ]; then
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
    find . -name "tmpclaude-*" -exec rm -rf {} + 2>/dev/null
    echo "      -> $total_temp elemento(s) eliminado(s)"
else
    echo "      -> No se encontraron archivos"
fi

# Node modules cache
echo "[7/7] Eliminando cache de npm/vite..."
count=$(find frontend -type d -name ".vite" 2>/dev/null | wc -l)
if [ "$count" -gt 0 ]; then
    find frontend -type d -name ".vite" -exec rm -rf {} + 2>/dev/null
    echo "      -> $count directorio(s) eliminado(s)"
else
    echo "      -> No se encontraron directorios"
fi

echo ""
echo "========================================"
echo " Limpieza completada exitosamente"
echo "========================================"
echo ""
