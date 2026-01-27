# Análisis de Impacto - Reorganización de Scripts

**Fecha**: 2026-01-27
**Cambio**: Reorganización de scripts backend en carpetas temáticas

## 📊 Resumen Ejecutivo

**Scripts migrados**: 31 scripts reorganizados en 7 categorías
**Archivos afectados**: 15 archivos de documentación requieren actualización
**Impacto**: MEDIO - Rutas de scripts cambiaron, documentación desactualizada

---

## 🎯 Cambios en Rutas de Scripts

### Mapeo de Rutas Antiguas → Nuevas

| Script Antiguo | Nueva Ubicación | Categoría |
|----------------|-----------------|-----------|
| `scripts/create_admin.py` | `scripts/user-mgmt/create_admin.py` | user-mgmt |
| `scripts/create_verified_user.py` | `scripts/user-mgmt/create_verified_user.py` | user-mgmt |
| `scripts/promote_to_admin.py` | `scripts/user-mgmt/promote_to_admin.py` | user-mgmt |
| `scripts/manage_follows.py` | `scripts/user-mgmt/manage_follows.py` | user-mgmt |
| `scripts/init_dev_data.py` | `scripts/seeding/init_dev_data.py` | seeding |
| `scripts/seed_achievements.py` | `scripts/seeding/seed_achievements.py` | seeding |
| `scripts/seed_cycling_types.py` | `scripts/seeding/seed_cycling_types.py` | seeding |
| `scripts/seed_trips.py` | `scripts/seeding/seed_trips.py` | seeding |
| `scripts/add_test_trip_with_coordinates.py` | `scripts/seeding/add_test_trip_with_coordinates.py` | seeding |
| `scripts/test_route_statistics.py` | `scripts/testing/test_route_statistics.py` | testing |
| `scripts/test_gpx_statistics.sh` | `scripts/testing/test_gpx_statistics.sh` | testing |
| `scripts/test_gpx_statistics.ps1` | `scripts/testing/test_gpx_statistics.ps1` | testing |
| `scripts/test_tags.sh` | `scripts/testing/test_tags.sh` | testing |
| `scripts/check_latest_gpx.py` | `scripts/dev-tools/check_latest_gpx.py` | dev-tools |
| `scripts/check_test_data.py` | `scripts/dev-tools/check_test_data.py` | dev-tools |
| `scripts/check_stats.py` | `scripts/dev-tools/check_stats.py` | dev-tools |
| `scripts/clean_trips.py` | `scripts/dev-tools/clean_trips.py` | dev-tools |
| `scripts/docker-entrypoint.sh` | `scripts/deployment/docker-entrypoint.sh` | deployment |
| `scripts/mvp-check.sh` | `scripts/deployment/mvp-check.sh` | deployment |

---

## 🔴 Archivos CRÍTICOS que Requieren Actualización

### Directorio Raíz

#### 1. **CLAUDE.md** - ALTA PRIORIDAD
**Ubicación**: `./CLAUDE.md`
**Referencias encontradas**: 11 líneas

