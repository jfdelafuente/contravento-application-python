# Script de limpieza de archivos temporales para ContraVento
# Uso: .\cleanup-temp.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Limpieza de Archivos Temporales" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Archivos de log
Write-Host "[1/7] Eliminando archivos de log..." -ForegroundColor Yellow
$logs = @(Get-ChildItem -Path . -Filter "*.log" -Recurse -File -ErrorAction SilentlyContinue)
if ($logs.Count -gt 0) {
    $logs | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "      -> $($logs.Count) archivo(s) encontrado(s)" -ForegroundColor Gray
} else {
    Write-Host "      -> No se encontraron archivos" -ForegroundColor Gray
}

# Cache de Python
Write-Host "[2/7] Eliminando cache de Python..." -ForegroundColor Yellow
$pycache = @(Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue)
$pyc = @(Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File -ErrorAction SilentlyContinue)
$pyo = @(Get-ChildItem -Path . -Filter "*.pyo" -Recurse -File -ErrorAction SilentlyContinue)
$totalPy = $pycache.Count + $pyc.Count + $pyo.Count
if ($totalPy -gt 0) {
    $pycache | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $pyc | Remove-Item -Force -ErrorAction SilentlyContinue
    $pyo | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "      -> $totalPy elemento(s) encontrado(s) (algunos pueden estar en uso)" -ForegroundColor Gray
} else {
    Write-Host "      -> No se encontraron archivos" -ForegroundColor Gray
}

# Cache de pytest
Write-Host "[3/7] Eliminando cache de pytest..." -ForegroundColor Yellow
$pytest = @(Get-ChildItem -Path . -Filter ".pytest_cache" -Recurse -Directory -ErrorAction SilentlyContinue)
if ($pytest.Count -gt 0) {
    $pytest | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      -> $($pytest.Count) directorio(s) encontrado(s)" -ForegroundColor Gray
} else {
    Write-Host "      -> No se encontraron directorios" -ForegroundColor Gray
}

# Cache de mypy
Write-Host "[4/7] Eliminando cache de mypy..." -ForegroundColor Yellow
$mypy = @(Get-ChildItem -Path . -Filter ".mypy_cache" -Recurse -Directory -ErrorAction SilentlyContinue)
if ($mypy.Count -gt 0) {
    $mypy | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      -> $($mypy.Count) directorio(s) encontrado(s)" -ForegroundColor Gray
} else {
    Write-Host "      -> No se encontraron directorios" -ForegroundColor Gray
}

# Archivos de coverage
Write-Host "[5/7] Eliminando archivos de coverage..." -ForegroundColor Yellow
$coverage = @(Get-ChildItem -Path . -Filter ".coverage" -Recurse -File -ErrorAction SilentlyContinue)
$coverageXml = @(Get-ChildItem -Path . -Filter "coverage.xml" -Recurse -File -ErrorAction SilentlyContinue)
$htmlcov = @(Get-ChildItem -Path . -Filter "htmlcov" -Recurse -Directory -ErrorAction SilentlyContinue)
$totalCov = $coverage.Count + $coverageXml.Count + $htmlcov.Count
if ($totalCov -gt 0) {
    $coverage | Remove-Item -Force -ErrorAction SilentlyContinue
    $coverageXml | Remove-Item -Force -ErrorAction SilentlyContinue
    $htmlcov | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      -> $totalCov elemento(s) encontrado(s)" -ForegroundColor Gray
} else {
    Write-Host "      -> No se encontraron archivos" -ForegroundColor Gray
}

# Egg info y archivos temporales de Claude
Write-Host "[6/7] Eliminando egg-info y temporales..." -ForegroundColor Yellow
$eggInfo = @(Get-ChildItem -Path . -Filter "*.egg-info" -Recurse -Directory -ErrorAction SilentlyContinue)
$tmpclaude = @(Get-ChildItem -Path . -Filter "tmpclaude-*" -Recurse -ErrorAction SilentlyContinue)
$totalTemp = $eggInfo.Count + $tmpclaude.Count
if ($totalTemp -gt 0) {
    $eggInfo | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $tmpclaude | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      -> $totalTemp elemento(s) encontrado(s)" -ForegroundColor Gray
} else {
    Write-Host "      -> No se encontraron archivos" -ForegroundColor Gray
}

# Node modules cache
Write-Host "[7/7] Eliminando cache de npm/vite..." -ForegroundColor Yellow
$vite = @(Get-ChildItem -Path frontend -Filter ".vite" -Recurse -Directory -ErrorAction SilentlyContinue)
if ($vite.Count -gt 0) {
    $vite | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "      -> $($vite.Count) directorio(s) encontrado(s)" -ForegroundColor Gray
} else {
    Write-Host "      -> No se encontraron directorios" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Limpieza completada exitosamente" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
