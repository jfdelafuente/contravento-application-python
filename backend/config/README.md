# Backend Configuration Files

Este directorio contiene archivos de configuración para el backend de ContraVento.

## Archivos

### `cycling_types.yaml`

Define los tipos de ciclismo iniciales que se cargarán en la base de datos.

**Uso**:
```bash
# Cargar tipos desde este archivo
poetry run python scripts/seed_cycling_types.py

# Actualizar tipos existentes desde este archivo
poetry run python scripts/seed_cycling_types.py --force
```

**Formato**:
```yaml
cycling_types:
  - code: bikepacking         # Identificador único (lowercase)
    display_name: Bikepacking # Nombre para mostrar
    description: "..."        # Descripción detallada
    is_active: true           # Si está activo
```

**Añadir nuevos tipos**:
1. Edita este archivo añadiendo el nuevo tipo
2. Ejecuta `poetry run python scripts/seed_cycling_types.py --force`
3. O usa la API: `POST /admin/cycling-types`

**Documentación completa**: Ver [docs/CYCLING_TYPES.md](../docs/CYCLING_TYPES.md)

## Notas

- Los archivos `.yaml` en este directorio NO deben ser commiteados con secretos
- Para configuración de entorno, usa archivos `.env` en el directorio raíz
- Para configuración específica de deployment, ver `docker-compose.*.yml`
