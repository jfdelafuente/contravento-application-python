# Feature Specification: Frontend de Autenticación y Perfiles de Usuario

**Feature Branch**: `005-frontend-user-profile`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Vamos a construir el frontend para la funcionalidad 001-user-profile donde el usuario pueda registrarse, logarse, recuperar la password, logout, verificar email en ContraVento"

## Clarifications

### Session 2026-01-08

- Q: Which CAPTCHA solution should be integrated for anti-bot protection during user registration? → A: Cloudflare Turnstile
- Q: Should special characters (símbolos) be required or optional in password validation? → A: Optional and not considered - only length, uppercase, lowercase, numbers affect strength
- Q: What level of access should unverified users have after registration? → A: Complete block - Cannot login at all until email verified
- Q: What color scheme should be used for the password strength indicator (débil/media/fuerte)? → A: Red/Yellow/Green - Standard traffic light pattern
- Q: When should real-time validation trigger for email and password fields? → A: Debounced keystroke - Wait 300-500ms after user stops typing before validating
- Q: How should JWT tokens be stored in the frontend for session management? → A: HttpOnly Cookies (backend managed) - Most secure, immune to XSS
- Q: How should the "Recordarme" (Remember Me) checkbox affect token duration and refresh token behavior? → A: Separate access/refresh tokens - Access token (15min), refresh token (30 days if "Recordarme", session-only if not)
- Q: What specific information should be displayed when a user account is temporarily blocked after failed login attempts? → A: Message with countdown and reason - Show block duration, reason (múltiples intentos fallidos), and live countdown timer
- Q: Should Two-Factor Authentication (2FA) be included in this frontend authentication feature scope? → A: Out of scope - Keep as separate future feature (will be implemented in dedicated feature 006-two-factor-auth)
- Q: What happens to the failed login attempt counter after the temporary account block (15 minutes) expires? → A: Reset counter after block expires - User gets 5 fresh attempts after timeout

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro de Nuevo Usuario (Priority: P1)

Un ciclista visita ContraVento por primera vez y quiere crear una cuenta. Accede a la página de registro donde introduce su nombre de usuario, email y contraseña. El formulario le muestra validaciones en tiempo real para cada campo. Al enviar el formulario, ve un mensaje confirmando que se ha enviado un email de verificación a su correo.

**Why this priority**: Es la puerta de entrada principal para nuevos usuarios. Sin esta funcionalidad, nadie puede unirse a la plataforma. Es el primer contacto del usuario con la interfaz y debe ser simple, claro y sin fricciones.

**Independent Test**: Puede ser probado completamente llenando el formulario de registro con datos válidos, enviándolo, y verificando que aparece el mensaje de confirmación de email enviado. Entrega valor inmediato al permitir que usuarios nuevos se registren.

**Acceptance Scenarios**:

1. **Given** un visitante en la página de inicio, **When** hace clic en "Registrarse", **Then** accede a un formulario limpio con campos para nombre de usuario, email y contraseña
2. **Given** un usuario llenando el formulario de registro, **When** escribe un nombre de usuario inválido (menos de 3 caracteres o caracteres especiales), **Then** ve un mensaje de error debajo del campo explicando los requisitos
3. **Given** un usuario llenando el formulario de registro, **When** escribe un email con formato inválido, **Then** ve un mensaje de error indicando que el formato del email es incorrecto
4. **Given** un usuario llenando el formulario de registro, **When** escribe una contraseña débil (menos de 8 caracteres o sin mayúsculas/números), **Then** ve un indicador visual de fortaleza de contraseña en rojo y mensajes con los requisitos faltantes
5. **Given** un usuario con todos los campos válidos, **When** envía el formulario, **Then** el botón muestra un spinner de carga y queda deshabilitado
6. **Given** un usuario con todos los campos válidos, **When** envía el formulario, **Then** Cloudflare Turnstile valida que no es un bot (invisiblemente en la mayoría de casos)
7. **Given** un registro exitoso, **When** el servidor responde correctamente, **Then** el usuario ve una pantalla de confirmación indicando que debe verificar su email
8. **Given** un usuario intentando registrarse con un email ya existente, **When** el servidor responde con error, **Then** ve un mensaje claro debajo del campo email indicando que ya está registrado con enlace a login
9. **Given** un error de conexión durante el registro, **When** el servidor no responde, **Then** ve un mensaje de error general con opción de reintentar

