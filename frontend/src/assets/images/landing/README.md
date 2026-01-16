# Landing Page Images - Quick Reference

**📖 Guía Completa**: Ver [`specs/014-landing-page-inspiradora/HERO_IMAGE_GUIDE.md`](../../../../specs/014-landing-page-inspiradora/HERO_IMAGE_GUIDE.md)

---

## 🚀 Cambio Rápido de Imagen (5 minutos)

### 1. Prepara tus imágenes
- Desktop: 1920×1080px (16:9)
- Mobile: 768×1024px (3:4)

### 2. Optimiza con herramientas online
- **TinyPNG**: https://tinypng.com/ (JPG)
- **Squoosh**: https://squoosh.app/ (WebP, calidad 80-85%)

### 3. Renombra y reemplaza
```
tu-imagen-desktop.jpg   → hero.jpg
tu-imagen-desktop.webp  → hero.webp
tu-imagen-mobile.jpg    → hero-mobile.jpg
tu-imagen-mobile.webp   → hero-mobile.webp
```

### 4. Coloca en esta carpeta
```
frontend/src/assets/images/landing/
```

### 5. Recarga navegador
- Chrome/Edge: `Ctrl+Shift+R`
- Firefox: `Ctrl+F5`

---

## 📋 Especificaciones Técnicas

### Imágenes Requeridas

| Archivo | Dimensiones | Formato | Peso Máx | Uso |
|---------|------------|---------|----------|-----|
| `hero.jpg` | 1920×1080px | JPG | 500 KB | Desktop fallback |
| `hero.webp` | 1920×1080px | WebP | 500 KB | Desktop optimizado |
| `hero-mobile.jpg` | 768×1024px | JPG | 200 KB | Mobile fallback |
| `hero-mobile.webp` | 768×1024px | WebP | 200 KB | Mobile optimizado |

### Calidad de Compresión

- **WebP**: 80-85% (mejor balance)
- **JPG**: 85-90% (fallback)

---

## 🛠️ Optimización Automática (Recomendado)

### Usando Script Incluido

```bash
# 1. Navega a frontend
cd frontend

# 2. Coloca tus JPG originales aquí:
# frontend/src/assets/images/landing/hero-original.jpg
# frontend/src/assets/images/landing/hero-mobile-original.jpg

# 3. Ejecuta script
node convert-to-webp.js

# 4. Se crean automáticamente los archivos WebP optimizados
```

### Usando cwebp (Google - Mejor Calidad)

```bash
# Desktop WebP
cwebp -q 82 -preset photo hero.jpg -o hero.webp

# Mobile WebP
cwebp -q 80 -preset photo hero-mobile.jpg -o hero-mobile.webp
```

---

## 🎨 Características de Imagen Ideal

✅ **Tema**: Ciclismo en entornos naturales/rurales
✅ **Iluminación**: Hora dorada (amanecer/atardecer)
✅ **Composición**: Ciclista en acción, paisaje amplio
✅ **Colores**: Tonos cálidos (compatible con paleta terracota/verde bosque)
✅ **Enfoque**: Sujeto nítido, fondo puede tener bokeh
✅ **Derechos**: Libre de derechos o licencia comercial

---

## 🔍 Bancos de Imágenes Gratuitas

- **Unsplash**: https://unsplash.com/s/photos/cycling
- **Pexels**: https://pexels.com/search/bicycle/
- **Pixabay**: https://pixabay.com/images/search/cycling/

**Búsquedas sugeridas**:
- "cyclist golden hour"
- "bikepacking landscape"
- "cycling rural sunset"
- "bicycle mountain road"

---

## 🐛 Troubleshooting Rápido

### Imagen no se muestra
```bash
# Verifica que existen
ls -la frontend/src/assets/images/landing/hero*

# Recarga forzada: Ctrl+Shift+R
```

### Imagen borrosa
```bash
# Aumenta calidad WebP
cwebp -q 90 -preset photo hero.jpg -o hero.webp
```

### Imagen muy pesada
```bash
# Comprime más
cwebp -q 75 -preset photo hero.jpg -o hero.webp

# Verifica tamaño
ls -lh hero.webp  # Debe ser < 500 KB
```

---

## 📍 Ubicación del Código

**Componente**: `frontend/src/components/landing/HeroSection.tsx`
**Líneas**: 24-49 (elemento `<picture>`)

**Para cambiar rutas de imágenes**, edita:
```typescript
<source srcSet="/src/assets/images/landing/TU-IMAGEN.webp" />
```

---

## ✅ Checklist de Verificación

- [ ] Imagen desktop (1920×1080px) < 500 KB
- [ ] Imagen mobile (768×1024px) < 200 KB
- [ ] Versiones WebP generadas
- [ ] Archivos en `frontend/src/assets/images/landing/`
- [ ] Alt text actualizado (si cambió el contenido)
- [ ] Navegador recargado (Ctrl+Shift+R)
- [ ] Verificado en mobile (DevTools → Toggle Device)
- [ ] WebP se carga correctamente (Network tab)

---

## 📚 Recursos

- **Guía Completa**: `specs/014-landing-page-inspiradora/HERO_IMAGE_GUIDE.md`
- **Optimización**: https://web.dev/optimize-images/
- **WebP Converter**: https://squoosh.app/
- **Lighthouse**: Chrome DevTools → Lighthouse tab

---

## 📊 Estado Actual

**Imágenes Actuales**:
- ✅ `hero.jpg` (536 KB, 1920×1080px)
- ✅ `hero.webp` (Optimizado)
- ✅ `hero-mobile.jpg` (149 KB, 768×1024px)
- ✅ `hero-mobile.webp` (Optimizado)

**Licencia**: Unsplash (CC0 - Uso comercial permitido)
**Alt Text**: "Ciclista en entorno rural durante la hora dorada"

---

**Última actualización**: 2026-01-16
**Feature**: 014 - Landing Page Inspiradora
