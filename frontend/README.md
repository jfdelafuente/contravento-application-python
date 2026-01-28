# ContraVento Frontend

Plataforma social para ciclistas - Interfaz de usuario moderna construida con React + TypeScript.

## 🚀 Inicio Rápido

### Prerequisitos

- Node.js 18+
- npm 9+

### Instalación

```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus configuraciones

# Iniciar servidor de desarrollo
npm run dev
```

La aplicación estará disponible en `http://localhost:3001`

## 📋 Comandos Disponibles

```bash
# Desarrollo
npm run dev          # Iniciar servidor de desarrollo con hot reload
npm run build        # Construir para producción
npm run preview      # Previsualizar build de producción
npm run lint         # Ejecutar linter (ESLint)
npm run type-check   # Verificar tipos TypeScript
```

## 🏗️ Arquitectura

### Estructura de Directorios

```
frontend/
├── src/
│   ├── components/         # Componentes reutilizables
│   │   ├── auth/          # Componentes de autenticación
│   │   ├── common/        # Componentes compartidos
│   │   └── routing/       # Componentes de enrutamiento
│   ├── contexts/          # React Context (estado global)
│   ├── hooks/             # Custom React hooks
│   ├── pages/             # Páginas/Vistas principales
│   ├── services/          # Servicios API y lógica de negocio
│   ├── styles/            # Estilos globales
│   ├── types/             # Definiciones TypeScript
│   ├── utils/             # Utilidades y helpers
│   ├── App.tsx            # Componente raíz
│   └── main.tsx           # Entry point
├── public/                # Archivos estáticos
└── index.html             # HTML principal
```

### Tecnologías Principales

- **React 18**: UI library con hooks y concurrent features
- **TypeScript 5**: Tipado estático
- **Vite**: Build tool y dev server
- **React Router 6**: Enrutamiento client-side
- **Axios**: Cliente HTTP con interceptores
- **React Hook Form**: Gestión de formularios
- **Zod**: Validación de esquemas
- **Cloudflare Turnstile**: Protección CAPTCHA

### Patrones de Diseño

#### 1. Autenticación HttpOnly Cookie

```typescript
// El token se gestiona automáticamente vía cookies HttpOnly
// No se almacena en localStorage (seguridad XSS)
await authService.login(email, password, rememberMe);
// Token establecido por backend en cookie HttpOnly
```

#### 2. Context API para Estado Global

```typescript
// AuthContext proporciona estado de autenticación global
const { user, isAuthenticated, login, logout } = useAuth();
```

#### 3. Protected Routes

```typescript
// Rutas protegidas con verificación de autenticación
<ProtectedRoute requireVerified={true}>
  <DashboardPage />
</ProtectedRoute>
```

#### 4. Lazy Loading

```typescript
// Carga diferida de rutas no críticas
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
```

#### 5. Error Boundary

```typescript
// Captura errores y muestra UI de respaldo
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

## 🔐 Seguridad

### Implementaciones de Seguridad

1. **HttpOnly Cookies**: Tokens JWT en cookies seguras (inmune a XSS)
2. **CAPTCHA**: Cloudflare Turnstile en registro y recuperación de contraseña
3. **Rate Limiting**: Protección contra intentos de login masivos
4. **Account Blocking**: Bloqueo temporal tras 5 intentos fallidos
5. **CSP Headers**: Content Security Policy headers configurados
6. **Input Validation**: Validación client y server-side con Zod
7. **Password Strength**: Medidor visual de fortaleza de contraseña

### Variables de Entorno

```bash
# .env.local
VITE_API_URL=http://localhost:8000           # URL del backend API
VITE_TURNSTILE_SITE_KEY=your_site_key        # Clave pública Turnstile
VITE_ENV=development                          # Entorno (development/production)
VITE_DEBUG=true                               # Habilitar logs de debug
```

⚠️ **Nunca** commits `.env.local` al repositorio

## 🎨 Componentes Principales

### Autenticación

- **RegisterForm**: Registro con validación en tiempo real
- **LoginForm**: Login con Remember Me y manejo de bloqueos
- **ForgotPasswordForm**: Solicitud de recuperación de contraseña
- **ResetPasswordForm**: Restablecimiento con validación de token
- **VerifyEmailPage**: Verificación de email con resend
- **UserMenu**: Menú de usuario con navegación y logout

### Utilidades

- **useDebounce**: Debouncing para validaciones asíncronas
- **useCountdown**: Temporizador de cuenta regresiva
- **passwordStrength**: Cálculo de fortaleza de contraseña
- **validators**: Validadores de email, username, etc.

## 🧪 Testing

```bash
# Ejecutar tests unitarios
npm run test