---

### User Story 2 - Inicio de Sesión (Priority: P1)

Un ciclista con cuenta existente quiere acceder a su perfil. Accede a la página de login donde introduce su email/nombre de usuario y contraseña. Al autenticarse correctamente, es redirigido a su dashboard personal.

**Why this priority**: Es igualmente crítico que el registro. Los usuarios recurrentes necesitan poder acceder a sus cuentas de forma rápida y segura. Es una funcionalidad que se usa en cada sesión.

**Independent Test**: Puede ser probado completamente con una cuenta existente, introduciendo credenciales correctas, y verificando que el usuario es redirigido a su área personal con su información de usuario visible.

**Acceptance Scenarios**:

1. **Given** un visitante en la página de inicio, **When** hace clic en "Iniciar Sesión", **Then** accede a un formulario con campos para email/username y contraseña
2. **Given** un usuario en el formulario de login, **When** introduce credenciales válidas y envía, **Then** el botón muestra spinner y queda deshabilitado durante la autenticación
3. **Given** credenciales correctas, **When** el servidor responde exitosamente, **Then** el usuario es redirigido a su dashboard y puede ver su nombre/foto en la barra de navegación
4. **Given** credenciales incorrectas, **When** el servidor responde con error de autenticación, **Then** el usuario ve un mensaje claro indicando "Email o contraseña incorrectos"
5. **Given** un usuario bloqueado temporalmente (5 intentos fallidos), **When** intenta iniciar sesión, **Then** ve un mensaje indicando que la cuenta está bloqueada temporalmente y cuánto tiempo debe esperar
6. **Given** un usuario con cuenta no verificada, **When** intenta iniciar sesión, **Then** ve un mensaje indicando que debe verificar su email con opción de reenviar el email de verificación
7. **Given** un usuario autenticado, **When** cierra el navegador y vuelve a abrir, **Then** sigue autenticado si no ha pasado el tiempo de expiración de sesión
8. **Given** un usuario en el formulario de login, **When** hace clic en "¿Olvidaste tu contraseña?", **Then** es redirigido a la página de recuperación de contraseña

---

### User Story 3 - Recuperación de Contraseña (Priority: P2)

Un ciclista olvidó su contraseña y necesita recuperar el acceso a su cuenta. Accede a la página de recuperación, introduce su email, recibe un correo con un enlace especial, hace clic en el enlace, y puede establecer una nueva contraseña.

**Why this priority**: Es una funcionalidad de soporte crítica que evita que usuarios pierdan acceso permanente a sus cuentas. Aunque no se usa frecuentemente, su ausencia generaría frustración y tickets de soporte.

**Independent Test**: Puede ser probado introduciendo un email registrado, verificando que se muestra mensaje de confirmación, siguiendo el enlace del email (se puede simular), e introduciendo una nueva contraseña válida.

**Acceptance Scenarios**:

1. **Given** un usuario en la página de login, **When** hace clic en "¿Olvidaste tu contraseña?", **Then** accede a un formulario pidiendo su email
2. **Given** un usuario en el formulario de recuperación, **When** introduce un email válido y envía, **Then** ve un mensaje indicando que se ha enviado un enlace de recuperación a ese email (sin revelar si el email existe o no por seguridad)
3. **Given** un usuario que recibió el email de recuperación, **When** hace clic en el enlace, **Then** es redirigido a una página para establecer nueva contraseña
4. **Given** un usuario en la página de nueva contraseña, **When** introduce una contraseña válida y confirma, **Then** ve validación en tiempo real de fortaleza de contraseña
5. **Given** un usuario con contraseña válida confirmada, **When** envía el formulario, **Then** ve un mensaje de éxito y es redirigido automáticamente al login
6. **Given** un usuario con un token de recuperación expirado (más de 1 hora), **When** intenta acceder al enlace, **Then** ve un mensaje indicando que el enlace ha expirado con opción de solicitar uno nuevo
7. **Given** un usuario que ya usó un token de recuperación, **When** intenta usarlo nuevamente, **Then** ve un mensaje indicando que el enlace ya fue utilizado

---

### User Story 4 - Verificación de Email (Priority: P2)

Un nuevo ciclista registrado recibe un email con un enlace de verificación. Al hacer clic en el enlace, su cuenta se activa y puede iniciar sesión en la plataforma.