**Líneas a actualizar**:
- Línea 279: `poetry run python scripts/create_admin.py` → `scripts/user-mgmt/create_admin.py`
- Línea 283: `poetry run python scripts/create_admin.py --username...` → `scripts/user-mgmt/create_admin.py`
- Línea 286: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`
- Línea 289: `poetry run python scripts/create_verified_user.py --username...` → `scripts/user-mgmt/create_verified_user.py`
- Línea 292: `poetry run python scripts/create_verified_user.py --username...` → `scripts/user-mgmt/create_verified_user.py`
- Línea 295: `poetry run python scripts/create_verified_user.py --verify-email...` → `scripts/user-mgmt/create_verified_user.py`
- Línea 298: `poetry run python scripts/promote_to_admin.py --username...` → `scripts/user-mgmt/promote_to_admin.py`
- Línea 301: `poetry run python scripts/promote_to_admin.py --username...` → `scripts/user-mgmt/promote_to_admin.py`
- Línea 699: `poetry run python scripts/seed_cycling_types.py` → `scripts/seeding/seed_cycling_types.py`
- Línea 702: `poetry run python scripts/seed_cycling_types.py --list` → `scripts/seeding/seed_cycling_types.py`
- Línea 739: `poetry run python scripts/seed_cycling_types.py --force` → `scripts/seeding/seed_cycling_types.py`

**Impacto**: CRÍTICO - Este es el archivo de referencia principal para developers

---

#### 2. **QUICK_START.md** - ALTA PRIORIDAD
**Ubicación**: `./QUICK_START.md`
**Referencias encontradas**: 3 líneas

**Líneas a actualizar**:
- Línea 928: `poetry run python scripts/create_admin.py` → `scripts/user-mgmt/create_admin.py`
- Línea 929: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`
- Línea 930: `poetry run python scripts/promote_to_admin.py --username X` → `scripts/user-mgmt/promote_to_admin.py`

**Impacto**: CRÍTICO - Documento de onboarding para nuevos usuarios

---

### Backend

#### 3. **backend/README.md** - PRIORIDAD MEDIA
**Ubicación**: `./backend/README.md`
**Referencias encontradas**: 4 líneas

**Líneas a actualizar**:
- Línea 97: `poetry run python scripts/seed_achievements.py` → `scripts/seeding/seed_achievements.py`
- Línea 120: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`
- Línea 123: `poetry run python scripts/create_verified_user.py --username...` → `scripts/user-mgmt/create_verified_user.py`
- Línea 126: `poetry run python scripts/create_verified_user.py --verify-email...` → `scripts/user-mgmt/create_verified_user.py`

**Impacto**: MEDIO - Documentación específica del backend

---

#### 4. **backend/config/README.md** - PRIORIDAD MEDIA
**Ubicación**: `./backend/config/README.md`
**Referencias encontradas**: 3 líneas

**Líneas a actualizar**:
- Línea 14: `poetry run python scripts/seed_cycling_types.py` → `scripts/seeding/seed_cycling_types.py`
- Línea 17: `poetry run python scripts/seed_cycling_types.py --force` → `scripts/seeding/seed_cycling_types.py`
- Línea 31: `poetry run python scripts/seed_cycling_types.py --force` → `scripts/seeding/seed_cycling_types.py`

**Impacto**: BAJO - Documentación de configuración

---

### Scripts

#### 5. **scripts/testing/README.md** - PRIORIDAD BAJA
**Ubicación**: `./scripts/testing/README.md`
**Referencias encontradas**: 1 línea

**Líneas a actualizar**:
- Línea 64: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`

**Impacto**: BAJO - Documentación interna de scripts

---

#### 6. **scripts/testing/gps/README.md** - PRIORIDAD BAJA
**Ubicación**: `./scripts/testing/gps/README.md`
**Referencias encontradas**: 2 líneas

**Líneas a actualizar**:
- Línea 198: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`
- Línea 245: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`

**Impacto**: BAJO - Documentación de testing GPS

---

#### 7. **scripts/seed/README.md** - PRIORIDAD BAJA
**Ubicación**: `./scripts/seed/README.md`
**Referencias encontradas**: 3 líneas

**Líneas a actualizar**:
- Línea 48: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`
- Línea 182: `[backend/scripts/create_admin.py](../../backend/scripts/create_admin.py)` → `[backend/scripts/user-mgmt/create_admin.py](...)`
- Línea 183: `[backend/scripts/create_verified_user.py](../../backend/scripts/create_verified_user.py)` → `[backend/scripts/user-mgmt/create_verified_user.py](...)`

**Impacto**: BAJO - Documentación legacy de seeding

---

#### 8. **scripts/README.md** - PRIORIDAD BAJA
**Ubicación**: `./scripts/README.md`
**Referencias encontradas**: 1 línea

**Líneas a actualizar**:
- Línea 244: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`

