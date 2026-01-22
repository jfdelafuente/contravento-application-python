# Jenkins CI/CD Environment - Quick Start Guide

## 📋 Descripción

Entorno Docker standalone optimizado para pipelines de CI/CD (Jenkins, GitHub Actions, GitLab CI).

**Incluye**:
- PostgreSQL (database)
- Backend API (FastAPI)
- Frontend (React/Vite dev server)
- pgAdmin (database UI)

**Características**:
- ✅ Un solo archivo (no requiere overlays)
- ✅ Auto-configuración (SECRET_KEY auto-generado)
- ✅ Rápido spin-up/teardown
- ✅ Scripts helpers cross-platform

---

## 🚀 Inicio Rápido

### Linux/Mac

```bash
# Iniciar entorno
./run-jenkins-env.sh start

# Ver logs
./run-jenkins-env.sh logs

# Ejecutar tests
./run-jenkins-env.sh test

# Detener
./run-jenkins-env.sh stop
```

### Windows PowerShell

```powershell
# Iniciar entorno
.\run-jenkins-env.ps1 start

# Ver logs
.\run-jenkins-env.ps1 logs

# Ejecutar tests
.\run-jenkins-env.ps1 test

# Detener
.\run-jenkins-env.ps1 stop
```

---

## 🌐 URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:5173 | - |
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **pgAdmin** | http://localhost:5050 | admin@jenkins.local / jenkins |

---

## 🗄️ Conexión a Base de Datos

```
Host:      localhost
Port:      5432
Database:  contravento_ci
User:      postgres
Password:  jenkins_test_password
```

**Herramientas recomendadas**: DBeaver, TablePlus, pgAdmin, psql

---

## 📝 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `start` | Inicia todos los servicios |
| `stop` | Detiene todos los servicios |
| `restart` | Reinicia todos los servicios |
| `logs` | Muestra logs en tiempo real |
| `status` | Verifica estado y health checks |
| `test` | Ejecuta tests de backend + frontend |
| `clean` | Detiene y elimina volúmenes |
| `help` | Muestra ayuda |

---

## 🔧 Uso Manual (sin scripts)

```bash
# Iniciar
docker-compose -f docker-compose-jenkins.yml up -d

# Ver logs
docker-compose -f docker-compose-jenkins.yml logs -f

# Ejecutar tests backend
docker-compose -f docker-compose-jenkins.yml exec backend pytest

# Ejecutar tests frontend
docker-compose -f docker-compose-jenkins.yml exec frontend npm test

# Detener
docker-compose -f docker-compose-jenkins.yml down

# Limpiar volúmenes
docker-compose -f docker-compose-jenkins.yml down -v
```

---

## 🔄 Integración con Jenkins

### Ejemplo de Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Setup Environment') {
            steps {
                sh 'docker-compose -f docker-compose-jenkins.yml up -d'
                sh 'sleep 30'  // Esperar a que servicios estén healthy
            }
        }

        stage('Backend Tests') {
            steps {
                sh 'docker-compose -f docker-compose-jenkins.yml exec -T backend pytest --cov=src --cov-report=term'
            }
        }

        stage('Frontend Tests') {
            steps {
                sh 'docker-compose -f docker-compose-jenkins.yml exec -T frontend npm test'
            }
        }

        stage('E2E Tests') {
            steps {
                sh 'docker-compose -f docker-compose-jenkins.yml exec -T frontend npm run test:e2e'
            }
        }
    }

    post {
        always {
            sh 'docker-compose -f docker-compose-jenkins.yml down -v'
        }
    }
}
```

---

## 🔄 Integración con GitHub Actions

### Ejemplo de workflow

```yaml
name: CI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Start CI environment
        run: docker-compose -f docker-compose-jenkins.yml up -d

      - name: Wait for services
        run: sleep 30

      - name: Run backend tests
        run: docker-compose -f docker-compose-jenkins.yml exec -T backend pytest --cov=src

      - name: Run frontend tests
        run: docker-compose -f docker-compose-jenkins.yml exec -T frontend npm test

      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose-jenkins.yml down -v