**Why this priority**: Es parte del flujo de seguridad y prevención de spam. El acceso está completamente bloqueado hasta la verificación, asegurando que todos los usuarios tengan emails válidos.

**Independent Test**: Puede ser probado registrando una cuenta nueva, simulando clic en el enlace de verificación del email, y verificando que aparece mensaje de confirmación con redirección al login o dashboard.

**Acceptance Scenarios**:

1. **Given** un usuario recién registrado, **When** hace clic en el enlace de verificación del email, **Then** es redirigido a una página de confirmación mostrando "Email verificado exitosamente"
2. **Given** un email verificado exitosamente, **When** el usuario está en la página de confirmación, **Then** ve un botón para "Iniciar sesión" y puede acceder a la plataforma
3. **Given** un usuario con un token de verificación expirado, **When** hace clic en el enlace, **Then** ve un mensaje indicando que el enlace ha expirado con opción de reenviar verificación
4. **Given** un usuario ya verificado, **When** intenta usar el mismo enlace de verificación nuevamente, **Then** ve un mensaje indicando que la cuenta ya está verificada
5. **Given** un usuario no verificado intentando iniciar sesión, **When** introduce credenciales correctas, **Then** ve un mensaje indicando que debe verificar su email con opción de reenviar email de verificación
6. **Given** un usuario solicitando reenvío de verificación desde el mensaje de login, **When** hace clic en "Reenviar email", **Then** ve confirmación de envío y el botón queda deshabilitado temporalmente para prevenir spam

---

### User Story 5 - Cierre de Sesión (Priority: P2)

Un ciclista autenticado quiere cerrar su sesión de forma segura, especialmente si está usando un dispositivo compartido. Hace clic en el botón de logout en el menú de usuario y su sesión se invalida.

**Why this priority**: Es importante para seguridad, especialmente en dispositivos compartidos, pero no es tan crítico como login/registro. Los usuarios pueden simplemente cerrar el navegador si están en dispositivos personales.

**Independent Test**: Puede ser probado autenticándose, haciendo clic en el botón de logout, y verificando que el usuario es redirigido a la página pública y ya no tiene acceso a rutas protegidas.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en cualquier página, **When** hace clic en su foto/nombre en la barra de navegación, **Then** se despliega un menú con opción "Cerrar sesión"
2. **Given** un usuario en el menú desplegable, **When** hace clic en "Cerrar sesión", **Then** ve una confirmación rápida ("¿Seguro que quieres cerrar sesión?") o se cierra directamente
3. **Given** un usuario cerrando sesión, **When** la sesión se invalida, **Then** es redirigido a la página de inicio pública
4. **Given** un usuario que cerró sesión, **When** intenta acceder a una ruta protegida mediante URL directa, **Then** es redirigido automáticamente al login
5. **Given** un usuario que cerró sesión, **When** vuelve a la página, **Then** la navegación muestra botones de "Iniciar Sesión" y "Registrarse" en lugar de menú de usuario

---

### User Story 6 - Navegación y Persistencia de Sesión (Priority: P3)

Un ciclista autenticado navega por diferentes páginas de la plataforma. Su estado de autenticación se mantiene consistente, puede ver su información de usuario en la barra de navegación, y tiene acceso a rutas protegidas sin necesidad de volver a autenticarse.

**Why this priority**: Es importante para la experiencia de usuario fluida, pero depende de que las funcionalidades básicas de autenticación funcionen primero. Mejora la UX pero no es bloqueante.

**Independent Test**: Puede ser probado autenticándose, navegando entre diferentes páginas (perfil, trips, etc.), refrescando el navegador, y verificando que el estado de autenticación persiste correctamente.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** navega a cualquier página de la plataforma, **Then** ve su foto de perfil y nombre en la esquina superior derecha de la barra de navegación
2. **Given** un usuario autenticado navegando, **When** refresca el navegador en cualquier página, **Then** su sesión persiste y no necesita volver a autenticarse
3. **Given** un usuario con sesión expirada (30 días de inactividad), **When** intenta acceder a una página protegida, **Then** ve un mensaje indicando que su sesión expiró y es redirigido al login
4. **Given** un usuario autenticado, **When** intenta acceder a las páginas de login o registro mediante URL directa, **Then** es redirigido automáticamente a su dashboard
5. **Given** un usuario no autenticado, **When** intenta acceder a una ruta protegida, **Then** es redirigido al login con parámetro de retorno para volver a la página después de autenticarse

