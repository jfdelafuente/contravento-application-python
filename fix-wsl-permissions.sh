#!/bin/bash
# ============================================================================
# Fix WSL Permissions and Poetry Issues
# ============================================================================
# Soluciona problemas comunes de permisos en WSL con Node.js y Poetry
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

print_header "WSL Permissions Fix"

# Step 1: Fix Poetry virtualenv configuration
print_info "Step 1: Limpiando configuración de Poetry..."

cd backend

# Remove existing virtualenv if corrupted
if [ -d ".venv" ]; then
    print_warning "Eliminando virtualenv existente (puede estar corrupto)..."
    rm -rf .venv
    print_success ".venv eliminado"
fi

# Configure Poetry to create virtualenvs in project directory
print_info "Configurando Poetry para usar virtualenvs locales..."
poetry config virtualenvs.in-project true --local
poetry config virtualenvs.prefer-active-python true --local

# Remove any cached Poetry data
if [ -d "$HOME/.cache/pypoetry" ]; then
    print_info "Limpiando caché de Poetry..."
    rm -rf "$HOME/.cache/pypoetry/virtualenvs"
    print_success "Caché limpiado"
fi

# Reinstall dependencies
print_info "Reinstalando dependencias de Python..."
poetry install
print_success "Dependencias instaladas en .venv local"

cd ..

# Step 2: Fix Node.js permissions
print_info "Step 2: Arreglando permisos de Node.js..."

cd frontend

# Remove node_modules if exists
if [ -d "node_modules" ]; then
    print_warning "Eliminando node_modules existente..."
    rm -rf node_modules
    print_success "node_modules eliminado"
fi

# Remove package-lock.json to avoid conflicts
if [ -f "package-lock.json" ]; then
    print_info "Eliminando package-lock.json..."
    rm -f package-lock.json
    print_success "package-lock.json eliminado"
fi

# Reinstall npm packages
print_info "Reinstalando dependencias de Node.js..."
# Clean install to avoid corrupted modules
npm ci 2>/dev/null || npm install

# Fix permissions on node_modules/.bin (critical for WSL)
if [ -d "node_modules/.bin" ]; then
    print_info "Aplicando permisos de ejecución a binarios de Node.js..."
    chmod -R +x node_modules/.bin
    print_success "Permisos aplicados a node_modules/.bin"
fi

# Verify vite installation
if [ -f "node_modules/.bin/vite" ]; then
    print_success "Vite instalado correctamente"
else
    print_error "Vite no se instaló correctamente"
fi

cd ..

# Step 3: Verify fixes
print_header "Verificación"

print_info "Python virtualenv:"
if [ -d "backend/.venv" ]; then
    print_success "backend/.venv creado correctamente"
    print_info "  Ubicación: $(cd backend && poetry env info --path)"
else
    print_error "backend/.venv no se pudo crear"
fi

print_info "Node.js binarios:"
if [ -x "frontend/node_modules/.bin/vite" ]; then
    print_success "frontend/node_modules/.bin/vite tiene permisos de ejecución"
else
    print_error "frontend/node_modules/.bin/vite NO tiene permisos de ejecución"
fi

echo ""

# Step 4: Instructions
print_header "Próximos pasos"

print_success "Reparación completada!"
echo ""
print_info "Ahora puedes ejecutar:"
print_info "  ./run-local-dev.sh --with-frontend"
echo ""
print_warning "Si sigues teniendo problemas, intenta:"
print_info "  1. Reiniciar la terminal WSL"
print_info "  2. Verificar que no haya variables de entorno de Windows contaminando WSL"
print_info "  3. Ejecutar: export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
echo ""