# Tests con coverage
npm run test:coverage

# Tests en modo watch
npm run test:watch
```

### Estrategia de Testing

- **Unit Tests**: Utilidades y funciones puras (≥90% coverage target)
- **Component Tests**: Componentes con @testing-library/react
- **Integration Tests**: Flujos completos de usuario
- **E2E Tests**: Cypress para flujos críticos (futuro)

## 📦 Build y Deployment

### Build de Producción

```bash
# Generar build optimizado
npm run build

# Output en dist/
# - Minificado y tree-shaken
# - Chunks separados para mejor caching
# - Source maps opcionales
```

### Optimizaciones

- **Code Splitting**: Lazy loading de rutas protegidas
- **Tree Shaking**: Eliminación de código no utilizado
- **Asset Optimization**: Minificación de CSS/JS
- **Bundle Analysis**: Verificar tamaño <200KB inicial

### Variables de Producción

```bash
VITE_API_URL=https://api.contravento.app
VITE_TURNSTILE_SITE_KEY=production_key
VITE_ENV=production
VITE_DEBUG=false
```

### Deployment a Diferentes Entornos

Para información completa sobre cómo desplegar el frontend en diferentes entornos (local, staging, producción), consulta la **[Guía de Deployment](../docs/deployment/README.md)**:

- **[Local Development](../docs/deployment/modes/local-dev.md)** - Desarrollo diario con SQLite
- **[Local Full Stack](../docs/deployment/modes/local-full.md)** - Docker con todos los servicios
- **[Production Build Testing](../docs/deployment/modes/local-prod.md)** - Probar build de producción localmente
- **[Frontend Deployment Guide](../docs/deployment/guides/frontend-deployment.md)** - Guía específica de frontend *(próximamente)*

## 🌐 Internacionalización

- **Idioma Principal**: Español (es-ES)
- **Textos**: Todos los textos user-facing en español
- **Formato de Fechas**: Formato español (`dd/MM/yyyy`)
- **Validaciones**: Mensajes de error en español

## ♿ Accesibilidad

- ARIA labels en todos los formularios
- Focus management apropiado
- Navegación por teclado
- Alto contraste en componentes críticos
- Loading states visibles
- Error messages descriptivos

## 🐛 Debugging

### Herramientas de Desarrollo

```typescript
// Debug mode en .env.local
VITE_DEBUG=true

// Logs automáticos de requests API
// Ver en consola: [API Request] POST /auth/login
```

### React DevTools

Instalar extensión de navegador:
- Chrome: React Developer Tools
- Firefox: React Developer Tools

### Redux DevTools (futuro)

Para cuando se implemente gestión de estado más compleja.

## 📚 Recursos

### Documentación

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [React Router](https://reactrouter.com)
- [React Hook Form](https://react-hook-form.com)
- [Zod](https://zod.dev)

### API Backend

- Documentación API: `http://localhost:8000/docs`
- Especificación OpenAPI: Ver `specs/005-frontend-user-profile/contracts/`

## 🤝 Contribución

### Code Style

- TypeScript strict mode habilitado
- ESLint + Prettier configurados
- Commits siguiendo Conventional Commits
- PRs requieren code review

### Convenciones

- Componentes: PascalCase (`UserMenu.tsx`)
- Hooks: camelCase con prefijo `use` (`useDebounce.ts`)
- Utilidades: camelCase (`passwordStrength.ts`)
- Tipos: PascalCase (`User`, `AuthContextType`)
- CSS Modules o styled-components para estilos aislados

## 📝 Licencia

[Especificar licencia del proyecto]

## 👥 Equipo

[Información del equipo de desarrollo]

---

**ContraVento** - Pedaleando juntos hacia nuevas aventuras 🚴‍♂️
