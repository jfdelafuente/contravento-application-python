# ContraVento - CI/CD Documentation

## CI/CD Pipeline 🚀

ContraVento utiliza **GitHub Actions** como plataforma principal de CI/CD para builds y despliegues automáticos.

### GitHub Actions (Recomendado)

✅ **Activo**: Workflow automático en push/PR

- Build automático de imágenes Docker (backend + frontend)
- Push a Docker Hub con tags semánticos
- Health checks integrados
- Cache de layers Docker para builds rápidos

**Documentación**:

- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - Guía completa de configuración
- [.github/workflows/docker-build-push.yml](.github/workflows/docker-build-push.yml) - Workflow principal

**Secrets configurados**:

- `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` - Autenticación Docker Hub
- `VITE_API_URL` / `VITE_TURNSTILE_SITE_KEY` - Variables de entorno frontend

### Jenkins (Opcional)

También disponible pipeline Jenkins para setups self-hosted:

**Documentación**:

- [JENKINS_SETUP.md](JENKINS_SETUP.md) - Guía de configuración Jenkins
- [JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md) - Setup de credentials
- [Jenkinsfile](Jenkinsfile) - Pipeline declarativo

### Migración y Comparativa

Ver [CICD_MIGRATION_GUIDE.md](CICD_MIGRATION_GUIDE.md) para:

- Comparativa Jenkins vs GitHub Actions
- Guía de migración paso a paso
- Estrategias de coexistencia