---

### Edge Cases

- ¿Qué sucede si un usuario intenta registrarse mientras ya está autenticado?
- ¿Cómo maneja el frontend la pérdida de conexión a internet durante el envío de formularios?
- ¿Qué pasa si el backend responde con errores inesperados (500 Internal Server Error)?
- ¿Cómo se comporta la aplicación si el token JWT expira mientras el usuario está navegando activamente?
- ¿Qué ocurre si un usuario abre múltiples pestañas y cierra sesión en una de ellas?
- ¿Cómo se manejan caracteres especiales o scripts maliciosos en campos de entrada (XSS prevention)?
- ¿Qué sucede si un usuario hace múltiples clics rápidos en el botón de submit durante el registro/login?
- ¿Cómo se comporta el frontend en dispositivos móviles con pantallas pequeñas?
- ¿Qué pasa si los campos de formulario contienen espacios en blanco al inicio o final?
- ¿Cómo se maneja la navegación con botón de "atrás" del navegador después de logout?
- ¿Qué ocurre con el contador de intentos fallidos después de que expira el bloqueo temporal de 15 minutos? (Respuesta: El contador se resetea, usuario obtiene 5 intentos nuevos)

## Requirements *(mandatory)*

### Functional Requirements

**Pantallas y Navegación:**

- **FR-001**: El sistema DEBE proporcionar una página de registro accesible desde la navegación principal
- **FR-002**: El sistema DEBE proporcionar una página de login accesible desde la navegación principal
- **FR-003**: El sistema DEBE proporcionar una página de recuperación de contraseña accesible desde el formulario de login
- **FR-004**: El sistema DEBE proporcionar una página de verificación de email accesible mediante enlace del email
- **FR-005**: El sistema DEBE proporcionar una página de establecer nueva contraseña accesible mediante enlace del email de recuperación
- **FR-006**: El sistema DEBE mostrar una barra de navegación diferente para usuarios autenticados vs no autenticados
- **FR-007**: El sistema DEBE redirigir automáticamente a usuarios no autenticados que intenten acceder a rutas protegidas
- **FR-008**: El sistema DEBE redirigir automáticamente a usuarios autenticados que intenten acceder a login/registro

**Formulario de Registro:**

- **FR-009**: El formulario de registro DEBE incluir campos para: nombre de usuario, email, contraseña, confirmar contraseña
- **FR-010**: El formulario DEBE validar en tiempo real el formato del nombre de usuario (3-30 caracteres alfanuméricos y guiones) con debounce de 300-500ms después de que el usuario deje de escribir
- **FR-011**: El formulario DEBE validar en tiempo real el formato del email con debounce de 300-500ms después de que el usuario deje de escribir
- **FR-012**: El formulario DEBE validar en tiempo real la fortaleza de la contraseña (mínimo 8 caracteres, mayúscula, minúscula, número) con debounce de 300-500ms después de que el usuario deje de escribir
- **FR-013**: El formulario DEBE mostrar un indicador visual de fortaleza de contraseña usando colores estándar: rojo (débil), amarillo (media), verde (fuerte), basado en longitud, presencia de mayúsculas, minúsculas y números (símbolos especiales permitidos pero no considerados en el cálculo)
- **FR-014**: El formulario DEBE validar que la confirmación de contraseña coincide con la contraseña
- **FR-015**: El formulario DEBE deshabilitar el botón de submit mientras haya errores de validación
- **FR-016**: El formulario DEBE mostrar spinner en el botón y deshabilitar todos los campos durante el envío
- **FR-017**: El formulario DEBE limpiar espacios en blanco al inicio y final de campos de texto antes de enviar
- **FR-018**: El formulario DEBE mostrar mensajes de error específicos recibidos del backend (email duplicado, username duplicado)
- **FR-019**: El sistema DEBE mostrar una pantalla de confirmación después de registro exitoso indicando verificación de email
- **FR-020**: El formulario de registro DEBE integrar Cloudflare Turnstile para protección anti-bot antes de permitir el envío
- **FR-021**: El CAPTCHA DEBE validarse de forma invisible cuando sea posible, minimizando fricción para usuarios legítimos

**Formulario de Login:**

