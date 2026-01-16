# Guía para Cambiar la Imagen del Hero Section

**Feature**: 014 - Landing Page Inspiradora
**Componente**: HeroSection
**Última actualización**: 2026-01-16

---

## Tabla de Contenidos

1. [Ubicación de Archivos](#ubicación-de-archivos)
2. [Especificaciones Técnicas](#especificaciones-técnicas)
3. [Método Rápido: Reemplazar Archivos](#método-rápido-reemplazar-archivos)
4. [Optimización de Imágenes](#optimización-de-imágenes)
5. [Método Avanzado: Cambiar Código](#método-avanzado-cambiar-código)
6. [Troubleshooting](#troubleshooting)

---

## Ubicación de Archivos

### Imágenes Actuales

```
frontend/src/assets/images/landing/
├── hero.webp              # Desktop WebP (optimizado)
├── hero.jpg               # Desktop JPG (fallback)
├── hero-mobile.webp       # Mobile WebP (optimizado)
├── hero-mobile.jpg        # Mobile JPG (fallback)
└── README.md              # Documentación de assets
```

### Componente

**Archivo**: `frontend/src/components/landing/HeroSection.tsx`
**Líneas**: 24-49 (elemento `<picture>`)

---

## Especificaciones Técnicas

### Dimensiones Recomendadas

| Versión | Resolución | Aspect Ratio | Peso Máximo |
|---------|-----------|--------------|-------------|
| **Desktop** | 1920×1080px | 16:9 | 500 KB |
| **Mobile** | 768×1024px | 3:4 | 200 KB |

### Formatos Soportados

| Formato | Uso | Ventajas | Compatibilidad |
|---------|-----|----------|----------------|
| **WebP** | Principal | -30% tamaño vs JPG, mejor calidad | Chrome, Firefox, Edge, Safari 14+ |
| **JPG** | Fallback | Compatibilidad universal | Todos los navegadores |

### Calidad de Compresión

- **WebP**: 80-85% (mejor balance calidad/tamaño)
- **JPG**: 85-90% (fallback, puede ser más pesado)

### Características de Imagen Ideal

✅ **Tema**: Ciclismo en entornos naturales/rurales
✅ **Iluminación**: Hora dorada (amanecer/atardecer) preferible
✅ **Composición**: Ciclista en acción, paisaje amplio
✅ **Colores**: Tonos cálidos, naturales (compatible con paleta terracota/verde bosque)
✅ **Enfoque**: Ciclista o paisaje nítido, fondo puede tener bokeh
✅ **Derechos**: Imagen libre de derechos o con licencia apropiada

---

## Método Rápido: Reemplazar Archivos

**Tiempo estimado**: 5-10 minutos
**Nivel**: Principiante
**Requiere**: Imágenes ya optimizadas

### Paso 1: Preparar tus Imágenes

1. **Descarga o selecciona** tu imagen base en alta resolución (mín. 1920×1080px)
2. **Crea dos versiones**:
   - Desktop: 1920×1080px
   - Mobile: 768×1024px (recorta o redimensiona enfocando el sujeto principal)

### Paso 2: Optimizar Imágenes

#### Opción A: Usar Herramientas Online (Sin instalación)

**TinyPNG** (https://tinypng.com/):
1. Sube tu imagen JPG
2. Descarga la versión comprimida
3. Resultado: ~60-70% reducción de tamaño

**Squoosh** (https://squoosh.app/):
1. Sube tu imagen
2. Selecciona formato WebP en panel derecho
3. Ajusta calidad a 80-85%
4. Descarga versión optimizada
5. Repite para JPG (calidad 85-90%)

#### Opción B: Usar Script Automático (Recomendado)

**Requisitos previos**:
- Node.js instalado
- Terminal/PowerShell

**Pasos**:

```bash
# 1. Navega al directorio frontend
cd "C:\My Program Files\workspace-claude\contravento-application-python\frontend"

# 2. Coloca tus imágenes JPG originales en:
# frontend/src/assets/images/landing/
# Nombres: hero-original.jpg, hero-mobile-original.jpg

# 3. Ejecuta el script de conversión
node convert-to-webp.js

# 4. El script creará automáticamente:
# - hero-original.webp (versión WebP optimizada)
# - hero-mobile-original.webp (versión WebP móvil)
```

### Paso 3: Renombrar y Reemplazar

1. **Renombra tus nuevas imágenes**:
   - `tu-imagen-desktop.jpg` → `hero.jpg`
   - `tu-imagen-desktop.webp` → `hero.webp`
   - `tu-imagen-mobile.jpg` → `hero-mobile.jpg`
   - `tu-imagen-mobile.webp` → `hero-mobile.webp`

2. **Reemplaza los archivos** en:
   ```
   frontend/src/assets/images/landing/
   ```

3. **Haz backup** (opcional pero recomendado):
   ```bash
   # Crea carpeta de backup
   mkdir frontend/src/assets/images/landing/backup

   # Copia imágenes actuales
   cp frontend/src/assets/images/landing/hero*.{jpg,webp} frontend/src/assets/images/landing/backup/
   ```

### Paso 4: Verificar Cambios

1. **Recarga el navegador** (Ctrl+F5 para forzar recarga)
2. **Verifica en mobile**: Abre DevTools → Toggle Device Toolbar (Ctrl+Shift+M)
3. **Verifica Network**: Asegúrate que se cargue WebP (mejor performance)

---

## Optimización de Imágenes

### Usando ImageMagick (CLI - Avanzado)

**Instalación**:
```bash
# Windows (usando Chocolatey)
choco install imagemagick

# macOS (usando Homebrew)
brew install imagemagick

# Linux (Ubuntu/Debian)
sudo apt-get install imagemagick
```

**Redimensionar Desktop**:
```bash
# Redimensionar a 1920×1080 manteniendo aspect ratio
magick convert original.jpg -resize 1920x1080^ -gravity center -extent 1920x1080 hero.jpg

# Optimizar calidad (85%)
magick convert hero.jpg -quality 85 hero-optimized.jpg
```

**Redimensionar Mobile**:
```bash
# Redimensionar a 768×1024 (portrait)
magick convert original.jpg -resize 768x1024^ -gravity center -extent 768x1024 hero-mobile.jpg

# Optimizar calidad (85%)
magick convert hero-mobile.jpg -quality 85 hero-mobile-optimized.jpg
```

**Convertir a WebP**:
```bash
# Desktop WebP (calidad 80)
magick convert hero.jpg -quality 80 hero.webp

# Mobile WebP (calidad 80)
magick convert hero-mobile.jpg -quality 80 hero-mobile.webp
```

### Usando cwebp (Oficial de Google - Mejor Calidad)

**Instalación**:
```bash
# Windows: Descarga de https://developers.google.com/speed/webp/download
# Extrae y agrega al PATH

# macOS
brew install webp

# Linux
sudo apt-get install webp
```

**Conversión**:
```bash
# Desktop WebP (calidad 82, preset photo)
cwebp -q 82 -preset photo hero.jpg -o hero.webp

# Mobile WebP (calidad 80, preset photo)
cwebp -q 80 -preset photo hero-mobile.jpg -o hero-mobile.webp
```

### Usando Sharp (Node.js - Script Personalizado)

**Crear script personalizado** (`optimize-hero.js`):

```javascript
// frontend/optimize-hero.js
const sharp = require('sharp');

async function optimizeHeroImages() {
  try {
    // Desktop JPG → WebP
    await sharp('src/assets/images/landing/hero.jpg')
      .resize(1920, 1080, { fit: 'cover', position: 'center' })
      .webp({ quality: 82 })
      .toFile('src/assets/images/landing/hero.webp');

    console.log('✅ Desktop WebP optimizado');

    // Desktop JPG optimizado
    await sharp('src/assets/images/landing/hero-original.jpg')
      .resize(1920, 1080, { fit: 'cover', position: 'center' })
      .jpeg({ quality: 88 })
      .toFile('src/assets/images/landing/hero.jpg');

    console.log('✅ Desktop JPG optimizado');

    // Mobile JPG → WebP
    await sharp('src/assets/images/landing/hero-mobile-original.jpg')
      .resize(768, 1024, { fit: 'cover', position: 'center' })
      .webp({ quality: 80 })
      .toFile('src/assets/images/landing/hero-mobile.webp');

    console.log('✅ Mobile WebP optimizado');

    // Mobile JPG optimizado
    await sharp('src/assets/images/landing/hero-mobile-original.jpg')
      .resize(768, 1024, { fit: 'cover', position: 'center' })
      .jpeg({ quality: 85 })
      .toFile('src/assets/images/landing/hero-mobile.jpg');

    console.log('✅ Mobile JPG optimizado');

    console.log('\n🎉 Todas las imágenes optimizadas exitosamente!');
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

optimizeHeroImages();
```

**Instalar dependencias**:
```bash
npm install sharp --save-dev
```

**Ejecutar script**:
```bash
node optimize-hero.js
```

---

## Método Avanzado: Cambiar Código

**Tiempo estimado**: 15-20 minutos
**Nivel**: Intermedio
**Requiere**: Conocimientos de React/TypeScript

### Paso 1: Ubicar el Componente

**Archivo**: `frontend/src/components/landing/HeroSection.tsx`

### Paso 2: Modificar Rutas de Imágenes

**Código actual** (líneas 24-49):

```typescript
<picture>
  {/* Mobile WebP (< 768px) */}
  <source
    media="(max-width: 768px)"
    srcSet="/src/assets/images/landing/hero-mobile.webp"
    type="image/webp"
  />
  {/* Mobile JPG Fallback (< 768px) */}
  <source
    media="(max-width: 768px)"
    srcSet="/src/assets/images/landing/hero-mobile.jpg"
    type="image/jpeg"
  />
  {/* Desktop WebP */}
  <source
    srcSet="/src/assets/images/landing/hero.webp"
    type="image/webp"
  />
  {/* Desktop JPG Fallback */}
  <img
    src="/src/assets/images/landing/hero.jpg"
    alt="Ciclista en entorno rural durante la hora dorada"
    className="hero-image"
    loading="eager"
  />
</picture>
```

### Paso 3: Cambiar a Tus Imágenes

**Opción A**: Usar nombres personalizados

```typescript
<picture>
  {/* Mobile WebP (< 768px) */}
  <source
    media="(max-width: 768px)"
    srcSet="/src/assets/images/landing/mi-hero-mobile.webp"
    type="image/webp"
  />
  {/* Mobile JPG Fallback (< 768px) */}
  <source
    media="(max-width: 768px)"
    srcSet="/src/assets/images/landing/mi-hero-mobile.jpg"
    type="image/jpeg"
  />
  {/* Desktop WebP */}
  <source
    srcSet="/src/assets/images/landing/mi-hero-desktop.webp"
    type="image/webp"
  />
  {/* Desktop JPG Fallback */}
  <img
    src="/src/assets/images/landing/mi-hero-desktop.jpg"
    alt="Tu descripción de la imagen aquí"
    className="hero-image"
    loading="eager"
  />
</picture>
```

**Opción B**: Usar URL externa (CDN)

```typescript
<picture>
  {/* Desktop WebP */}
  <source
    srcSet="https://cdn.contravento.com/images/hero-v2.webp"
    type="image/webp"
  />
  {/* Desktop JPG Fallback */}
  <img
    src="https://cdn.contravento.com/images/hero-v2.jpg"
    alt="Ciclista explorando nuevos territorios"
    className="hero-image"
    loading="eager"
  />
</picture>
```

### Paso 4: Actualizar Alt Text

**Importante para SEO y Accesibilidad**:

```typescript
alt="Ciclista en ruta de montaña durante la hora dorada - ContraVento"
```

**Buenas prácticas**:
- ✅ Describe la escena brevemente (10-15 palabras)
- ✅ Menciona elementos clave (ciclista, paisaje, momento del día)
- ✅ No uses "imagen de" o "foto de" (redundante)
- ✅ Incluye contexto relevante al sitio (ContraVento, naturaleza, etc.)

### Paso 5: Commit y Push

```bash
# Stage cambios
git add frontend/src/components/landing/HeroSection.tsx
git add frontend/src/assets/images/landing/

# Commit
git commit -m "feat(landing): update hero section image

- Replace hero image with new cycling scene
- Update alt text for better accessibility
- Optimize image sizes (Desktop: XXX KB, Mobile: YYY KB)

Co-Authored-By: Tu Nombre <tu@email.com>"

# Push
git push origin 014-landing-page-inspiradora
```

---

## Troubleshooting

### Problema 1: Imagen No Se Muestra

**Síntomas**: Área vacía o imagen rota

**Soluciones**:

1. **Verifica la ruta**:
   ```bash
   # Desde la raíz del proyecto
   ls -la frontend/src/assets/images/landing/
   ```

2. **Verifica permisos**:
   ```bash
   # Windows PowerShell
   Get-Acl frontend/src/assets/images/landing/hero.jpg

   # Linux/macOS
   ls -la frontend/src/assets/images/landing/hero.jpg
   ```

3. **Recarga forzada**:
   - Chrome/Edge: `Ctrl+Shift+R`
   - Firefox: `Ctrl+F5`
   - Safari: `Cmd+Shift+R`

4. **Limpia caché de Vite**:
   ```bash
   cd frontend
   rm -rf node_modules/.vite
   npm run dev
   ```

### Problema 2: Imagen Se Ve Borrosa

**Causas comunes**:
- Imagen fuente de baja resolución
- Compresión excesiva
- CSS scaling incorrecto

**Soluciones**:

1. **Verifica resolución original**:
   ```bash
   # Usando ImageMagick
   magick identify hero.jpg

   # Debería mostrar: hero.jpg JPEG 1920x1080
   ```

2. **Aumenta calidad de compresión**:
   ```bash
   # WebP con calidad 90
   cwebp -q 90 -preset photo hero.jpg -o hero.webp
   ```

3. **Verifica CSS**:
   ```css
   .hero-image {
     object-fit: cover; /* No debe ser 'fill' */
     image-rendering: auto; /* Nunca 'pixelated' */
   }
   ```

### Problema 3: Imagen Muy Pesada (Carga Lenta)

**Síntomas**: LCP > 2.5s, Lighthouse score bajo

**Soluciones**:

1. **Verifica tamaño de archivo**:
   ```bash
   ls -lh frontend/src/assets/images/landing/hero*

   # Desktop debería ser < 500 KB
   # Mobile debería ser < 200 KB
   ```

2. **Comprime más agresivamente**:
   ```bash
   # WebP con calidad 70-75 (más compresión)
   cwebp -q 75 -preset photo hero.jpg -o hero.webp
   ```

3. **Usa formato WebP siempre**:
   - WebP es ~30% más ligero que JPG
   - Navegadores modernos (95%+) lo soportan

4. **Verifica en Lighthouse**:
   ```
   Chrome DevTools → Lighthouse → Performance
   Target: LCP < 2.5s
   ```

### Problema 4: Imagen Recortada Incorrectamente en Mobile

**Causas**:
- Aspect ratio incorrecto
- Focal point descentrado

**Soluciones**:

1. **Ajusta focal point en ImageMagick**:
   ```bash
   # Centra en la parte superior (para ciclista en horizonte)
   magick convert original.jpg -resize 768x1024^ -gravity north -extent 768x1024 hero-mobile.jpg

   # Opciones de gravity:
   # - center: Centro
   # - north: Arriba
   # - south: Abajo
   # - east: Derecha
   # - west: Izquierda
   ```

2. **Crea versión mobile manualmente**:
   - Abre en editor de imágenes (GIMP, Photoshop)
   - Recorta 768×1024 enfocando el sujeto principal
   - Exporta con calidad 85%

3. **Ajusta CSS object-position**:
   ```css
   @media (max-width: 768px) {
     .hero-image {
       object-position: center top; /* Centra arriba */
     }
   }
   ```

### Problema 5: WebP No Se Carga, Solo JPG

**Síntomas**: Network tab muestra solo JPG

**Causas**:
- Navegador antiguo
- Extensión bloqueando WebP
- Servidor no sirve WebP correctamente

**Soluciones**:

1. **Verifica soporte de navegador**:
   ```javascript
   // Abre Console en DevTools
   const canvas = document.createElement('canvas');
   const webpSupport = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
   console.log('WebP Support:', webpSupport);
   ```

2. **Verifica MIME type en servidor**:
   ```bash
   # Debería retornar: image/webp
   curl -I http://localhost:5173/src/assets/images/landing/hero.webp
   ```

3. **Fallback a JPG está funcionando** (esto es normal):
   - Si el navegador no soporta WebP, usará JPG automáticamente
   - No es un error, es el comportamiento esperado

---

## Checklist de Cambio de Imagen

Usa este checklist para asegurar que todo está correcto:

### Pre-Cambio
- [ ] Imagen original en alta resolución (mín. 1920×1080px)
- [ ] Imagen tiene tema relevante (ciclismo, naturaleza, territorio)
- [ ] Derechos de uso verificados (libre de derechos o licencia apropiada)
- [ ] Backup de imágenes actuales creado

### Optimización
- [ ] Versión desktop creada (1920×1080px)
- [ ] Versión mobile creada (768×1024px)
- [ ] Desktop WebP generado (< 500 KB)
- [ ] Desktop JPG generado (< 600 KB)
- [ ] Mobile WebP generado (< 200 KB)
- [ ] Mobile JPG generado (< 250 KB)
- [ ] Calidad visual verificada (no borrosa, no pixelada)

### Implementación
- [ ] Archivos copiados a `frontend/src/assets/images/landing/`
- [ ] Nombres correctos (hero.webp, hero.jpg, hero-mobile.webp, hero-mobile.jpg)
- [ ] Alt text actualizado (descriptivo, relevante, conciso)
- [ ] Código compilado sin errores (`npm run build`)

### Verificación
- [ ] Imagen se muestra correctamente en desktop
- [ ] Imagen se muestra correctamente en mobile (DevTools)
- [ ] WebP se carga en navegadores compatibles (Chrome DevTools → Network)
- [ ] JPG fallback funciona en navegadores antiguos
- [ ] LCP < 2.5s (Lighthouse Performance)
- [ ] No hay errores en Console

### Post-Cambio
- [ ] Commit con mensaje descriptivo
- [ ] Push a branch `014-landing-page-inspiradora`
- [ ] Documentación actualizada (este archivo si es necesario)
- [ ] Tests pasando (`npm test`)

---

## Recursos Adicionales

### Herramientas Online

- **TinyPNG**: https://tinypng.com/ (Compresión JPG/PNG)
- **Squoosh**: https://squoosh.app/ (Conversión y compresión WebP)
- **Remove.bg**: https://remove.bg/ (Remover fondo si necesario)
- **Unsplash**: https://unsplash.com/s/photos/cycling (Imágenes gratuitas de ciclismo)
- **Pexels**: https://pexels.com/search/bicycle/ (Imágenes gratuitas de bicicletas)

### Herramientas CLI

- **ImageMagick**: https://imagemagick.org/
- **cwebp (Google)**: https://developers.google.com/speed/webp/docs/cwebp
- **Sharp (Node.js)**: https://sharp.pixelplumbing.com/

### Bancos de Imágenes (Gratis)

- **Unsplash**: https://unsplash.com/ (Licencia libre)
- **Pexels**: https://pexels.com/ (Licencia libre)
- **Pixabay**: https://pixabay.com/ (Licencia libre)
- **Burst by Shopify**: https://burst.shopify.com/ (Licencia comercial gratuita)

### Guías de Optimización

- **Google Web.dev**: https://web.dev/optimize-images/
- **MDN Web Docs**: https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images
- **Lighthouse**: https://developers.google.com/web/tools/lighthouse

---

## Contacto y Soporte

Si tienes problemas o preguntas:

1. **Revisa este documento** primero
2. **Consulta el README** en `frontend/src/assets/images/landing/README.md`
3. **Revisa los logs** de Vite en la terminal
4. **Abre DevTools Console** para ver errores JavaScript
5. **Crea un issue** en GitHub con tag `[Feature 014] Hero Image`

---

**Última actualización**: 2026-01-16
**Mantenedor**: Equipo Frontend ContraVento
**Versión**: 1.0.0
