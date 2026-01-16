# Feature Specification: Landing Page Inspiradora

**Feature Branch**: `014-landing-page-inspiradora`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Landing Page Inspiradora - Crear landing page pública centrada en conexión humana y territorial para ciclistas, con hero cinematográfico, manifiesto de 4 pilares, grid de valores (territorio/comunidad/ética), sección cómo funciona, y CTA de registro. Diseño rústico minimalista con paleta terracota (#D35400), verde bosque (#1B2621), crema (#F9F7F2), siguiendo filosofía el camino es el destino."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visitante Descubre la Filosofía ContraVento (Priority: P1)

Un ciclista o persona interesada en cicloturismo llega a la landing page (desde redes sociales, búsqueda orgánica, o recomendación) y descubre la propuesta de valor diferencial de ContraVento: una plataforma que prioriza la conexión humana y territorial por encima del rendimiento deportivo.

**Why this priority**: Esta es la primera impresión crítica. Si no logramos capturar la atención y transmitir nuestra filosofía única en los primeros 5 segundos, perdemos al visitante. Es el MVP absoluto de la landing page.

**Independent Test**: Un visitante puede llegar a la página raíz (/), ver el hero cinematográfico con el mensaje "El camino es el destino", leer el manifiesto de 4 pilares, y comprender la propuesta de valor sin necesidad de registrarse o navegar a otras secciones.

**Acceptance Scenarios**:

1. **Given** un visitante llega a la URL raíz del sitio, **When** la página carga completamente, **Then** ve inmediatamente:
   - Imagen hero de alta calidad (ciclista en entorno rural, hora dorada)
   - Titular principal "El camino es el destino" con tipografía distintiva
   - Subtítulo explicativo sobre conectar vs competir
   - Botón CTA "Formar parte del viaje" visible sin scroll

2. **Given** un visitante scrollea hacia abajo desde el hero, **When** llega a la sección de manifiesto, **Then** ve los 4 pilares filosóficos claramente presentados:
   - "El camino es el destino" - No conquistar, sino habitar
   - "Motor de regeneración" - Activar economía de pueblos pequeños
   - "Solidaridad en ruta" - Comunidad que se cuida mutuamente
   - "No dejar rastro" - Respeto al entorno y cortesía rural

3. **Given** un visitante está en cualquier dispositivo (móvil, tablet, desktop), **When** visualiza la landing page, **Then** el diseño se adapta correctamente manteniendo:
   - Legibilidad del texto (tipografía escalable)
   - Proporción de imágenes hero
   - Jerarquía visual clara

---

### User Story 2 - Visitante Comprende los Valores Diferenciadores (Priority: P2)

El visitante, ya captado por la filosofía, quiere entender cómo ContraVento traduce estos valores en acciones concretas: impacto territorial, construcción de comunidad, y ética de preservación.

**Why this priority**: Una vez captada la atención con la filosofía (P1), necesitamos concretar cómo se materializa en la plataforma. Sin esto, el mensaje quedaría abstracto y poco convincente.

**Independent Test**: Un visitante puede scrollear a la sección "Pilares de Valor" y comprender las tres dimensiones prácticas (Territorio, Comunidad, Ética) sin necesidad de registrarse, con iconografía clara y copy conciso.

**Acceptance Scenarios**:

1. **Given** un visitante ha leído el manifiesto, **When** scrollea a la sección "Pilares de Valor", **Then** ve un grid visual de 3 columnas con:
   - **Columna 1 (Territorio)**: Icono de tienda local + "Consumo local, impacto real"
   - **Columna 2 (Comunidad)**: Icono de brújula/manos + "Reporte de alertas y consejos compartidos"
   - **Columna 3 (Ética)**: Icono de hoja/huella + "Cortesía rural y ética de preservación"

2. **Given** un visitante está en un dispositivo móvil, **When** visualiza los pilares de valor, **Then** el grid se reorganiza verticalmente (stack) manteniendo orden y legibilidad

3. **Given** un visitante interactúa con un pilar, **When** hace hover (desktop) o tap (móvil), **Then** el pilar se resalta sutilmente (cambio de color de fondo o sombra) sin expandir contenido adicional

---

### User Story 3 - Visitante Entiende Cómo Funciona la Plataforma (Priority: P2)

El visitante, convencido de la filosofía y valores, quiere saber cómo usar ContraVento en la práctica: qué acciones puede realizar, cómo contribuye al impacto territorial, y cómo se beneficia de la comunidad.

**Why this priority**: Después de inspirar (P1) y concretar valores (P2), necesitamos mostrar el "cómo" práctico. Esto reduce fricción en la conversión a registro al responder "¿qué puedo hacer aquí?".

**Independent Test**: Un visitante puede scrollear a la sección "Cómo Funciona" y ver un flujo visual de 4 pasos que explica el ciclo completo: documentar viaje → compartir con comunidad → descubrir rutas → impactar territorios.

**Acceptance Scenarios**:

1. **Given** un visitante ha comprendido los valores, **When** scrollea a "Cómo Funciona", **Then** ve un flujo visual de 4 pasos numerados:
   - **Paso 1**: "Documenta tu viaje" - Crea diarios de ruta con fotos y ubicaciones
   - **Paso 2**: "Comparte con la comunidad" - Publica para inspirar a otros ciclistas
   - **Paso 3**: "Descubre nuevas rutas" - Explora viajes de la comunidad
   - **Paso 4**: "Impacta positivamente" - Tu pedalada activa economías locales

2. **Given** el flujo de 4 pasos tiene iconos ilustrativos, **When** un visitante visualiza la sección, **Then** cada paso incluye:
   - Número de orden (1, 2, 3, 4)
   - Icono representativo (ej: cámara, compartir, mapa, corazón/huella)
   - Título corto (máx 5 palabras)
   - Descripción breve (máx 2 líneas)

3. **Given** un visitante está en móvil, **When** visualiza "Cómo Funciona", **Then** los 4 pasos se apilan verticalmente con separación clara entre ellos

---

### User Story 4 - Visitante Se Registra en la Plataforma (Priority: P1)

El visitante, convencido por la propuesta de valor, decide unirse a ContraVento haciendo clic en el CTA principal ("Formar parte del viaje") y completando el proceso de registro.

**Why this priority**: Es el objetivo final de conversión de la landing page. Sin un registro exitoso, todo el esfuerzo anterior no se traduce en nuevos usuarios. Debe ser frictionless y coherente con la filosofía pausada y humana.

**Independent Test**: Un visitante puede hacer clic en el CTA "Formar parte del viaje" (disponible en múltiples lugares de la landing), ser redirigido a /register, y completar el registro sin confusión o errores técnicos.

**Acceptance Scenarios**:

1. **Given** un visitante está en la landing page, **When** hace clic en el botón CTA "Formar parte del viaje" (hero section), **Then** es redirigido a la página de registro (/register) manteniendo el contexto de origen

2. **Given** un visitante scrollea hasta el final de la landing, **When** llega a la sección final de CTA, **Then** ve:
   - Mensaje inspirador final (ej: "¿Listo para pedalear con propósito?")
   - Botón CTA destacado "Formar parte del viaje" (color terracota #D35400)
   - Opción alternativa "¿Ya tienes cuenta? Inicia sesión" (enlace discreto)

3. **Given** un visitante hace clic en el CTA desde cualquier sección, **When** es redirigido a /register, **Then** el formulario de registro muestra:
   - Campos mínimos necesarios (username, email, password)
   - Diseño coherente con la estética rústica de la landing
   - Mensaje que refuerza la filosofía (ej: "Únete a una comunidad que pedalea para conectar")

4. **Given** un visitante completa el registro exitosamente, **When** verifica su email y hace login, **Then** es redirigido al dashboard con un mensaje de bienvenida coherente con el tono pausado y humano

---

### User Story 5 - Visitante Accede a Información Adicional (Footer) (Priority: P3)

El visitante, explorando la landing page, busca información complementaria como enlaces a redes sociales, términos de servicio, política de privacidad, o contacto.

**Why this priority**: Si bien es importante para credibilidad y cumplimiento legal, no es crítico para la primera impresión ni para la conversión inmediata. Un visitante puede decidir unirse sin leer el footer.

**Independent Test**: Un visitante puede scrollear hasta el final de la landing page y encontrar un footer minimalista con enlaces a redes sociales, legal (términos, privacidad), y contacto.

**Acceptance Scenarios**:

1. **Given** un visitante scrollea hasta el final de la landing, **When** llega al footer, **Then** ve:
   - Logo o nombre ContraVento (texto simple, coherente con diseño rústico)
   - Enlaces a redes sociales (Instagram, Facebook)
   - Enlaces legales: "Términos de Servicio", "Política de Privacidad"
   - Link de contacto: "Contacto" o email de soporte

2. **Given** el footer tiene enlaces externos (redes sociales), **When** un visitante hace clic en ellos, **Then** se abren en nueva pestaña sin sacar al usuario de la landing page

3. **Given** el footer está en el fondo de la página, **When** un visitante lo visualiza, **Then** el diseño es discreto, no compite visualmente con el CTA principal, y usa colores neutros de la paleta (#4A4A4A para texto, #F9F7F2 fondo)

---

### Edge Cases

- **Visitante con JavaScript deshabilitado**: La landing debe ser funcional con contenido estático (hero, manifiesto, pilares, CTA). No se requieren animaciones o interacciones complejas.
- **Visitante con conexión lenta**: Usar lazy loading para imágenes hero, formato WebP con fallback a JPG, imágenes responsivas (srcset).
- **Visitante en navegador antiguo**: Assumir compatibilidad con últimas 2 versiones de Chrome, Firefox, Safari, Edge. Degradación elegante para versiones antiguas.
- **Visitante con bloqueador de anuncios**: Evitar patrones que parezcan ads (ej: banners width=728px, popups). El CTA debe ser claramente parte del contenido orgánico.
- **Visitante que llega desde campaña de marketing**: Soportar parámetros UTM (utm_source, utm_medium, utm_campaign) sin afectar UX visible.
- **Visitante que vuelve después de registrarse**: Detectar usuario autenticado y redirigir automáticamente a /dashboard sin mostrar la landing de nuevo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La landing page DEBE ser accesible en la URL raíz (/) sin requerir autenticación
- **FR-002**: La hero section DEBE mostrar una imagen de fondo de alta calidad (min 1920x1080px) con optimización para carga rápida
- **FR-003**: El titular principal "El camino es el destino" DEBE usar tipografía serif (Playfair Display) con peso bold y tamaño prominente
- **FR-004**: La sección de manifiesto DEBE presentar los 4 pilares filosóficos en orden específico:
  1. "El camino es el destino" - No venimos a conquistar, venimos a habitar
  2. "Motor de regeneración" - Tu pedalada activa la economía de los pueblos pequeños
  3. "Solidaridad en ruta" - La comunidad se cuida y se reporta mutuamente
  4. "No dejar rastro" - Respeto absoluto al entorno natural y la cortesía rural
- **FR-005**: La sección "Pilares de Valor" DEBE mostrar 3 columnas con iconos, títulos y descripciones cortas:
  - Territorio: "Consumo local, impacto real"
  - Comunidad: "Reporte de alertas y consejos compartidos"
  - Ética: "Cortesía rural y ética de preservación"
- **FR-006**: La sección "Cómo Funciona" DEBE presentar un flujo visual de 4 pasos numerados con iconos
- **FR-007**: El botón CTA "Formar parte del viaje" DEBE estar visible en al menos 2 ubicaciones: hero section y sección final
- **FR-008**: El botón CTA DEBE usar color terracota (#D35400) con contraste adecuado para accesibilidad (WCAG AA: mínimo 4.5:1)
- **FR-009**: El footer DEBE incluir enlaces a: redes sociales (Instagram, Facebook), términos de servicio, política de privacidad, y contacto
- **FR-010**: La landing page DEBE ser responsive con breakpoints para móvil (< 768px), tablet (768-1024px), y desktop (> 1024px)
- **FR-011**: El diseño DEBE usar la paleta de colores especificada:
  - Fondo: #F9F7F2 (crema orgánico)
  - Títulos: #1B2621 (verde bosque)
  - CTA: #D35400 (terracota)
  - Texto: #4A4A4A (gris carbón)
- **FR-012**: Los textos DEBEN mantener un tono inspirador, ético, pausado y humano
- **FR-013**: El CTA "Formar parte del viaje" DEBE redirigir a la página de registro (/register)
- **FR-014**: La landing page DEBE detectar si el usuario ya está autenticado y redirigir a /dashboard automáticamente
- **FR-015**: Las imágenes DEBEN usar formato WebP con fallback a JPG para compatibilidad
- **FR-016**: La landing page DEBE cargar en menos de 3 segundos en conexión 3G
- **FR-017**: La landing page DEBE ser indexable por motores de búsqueda (meta tags, títulos semánticos, alt text)

### Key Entities

No aplica - La landing page es principalmente presentacional. No introduce nuevas entidades de datos, sino que presenta la propuesta de valor y redirige al registro existente.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los visitantes comprenden la propuesta de valor de ContraVento en menos de 10 segundos de llegar al hero section
- **SC-002**: La tasa de conversión de visitante a registro aumenta en un 25% comparado con el flujo actual
- **SC-003**: El 80% de los visitantes scrollean más allá del hero section para leer el manifiesto o pilares de valor
- **SC-004**: El tiempo promedio en la landing page es de al menos 30 segundos (indicador de interés genuino)
- **SC-005**: La landing page mantiene un Core Web Vitals score "Good":
  - Largest Contentful Paint (LCP) < 2.5s
  - First Input Delay (FID) < 100ms
  - Cumulative Layout Shift (CLS) < 0.1
- **SC-006**: El 90% de los visitantes en móvil pueden leer todos los textos sin hacer zoom
- **SC-007**: El contraste de colores cumple WCAG AA para accesibilidad (mínimo 4.5:1 para texto normal)
- **SC-008**: El botón CTA "Formar parte del viaje" es clickeado por al menos el 15% de los visitantes
- **SC-009**: La landing page genera al menos 50 registros nuevos en la primera semana post-lanzamiento
- **SC-010**: El 70% de los usuarios que registran desde la landing completan su primer viaje documentado dentro de las siguientes 2 semanas

---

## Scope & Constraints *(mandatory)*

### In Scope

- Diseño y desarrollo de la landing page responsive (móvil, tablet, desktop)
- Hero section con imagen cinematográfica y copy principal
- Sección de manifiesto con los 4 pilares filosóficos
- Sección de pilares de valor (grid 3x1: Territorio, Comunidad, Ética)
- Sección "Cómo Funciona" con flujo de 4 pasos
- CTA principal "Formar parte del viaje" con redirección a /register
- Footer minimalista con enlaces sociales, legales, y contacto
- Optimización de performance (imágenes WebP, lazy loading)
- Responsive design con breakpoints estándar
- SEO básico (meta tags, alt text, títulos semánticos)
- Detección de usuario autenticado con redirección a /dashboard

### Out of Scope

- Sistema de blog o sección de noticias en la landing
- Integración de testimonios de usuarios (puede añadirse en versión futura)
- Formulario de contacto embebido (se usa link a email o página separada)
- Animaciones complejas o parallax scrolling (mantener diseño pausado y simple)
- Personalización de contenido basada en ubicación geográfica del visitante
- A/B testing de variantes de copy o diseño (se hará manualmente post-lanzamiento)
- Integración de chat en vivo o chatbot
- Sistema de newsletter embebido en la landing (puede añadirse después)
- Rediseño de las páginas de registro/login existentes (se mantienen, solo mejora redirección)

### Constraints

- **Diseño coherente**: Respetar la paleta de colores y tipografía especificada
- **Performance**: Página debe cargar en < 3s en conexión 3G (budget: < 500KB inicial)
- **Compatibilidad**: Últimas 2 versiones de Chrome, Firefox, Safari, Edge
- **Accesibilidad**: Cumplir WCAG 2.1 nivel AA (contraste, navegación por teclado, alt text)
- **SEO**: Meta tags obligatorios (title, description, og:image, canonical)
- **Responsividad**: Mobile-first design, breakpoints estándar (768px, 1024px)
- **Reutilización**: Usar componentes React existentes cuando sea posible
- **Integración**: Coexistir con PublicFeedPage (que se mueve a /trips/public) sin romper rutas
- **Backend**: No requiere cambios en backend (usa endpoints de auth existentes)

---

## Assumptions *(mandatory)*

1. **Imágenes disponibles**: El equipo proveerá imágenes de alta calidad para el hero section con licencia apropiada
2. **Copy final aprobado**: Los textos del manifiesto y pilares ya están definidos en feature/landing_page.md
3. **Iconos**: Se usarán iconos de biblioteca open-source (Heroicons, Feather Icons) coherentes con estilo minimalista
4. **Tipografía**: Playfair Display está disponible vía Google Fonts sin costo
5. **Redes sociales**: ContraVento tiene presencia en Instagram y Facebook con URLs válidas
6. **Documentos legales**: Ya existen o se crearán páginas de "Términos de Servicio" y "Política de Privacidad"
7. **Tráfico inicial**: Campaña de marketing generará al menos 500 visitantes en primera semana post-lanzamiento
8. **Usuario autenticado**: Se puede detectar mediante AuthContext de React sin cambios backend
9. **Registro existente**: La página /register funciona correctamente y no requiere modificaciones
10. **Analytics**: Ya existe integración de analytics para medir conversiones y engagement
11. **Hosting/Deployment**: La landing se desplegará en el mismo dominio, sin subdominio separado
12. **Mantenimiento de contenido**: El copy es estático (hardcoded), no requiere CMS

---

## Dependencies *(mandatory)*

### External Dependencies

- **Google Fonts API**: Para cargar tipografía Playfair Display
- **Biblioteca de iconos**: Heroicons o Feather Icons (MIT license)
- **Imágenes**: Proveedor externo para imagen hero cinematográfica

### Internal Dependencies

- **AuthContext (React)**: Para detectar si el usuario está autenticado
- **Página de registro (/register)**: Debe estar funcional para recibir tráfico del CTA
- **Router de React**: Para manejar ruta raíz (/) y redirecciones
- **Componentes existentes**: Reutilizar botones si el estilo es coherente
- **SEO configuration**: Archivo de meta tags (Helmet en React)

### Feature Dependencies

- **Feature 005 (Frontend User Auth)**: Ya completada - proporciona AuthContext
- **Feature 013 (Public Trips Feed)**: Ya completada - coexistirá moviéndola a /trips/public

---

## Open Questions *(if any)*

Ninguna pregunta abierta. Todas las decisiones clave han sido resueltas con defaults razonables:
- Pilares de valor: Estáticos con hover sutil (no expandibles)
- Redes sociales: Instagram + Facebook
- Usuarios autenticados: Redirigir automáticamente a /dashboard