- **FR-022**: El formulario de login DEBE incluir campos para: email/username, contraseña
- **FR-023**: El formulario DEBE permitir login con email O nombre de usuario indistintamente
- **FR-024**: El formulario DEBE incluir un checkbox "Recordarme" que determina si el refresh token persiste 30 días (marcado) o solo durante la sesión del navegador (no marcado)
- **FR-025**: El formulario DEBE incluir un enlace a recuperación de contraseña
- **FR-026**: El formulario DEBE mostrar spinner y deshabilitar campos durante la autenticación
- **FR-027**: El formulario DEBE mostrar mensajes de error claros: credenciales incorrectas, cuenta bloqueada, cuenta no verificada
- **FR-028**: El formulario DEBE mostrar un mensaje claro cuando la cuenta está bloqueada: razón (múltiples intentos fallidos), duración del bloqueo (15 minutos), y contador en tiempo real del tiempo restante (formato MM:SS)
- **FR-029**: El backend DEBE establecer el token JWT en una HttpOnly cookie después de login exitoso (el frontend no tiene acceso directo al token para máxima seguridad)
- **FR-030**: El sistema DEBE redirigir al usuario a su dashboard (o página de retorno) después de login exitoso
- **FR-031**: El sistema DEBE usar dos tokens separados: access token (15 minutos de duración) y refresh token (30 días si "Recordarme", sesión si no)
- **FR-032**: El sistema DEBE refrescar automáticamente el access token cuando expire usando el refresh token (llamada transparente al backend)
- **FR-033**: El sistema DEBE redirigir al login si el refresh token también ha expirado o es inválido

**Recuperación de Contraseña:**

- **FR-034**: La página de recuperación DEBE incluir un formulario con campo de email
- **FR-035**: El formulario DEBE mostrar mensaje de confirmación genérico después de enviar (sin revelar si el email existe)
- **FR-036**: La página de nueva contraseña DEBE validar que el token en la URL es válido antes de mostrar el formulario
- **FR-037**: La página de nueva contraseña DEBE incluir campos para: nueva contraseña, confirmar nueva contraseña
- **FR-038**: El formulario DEBE validar fortaleza de la nueva contraseña igual que en registro
- **FR-039**: El formulario DEBE mostrar mensajes de error si el token ha expirado o ya fue usado
- **FR-040**: El sistema DEBE redirigir automáticamente al login después de cambio de contraseña exitoso

**Verificación de Email:**

- **FR-041**: La página de verificación DEBE validar automáticamente el token en la URL al cargar
- **FR-042**: La página DEBE mostrar mensaje de éxito si la verificación fue exitosa
- **FR-043**: La página DEBE mostrar mensaje de error si el token ha expirado o es inválido
- **FR-044**: La página DEBE proporcionar botón para reenviar email de verificación si el token expiró
- **FR-045**: La página DEBE proporcionar botón para ir al login después de verificación exitosa
- **FR-046**: El sistema DEBE bloquear completamente el acceso (login) a usuarios no verificados
- **FR-047**: El mensaje de error al intentar login sin verificar DEBE incluir opción para reenviar email de verificación

**Gestión de Sesión:**

- **FR-048**: El sistema DEBE usar HttpOnly cookies para almacenar el token JWT (establecidas por el backend, inaccesibles desde JavaScript)
- **FR-049**: El navegador DEBE enviar automáticamente la cookie HttpOnly con cada petición a APIs protegidas (sin intervención del frontend)
- **FR-050**: El sistema DEBE validar la existencia y validez de la sesión al cargar cada ruta protegida
- **FR-051**: El sistema DEBE manejar automáticamente la expiración del access token usando el refresh token
- **FR-052**: El sistema DEBE invalidar ambas cookies (access y refresh) al cerrar sesión (mediante llamada al endpoint de logout del backend)
- **FR-053**: El sistema DEBE sincronizar el estado de autenticación entre múltiples pestañas del navegador
- **FR-054**: El sistema DEBE mostrar foto de perfil y nombre del usuario autenticado en la barra de navegación
- **FR-055**: El sistema DEBE proporcionar un menú desplegable en la navegación con opción de logout

**Manejo de Errores y Validación:**

