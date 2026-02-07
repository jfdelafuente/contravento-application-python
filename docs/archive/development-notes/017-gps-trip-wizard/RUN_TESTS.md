# Guía para Ejecutar Pruebas del Wizard GPX

## Correcciones Realizadas

### 1. Problema de Referencia a `mockTelemetryData`
**Arreglado**: El mock de `Step1Upload` usaba `mockTelemetryData` antes de que fuera definido.
**Solución**: Inline los datos de telemetría directamente en el mock.

### 2. Actualización de Estructura de 5 Pasos
**Arreglado**: Todas las pruebas actualizadas para reflejar los 5 pasos del wizard:
- Step 0: Upload GPX
- Step 1: Trip Details
- Step 2: Map Visualization
- Step 3: POI Management
- Step 4: Review & Publish

### 3. Mocks de Componentes de Paso
**Añadido**: Mocks para todos los componentes de paso con botones simplificados.

## Comandos para Ejecutar Pruebas

### Opción 1: Todas las Pruebas del Wizard
```bash
cd frontend
npm test -- tests/unit/Step*.test.tsx tests/unit/GPXWizard.test.tsx --run
```

### Opción 2: Solo GPXWizard
```bash
cd frontend
npm test -- tests/unit/GPXWizard.test.tsx --run --reporter=verbose
```

### Opción 3: Solo Step3POIs
```bash
cd frontend
npm test -- tests/unit/Step3POIs.test.tsx --run --reporter=verbose
```

### Opción 4: Solo Step4Review
```bash
cd frontend
npm test -- tests/unit/Step4Review.test.tsx --run --reporter=verbose
```

### Opción 5: Con Cobertura
```bash
cd frontend
npm run test:coverage -- tests/unit/GPXWizard.test.tsx tests/unit/Step3POIs.test.tsx tests/unit/Step4Review.test.tsx
```

## Verificación Manual de TypeScript

Antes de ejecutar las pruebas, verifica que no haya errores de TypeScript:

```bash
cd frontend
npx tsc --noEmit
```

## Archivos Modificados

1. `tests/unit/GPXWizard.test.tsx` - Refactorizado con mocks de componentes
2. `tests/unit/Step3POIs.test.tsx` - Selectores ARIA actualizados
3. `tests/unit/Step4Review.test.tsx` - Renombrado desde Step3Review, prop `pois` añadido

## Resultado Esperado

Todas las pruebas deberían pasar:
- ✅ GPXWizard: ~19 pruebas
- ✅ Step3POIs: ~11 pruebas
- ✅ Step4Review: ~20+ pruebas

Total esperado: ~50+ pruebas pasando
