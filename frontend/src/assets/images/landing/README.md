# Landing Page Images

## Hero Image Requirements

**IMPORTANT**: Este directorio necesita las siguientes imágenes para el hero section de la landing page.

### Imágenes Requeridas

1. **hero.jpg** (Desktop version)
   - Dimensiones: 2560×1440px (16:9 ratio)
   - Formato: JPG
   - Tamaño objetivo: ~500KB (antes de optimización)
   - Contenido: Ciclista en entorno rural durante la hora dorada

2. **hero.webp** (Desktop WebP optimized)
   - Dimensiones: 2560×1440px
   - Formato: WebP
   - Tamaño objetivo: < 200KB
   - Generado desde hero.jpg

3. **hero-mobile.jpg** (Mobile version)
   - Dimensiones: 1024×768px
   - Formato: JPG
   - Tamaño objetivo: ~150KB
   - Contenido: Misma imagen recortada para mobile

4. **hero-mobile.webp** (Mobile WebP optimized)
   - Dimensiones: 1024×768px
   - Formato: WebP
   - Tamaño objetivo: < 60KB
   - Generado desde hero-mobile.jpg

### Opciones para Obtener Imágenes

#### Opción 1: Placeholder de Unsplash (Desarrollo)

Para desarrollo, puedes usar imágenes temporales de Unsplash:

```bash
# Buscar en: https://unsplash.com/s/photos/cyclist-sunset
# Palabras clave: "cyclist golden hour", "bikepacking landscape", "cycling rural"
```

Ejemplos de búsquedas sugeridas:
- https://unsplash.com/s/photos/cyclist-sunset
- https://unsplash.com/s/photos/bikepacking-landscape
- https://unsplash.com/s/photos/cycling-nature

#### Opción 2: Fotografía Personalizada (Producción)

Para producción, se recomienda:
- Fotografía original de ContraVento
- Licencia comercial apropiada
- Alta resolución para mantener calidad en pantallas 4K

### Optimización de Imágenes

Una vez tengas las imágenes JPG, optimízalas con:

```bash
# Instalar Squoosh CLI (recomendado por Google)
npm install -g @squoosh/cli

# Convertir JPG a WebP (desde el directorio de imágenes)
cd frontend/src/assets/images/landing

# Desktop version
squoosh-cli --webp auto hero.jpg

# Mobile version
squoosh-cli --webp auto hero-mobile.jpg
```

### Licencia

**IMPORTANTE**: Asegúrate de que todas las imágenes tienen la licencia adecuada para uso comercial.

- Unsplash: Licencia gratuita para uso comercial (CC0)
- Stock photos pagadas: Verifica términos de licencia
- Fotografía personalizada: Obtén derechos de autor por escrito

### Alt Text Recomendado

Para accesibilidad, usar:
```
"Ciclista en entorno rural durante la hora dorada"
```

---

**Status**: ✅ DESARROLLO - Imágenes placeholder de Unsplash disponibles
**Current Images**:
- hero.jpg (536KB, 2560×1440px) - Placeholder from Unsplash
- hero-mobile.jpg (149KB, 1024×768px) - Placeholder from Unsplash
- hero.webp / hero-mobile.webp - Currently JPG copies, need WebP optimization

**Production TODO**:
1. Replace with official ContraVento photography
2. Optimize WebP files (target: <200KB desktop, <60KB mobile)
3. Use Squoosh CLI or https://squoosh.app/ for optimization