- **FR-056**: Todos los formularios DEBEN mostrar mensajes de error en español con instrucciones claras
- **FR-057**: Los mensajes de validación DEBEN aparecer debajo de cada campo específico
- **FR-058**: El sistema DEBE prevenir doble envío de formularios deshabilitando el botón después del primer clic
- **FR-059**: El sistema DEBE mostrar mensajes de error de red cuando no hay conexión a internet
- **FR-060**: El sistema DEBE proporcionar opción de "Reintentar" cuando falla una petición de red
- **FR-061**: El sistema DEBE sanitizar todas las entradas de usuario para prevenir XSS

**Responsive y Accesibilidad:**

- **FR-062**: Todas las páginas de autenticación DEBEN ser completamente responsive (mobile, tablet, desktop)
- **FR-063**: Los formularios DEBEN ser accesibles mediante teclado (navegación con Tab, Enter para submit)
- **FR-064**: Los campos de contraseña DEBEN incluir botón para mostrar/ocultar contraseña
- **FR-065**: Los mensajes de error DEBEN ser anunciados por lectores de pantalla

### Key Entities

- **AuthState**: Estado de autenticación de la aplicación. Atributos: usuario autenticado (objeto User o null), token JWT, estado de carga, errores de autenticación

- **User**: Información del usuario autenticado. Atributos: id, username, email, foto de perfil, email verificado, fecha de registro

- **FormValidation**: Estado de validación de formularios. Atributos: errores por campo, formulario válido (booleano), estado de envío

- **RegisterFormData**: Datos del formulario de registro. Atributos: username, email, password, confirmPassword

- **LoginFormData**: Datos del formulario de login. Atributos: emailOrUsername, password, rememberMe

- **PasswordResetFormData**: Datos para recuperación de contraseña. Atributos: email (solicitud) o newPassword + confirmPassword (cambio)

- **TokenValidation**: Estado de validación de tokens (verificación email, recuperación contraseña). Atributos: token válido (booleano), token expirado (booleano), mensaje de error

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Eficiencia de Registro:**

- **SC-001**: Los usuarios pueden completar el formulario de registro en menos de 90 segundos sin errores
- **SC-002**: El formulario de registro responde a validaciones en tiempo real en menos de 200ms por campo
- **SC-003**: El 90% de los usuarios completan el registro exitosamente en el primer intento (sin abandonar el formulario)
- **SC-004**: La página de registro carga completamente en menos de 2 segundos

**Eficiencia de Login:**

- **SC-005**: Los usuarios pueden iniciar sesión en menos de 15 segundos desde que acceden al formulario
- **SC-006**: El proceso de autenticación responde en menos de 1 segundo después de enviar credenciales
- **SC-007**: El 95% de los usuarios inician sesión exitosamente en el primer intento con credenciales correctas
- **SC-008**: La redirección al dashboard después de login ocurre en menos de 500ms

**Recuperación de Contraseña:**

- **SC-009**: Los usuarios pueden solicitar recuperación de contraseña en menos de 30 segundos
- **SC-010**: Los usuarios pueden establecer nueva contraseña en menos de 60 segundos después de hacer clic en el enlace del email
- **SC-011**: El 85% de los usuarios completan exitosamente el cambio de contraseña en el primer intento

**Verificación de Email:**

- **SC-012**: La verificación de email ocurre instantáneamente (menos de 1 segundo) al hacer clic en el enlace
- **SC-013**: El 90% de los usuarios entienden que deben verificar su email sin necesidad de soporte adicional
- **SC-014**: El reenvío de email de verificación tiene un cooldown de al menos 60 segundos para prevenir spam

**Experiencia de Usuario:**

- **SC-015**: Todos los formularios muestran feedback visual inmediato (menos de 100ms) al interactuar con campos
- **SC-016**: El 90% de los mensajes de error son comprensibles sin necesidad de consultar documentación
- **SC-017**: Los usuarios pueden navegar todos los formularios completamente usando solo el teclado
- **SC-018**: Las páginas de autenticación funcionan correctamente en pantallas desde 320px de ancho (móviles pequeños)

**Seguridad:**

- **SC-019**: Cero vulnerabilidades XSS en campos de entrada de formularios
- **SC-020**: Los tokens JWT se almacenan de forma segura (no accesibles desde JavaScript si se usa httpOnly)
- **SC-021**: Las contraseñas nunca se muestran en texto plano en el código HTML o consola del navegador
- **SC-022**: Los tokens de verificación y recuperación se validan en el backend antes de permitir acciones

