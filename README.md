# ContraVento 🚴

Plataforma social para cicloturistas que combina diario de viajes, comunidad y mapas interactivos. Comparte tus aventuras sobre dos ruedas, descubre nuevas rutas y conecta con otros amantes del cicloturismo.

[![CI/CD](https://github.com/jfdelafuente/contravento-application-python/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/jfdelafuente/contravento-application-python/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Características Principales

### 📖 Diario de Viajes Digital

Documenta cada aventura con detalle:

- **Escribe tu historia**: Editor de texto enriquecido para narrar tu experiencia
- **Galería de fotos**: Sube múltiples imágenes de cada etapa del viaje
- **Datos del viaje**: Registra fechas, distancia, dificultad y ubicaciones
- **Organización**: Categoriza tus viajes con etiquetas personalizadas

### 🗺️ Rutas GPS Interactivas

Visualiza y comparte tus rutas:

- **Sube archivos GPX**: Importa tracks de tu GPS o smartphone
- **Visualización en mapa**: Muestra tu ruta sobre mapas especializados en ciclismo
- **Estadísticas automáticas**: Distancia total, elevación ganada/perdida, altitud máxima
- **Perfil de elevación**: Gráfico interactivo del desnivel de la ruta
- **Puntos de interés**: Marca inicio, fin y lugares destacados

### 🌍 Red Social de Ciclistas

Conecta con la comunidad:

- **Feed personalizado**: Descubre viajes recientes de la comunidad
- **Interacción**: Comparte, comenta y da "me gusta" a otros viajes
- **Seguir ciclistas**: Sigue a usuarios con gustos similares
- **Comentarios**: Intercambia consejos, dudas y experiencias
- **Inspiración continua**: Encuentra tu próxima aventura viendo lo que otros han hecho

### 👤 Perfil de Ciclista

Tu espacio personal:

- **Portfolio de viajes**: Todos tus viajes organizados en un solo lugar
- **Estadísticas globales**: Kilómetros totales, viajes completados, países visitados
- **Sobre ti**: Bio, ubicación, tipo de ciclismo favorito
- **Conexiones**: Seguidores y usuarios que sigues

---

## 🚀 Quick Start

La forma más rápida de empezar a desarrollar:

```bash
# Linux/Mac
./run-local-dev.sh --setup  # Primera vez (crea DB, usuarios, datos)
./run-local-dev.sh          # Siguientes veces

# Windows PowerShell
.\run-local-dev.ps1 -Setup  # Primera vez
.\run-local-dev.ps1         # Siguientes veces
```

**Acceso**:

- Backend API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>
- Frontend: <http://localhost:5173> (en terminal separado)

**Credenciales por defecto**:

- Admin: `admin` / `AdminPass123!`
- Usuario: `testuser` / `TestPass123!`

---

## 📚 Documentación

### Para Usuarios

- **[User Guides](docs/user-guides/README.md)** - Cómo usar ContraVento (español)
  - [Crear viajes](docs/user-guides/trips/creating-trips.md)
  - [Subir GPX](docs/user-guides/trips/uploading-gpx.md)
  - [Red social](docs/user-guides/social/following-users.md)

### Para Desarrolladores

- **[📘 Documentation Hub](docs/README.md)** - Índice completo de documentación
- **[🚀 Deployment Guide](docs/deployment/README.md)** - Todos los modos de despliegue
- **[💻 API Reference](docs/api/README.md)** - Endpoints y autenticación
- **[🏗️ Architecture](docs/architecture/README.md)** - Diseño del sistema
- **[🧪 Testing](docs/testing/README.md)** - Estrategias de testing
- **[🛠️ Development](docs/development/README.md)** - Workflows y troubleshooting

### Modos de Despliegue

| Modo | Base de Datos | Docker | Propósito |
| ---- | ------------- | ------ | --------- |
| **local-dev** | SQLite | ❌ No | Desarrollo diario (⚡ más rápido) |
| **local-minimal** | PostgreSQL | ✅ Sí | Testing con PostgreSQL |
| **local-full** | PostgreSQL | ✅ Sí | Testing completo (email, Redis) |
| **staging** | PostgreSQL | ✅ Sí | Pre-producción |
| **production** | PostgreSQL | ✅ Sí | Producción |

Ver [Deployment Guide](docs/deployment/README.md) para detalles de cada modo.

---

## 🛠️ Tech Stack

### Backend

- **Python 3.12** - Lenguaje
- **FastAPI** - Framework web async
- **SQLAlchemy 2.0** - ORM async
- **PostgreSQL** (producción) / **SQLite** (desarrollo)
- **Alembic** - Migraciones de base de datos
- **Poetry** - Gestión de dependencias

### Frontend

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Utility-first CSS
- **React Router 6** - Routing
- **React Hook Form** - Gestión de formularios
- **Leaflet.js** + **react-leaflet** - Mapas interactivos
- **Recharts** - Gráficos de elevación

### DevOps

- **Docker** + **Docker Compose** - Containerización
- **GitHub Actions** - CI/CD (primary)
- **Nginx** - Reverse proxy (producción)

---

## 🧪 Testing

```bash
# Backend tests (≥90% coverage required)
cd backend
poetry run pytest --cov=src --cov-report=html

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

Ver [Testing Guide](docs/testing/README.md) para estrategias completas.

---

## 📦 Estructura del Proyecto

```text
contravento-application-python/
├── backend/                 # API FastAPI
│   ├── src/                # Código fuente
│   │   ├── api/           # Endpoints REST
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── tests/             # Tests (unit, integration, contract)
│   └── scripts/           # Scripts de utilidad
├── frontend/               # App React
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom hooks
│   │   └── services/      # API client
│   └── tests/             # Tests (unit, E2E)
├── docs/                   # Documentación completa
│   ├── deployment/        # Guías de despliegue
│   ├── user-guides/       # Guías de usuario
│   ├── api/               # API reference
│   ├── architecture/      # Diseño del sistema
│   ├── testing/           # Testing strategies
│   └── development/       # Developer workflows
└── specs/                  # Feature specifications
```

---

## 🤝 Contributing

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'feat: add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

Ver [CONTRIBUTING.md](docs/CONTRIBUTING.md) para guías detalladas de contribución.

---

## 📝 License

Este proyecto está licenciado bajo la MIT License - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🔗 Links Útiles

- **[Documentación Completa](docs/README.md)** - Hub de navegación
- **[API Docs (Swagger)](http://localhost:8000/docs)** - API interactiva (local)
- **[Issues](https://github.com/jfdelafuente/contravento-application-python/issues)** - Reportar bugs o sugerir features
- **[GitHub Actions](https://github.com/jfdelafuente/contravento-application-python/actions)** - CI/CD status

---

**Versión**: 1.0.0
**Última actualización**: 2026-02-07
**Estado**: ✅ En desarrollo activo