```

---

## ⚙️ Variables de Entorno (Opcionales)

Puedes personalizar el entorno creando un archivo `.env`:

```bash
# .env
SECRET_KEY=my_custom_secret_key_for_testing
POSTGRES_PASSWORD=my_custom_password
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA
```

**Valores por defecto** (si no se especifican):
- `SECRET_KEY`: `jenkins_default_secret_key_for_testing_only_do_not_use_in_production`
- `POSTGRES_PASSWORD`: `jenkins_test_password`
- `VITE_TURNSTILE_SITE_KEY`: `1x00000000000000000000AA` (test key que auto-pasa)

---

## 🧹 Limpieza Completa

```bash
# Linux/Mac
./run-jenkins-env.sh clean

# Windows PowerShell
.\run-jenkins-env.ps1 clean

# Manual
docker-compose -f docker-compose-jenkins.yml down -v
docker volume prune -f
```

---

## 🐛 Troubleshooting

### Error: "Port 5432 already in use"

```bash
# Detener PostgreSQL local
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # Mac

# O cambiar puerto en docker-compose-jenkins.yml:
ports:
  - "5433:5432"  # Usar 5433 en host
```

### Error: "Backend unhealthy"

```bash
# Ver logs del backend
docker-compose -f docker-compose-jenkins.yml logs backend

# Verificar base de datos
docker-compose -f docker-compose-jenkins.yml exec postgres psql -U postgres -d contravento_ci -c "\dt"
```

### Error: "Frontend build fails"

```bash
# Rebuild frontend
docker-compose -f docker-compose-jenkins.yml build --no-cache frontend

# Ver logs
docker-compose -f docker-compose-jenkins.yml logs frontend
```

---

## 📊 Health Checks

Todos los servicios tienen health checks configurados:

```bash
# Verificar estado
./run-jenkins-env.sh status

# O manualmente
curl http://localhost:8000/health          # Backend
curl http://localhost:5173                 # Frontend
docker-compose -f docker-compose-jenkins.yml exec postgres pg_isready
```

---

## 🔍 Debugging con pgAdmin

1. Abrir http://localhost:5050
2. Login: `admin@jenkins.local` / `jenkins`
3. Server "ContraVento CI Database" ya está configurado
4. Click en el server para conectar

**Queries útiles**:

```sql
-- Ver todas las tablas
\dt

-- Ver viajes
SELECT * FROM trips LIMIT 10;

-- Ver usuarios
SELECT username, email, is_verified FROM users;

-- Ver archivos GPX
SELECT gpx_file_id, trip_id, file_name FROM gpx_files;
```

---

## 📚 Comparación con Otros Entornos

| Característica | Jenkins CI | Local Minimal | Local Full |
|----------------|------------|---------------|------------|
| **PostgreSQL** | ✅ | ✅ | ✅ |
| **Backend** | ✅ | ✅ | ✅ |
| **Frontend** | ✅ | Opcional | Opcional |
| **pgAdmin** | ✅ | ❌ | ✅ |
| **Redis** | ❌ | ❌ | ✅ |
| **MailHog** | ❌ | ❌ | ✅ |
| **Auto-config** | ✅ | ❌ | ❌ |
| **Uso** | CI/CD | Dev diario | Testing completo |

---

## 📖 Documentación Relacionada

- [CLAUDE.md](CLAUDE.md) - Guía principal del proyecto
- [QUICK_START.md](QUICK_START.md) - Deployment rápido
- [docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md) - Guía completa de CI/CD
- [docker-compose.local-minimal.yml](docker-compose.local-minimal.yml) - Entorno minimal

---

## 🤝 Contribución

Si encuentras problemas o tienes sugerencias para mejorar este entorno:

1. Reporta issues en GitHub
2. Propón mejoras al pipeline
3. Documenta casos de uso adicionales

---

**Última actualización**: 2026-01-22