**Performance:**

- **SC-023**: El bundle de JavaScript para autenticación es menor a 100KB (gzipped)
- **SC-024**: El tiempo de carga inicial de cualquier página de autenticación es menor a 3 segundos en conexiones 3G
- **SC-025**: El sistema maneja correctamente pérdida de conexión con mensajes claros y opción de reintentar

**Persistencia de Sesión:**

- **SC-026**: La sesión del usuario persiste correctamente después de refrescar el navegador en el 100% de casos
- **SC-027**: El cierre de sesión en una pestaña se sincroniza con otras pestañas abiertas en menos de 2 segundos
- **SC-028**: Los usuarios no autenticados son redirigidos al login en menos de 200ms al intentar acceder rutas protegidas

**Compatibilidad:**

- **SC-029**: La interfaz funciona correctamente en los últimos 2 años de versiones de Chrome, Firefox, Safari y Edge
- **SC-030**: La interfaz es completamente usable en dispositivos touch (móviles y tablets)

## Assumptions

1. **Framework Frontend**: La aplicación se construirá con React y TypeScript para type safety
2. **Gestión de Estado**: Se usará Context API o Redux para manejar el estado de autenticación globalmente
3. **Enrutamiento**: Se usará React Router para navegación y protección de rutas
4. **Validación de Formularios**: Se implementará validación tanto del lado del cliente (UX inmediata) como validación final en el backend
5. **Estilos**: La interfaz seguirá un sistema de diseño consistente con componentes reutilizables
6. **API Backend**: El backend (especificado en 001-user-profiles) está implementado y funcional con los siguientes endpoints:
   - POST /auth/register
   - POST /auth/login
   - POST /auth/logout
   - POST /auth/password-reset/request
   - POST /auth/password-reset/confirm
   - GET /auth/verify-email?token=xxx
   - POST /auth/resend-verification
7. **Formato de Respuestas**: El backend responde en formato JSON con estructura consistente:
   ```json
   {
     "success": true/false,
     "data": {...},
     "error": { "code": "ERROR_CODE", "message": "Mensaje en español" }
   }
   ```
8. **JWT Token**: El backend establece el token JWT en una HttpOnly cookie (no retornado en el body de la respuesta) y retorna solo la información del usuario:
   ```json
   {
     "success": true,
     "data": {
       "user": { "id": "...", "username": "...", "email": "...", ... }
     }
   }
   ```
9. **Almacenamiento de Token**: El token JWT se almacena exclusivamente en HttpOnly cookies establecidas por el backend (inaccesible desde JavaScript del frontend para prevenir XSS)
10. **Idioma**: Toda la interfaz está en español (mensajes de error, labels, placeholders, etc.)
11. **Email Transaccional**: Los emails de verificación y recuperación se envían desde el backend; el frontend solo muestra mensajes de confirmación
12. **Redirecciones**: Después de login exitoso, los usuarios son redirigidos a `/dashboard` o a la página que intentaban acceder antes del login
13. **Sesiones Múltiples**: El sistema permite múltiples sesiones activas (varios dispositivos), pero sincroniza logout entre pestañas del mismo navegador
14. **Expiración de Token**: El frontend maneja la expiración del token limpiando el estado y redirigiendo al login

## Out of Scope

Las siguientes funcionalidades NO están incluidas en esta especificación:

- Vista y edición de perfil público (será especificación separada: frontend-user-profile-management)
- Visualización de estadísticas del usuario (será especificación separada)
- Funcionalidad de seguir/dejar de seguir usuarios
- Autenticación mediante OAuth (Google, Facebook, Strava)
- Autenticación de dos factores (2FA)
- Recordar credenciales con autocompletar del navegador (se permite pero no se implementa activamente)
- Gestión de sesiones activas (ver dispositivos donde hay sesión abierta)
- Cambio de contraseña desde el perfil (solo recuperación cuando se olvida)
- Cambio de email desde el perfil
- Eliminación de cuenta
- Modo oscuro/claro en la interfaz de autenticación
- Internacionalización (i18n) para otros idiomas
- Tests E2E automatizados (pueden añadirse posteriormente)
- Animaciones complejas o transiciones entre páginas
- Sistema de notificaciones push
- Integración con gestores de contraseñas (se permite pero no se implementa activamente)