**Impacto**: BAJO - Documentación raíz de scripts

---

### Backend Docs

#### 9. **backend/docs/api/README.md** - PRIORIDAD BAJA
**Ubicación**: `./backend/docs/api/README.md`
**Referencias encontradas**: 1 línea

**Líneas a actualizar**:
- Línea 124: `poetry run python scripts/create_verified_user.py` → `scripts/user-mgmt/create_verified_user.py`

**Impacto**: BAJO - Documentación de API

---

## ✅ Archivos YA ACTUALIZADOS (No requieren cambios)

- ✅ `backend/Dockerfile` - Actualizado con nuevas rutas
- ✅ `backend/scripts/deployment/docker-entrypoint.sh` - Actualizado
- ✅ `backend/scripts/seeding/init_dev_data.py` - Actualizado con nuevos imports
- ✅ `backend/scripts/README.md` - Completamente reescrito

---

## 🎯 Plan de Acción Recomendado

### Prioridad 1: CRÍTICO (Actualizar AHORA)
1. ✅ `CLAUDE.md` - 11 referencias
2. ✅ `QUICK_START.md` - 3 referencias

### Prioridad 2: MEDIO (Actualizar pronto)
3. ⏳ `backend/README.md` - 4 referencias
4. ⏳ `backend/config/README.md` - 3 referencias

### Prioridad 3: BAJA (Actualizar cuando sea posible)
5. ⏳ `scripts/testing/README.md` - 1 referencia
6. ⏳ `scripts/testing/gps/README.md` - 2 referencias
7. ⏳ `scripts/seed/README.md` - 3 referencias
8. ⏳ `scripts/README.md` - 1 referencia
9. ⏳ `backend/docs/api/README.md` - 1 referencia

---

## 🔍 Archivos en specs/ (Documentación de User Stories)

**No requieren actualización inmediata** pero deben revisarse:
- `specs/001-user-profiles/quickstart.md`
- `specs/002-travel-diary/quickstart.md`
- `specs/003-gps-routes/MANUAL_TESTING.md`
- `specs/004-social-network/TESTING_MANUAL_US1_US2.md`
- Y otros archivos de testing manual

Estos archivos contienen referencias antiguas pero son documentos de testing históricos que pueden actualizarse de forma incremental.

---

## 🛠️ Comando de Búsqueda para Verificar

Para encontrar todas las referencias pendientes:

```bash
# Buscar referencias a rutas antiguas
grep -r "scripts/create_admin.py" --include="*.md" .
grep -r "scripts/create_verified_user.py" --include="*.md" .
grep -r "scripts/seed_" --include="*.md" .
grep -r "scripts/promote_to_admin.py" --include="*.md" .
grep -r "scripts/manage_follows.py" --include="*.md" .
grep -r "scripts/init_dev_data.py" --include="*.md" .
```

---

## 📝 Notas Importantes

1. **Backwards Compatibility**: Los scripts físicos se movieron con `mv`, NO con `git mv`, por lo que Git los detectó como delete + create en lugar de rename. Esto NO afecta la funcionalidad.

2. **Import Paths**: Solo `init_dev_data.py` requirió actualización de imports internos (ya completado).

3. **Docker References**: Dockerfile y docker-entrypoint.sh ya están actualizados.

4. **Testing**: Se recomienda ejecutar `poetry run python scripts/seeding/init_dev_data.py` para verificar que todos los imports funcionan correctamente.

---

## ✅ Validación Post-Migración

```bash
# Verificar que init_dev_data funciona
poetry run python scripts/seeding/init_dev_data.py

# Verificar que create_admin funciona
poetry run python scripts/user-mgmt/create_admin.py --help

# Verificar que seed_cycling_types funciona
poetry run python scripts/seeding/seed_cycling_types.py --list
```

---

**Estado**: MIGRACIÓN COMPLETADA - Documentación requiere actualización
**Próximo paso**: Actualizar archivos de Prioridad 1 (CLAUDE.md, QUICK_START.md)
