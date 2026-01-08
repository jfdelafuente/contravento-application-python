# Configuración de MailHog para Testing de Emails

MailHog es un servidor SMTP de prueba que captura todos los emails enviados por la aplicación y los muestra en una interfaz web. Esto permite probar funcionalidades de email sin enviar emails reales.

## ¿Cuándo usar MailHog?

MailHog es útil cuando desarrollas o pruebas estas funcionalidades:

- ✅ Registro de usuarios (email de verificación)
- ✅ Restablecimiento de contraseña (email con token)
- ✅ Notificaciones por email
- ✅ Cualquier funcionalidad que envíe emails

## Incluido en Docker Full

MailHog está **solo disponible en Docker Full**, no en Docker Minimal.

```bash
# Iniciar Docker Full (incluye MailHog)
./deploy.sh local         # Linux/Mac
.\deploy.ps1 local        # Windows
```

## Configuración Automática

Cuando usas Docker Full, MailHog se configura automáticamente:

### 1. Servicio MailHog (docker-compose.local.yml)

```yaml
mailhog:
  image: mailhog/mailhog:latest
  container_name: contravento-mailhog
  ports:
    - "1025:1025"  # SMTP server (puerto interno)
    - "8025:8025"  # Web UI (interfaz web)
  restart: unless-stopped
  networks:
    - contravento-network
```

### 2. Variables de Entorno (.env.local)

El backend se conecta a MailHog automáticamente con esta configuración:

```bash
# EMAIL - MailHog (Local)
SMTP_HOST=mailhog          # Nombre del servicio en Docker
SMTP_PORT=1025             # Puerto SMTP de MailHog
SMTP_USER=                 # MailHog no requiere autenticación
SMTP_PASSWORD=             # MailHog no requiere autenticación
SMTP_FROM=dev@contravento.local
SMTP_TLS=false             # MailHog no usa TLS
```

**Importante**: `SMTP_HOST=mailhog` usa el nombre del servicio Docker, no `localhost`.

## Acceso a la Interfaz Web

Una vez que Docker Full esté corriendo:

1. **Abre tu navegador**: <http://localhost:8025>

2. **Interfaz MailHog**: Verás:
   - Lista de emails recibidos (inicialmente vacía)
   - Detalles de cada email (remitente, destinatario, asunto, cuerpo)
   - Opciones para ver HTML, texto plano, headers

## Probar el Envío de Emails

### Opción 1: Registro de Usuario (API)

Usa la API de registro para enviar un email de verificación:

```bash
# Registrar un nuevo usuario
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Resultado**:
1. El backend enviará un email de verificación a MailHog
2. Ve a <http://localhost:8025> para ver el email capturado
3. Verás el token de verificación en el email

### Opción 2: Restablecimiento de Contraseña

```bash
# Solicitar restablecimiento de contraseña
curl -X POST http://localhost:8000/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

**Resultado**:
1. Email de reset enviado a MailHog
2. Revisa el token en <http://localhost:8025>

### Opción 3: Script de Prueba

Puedes crear un script simple para probar el envío:

```python
# backend/scripts/test_email.py
import asyncio
from src.utils.email import send_email

async def main():
    await send_email(
        to_email="test@example.com",
        subject="Test Email from ContraVento",
        body="<h1>Hello!</h1><p>This is a test email.</p>"
    )
    print("✅ Email sent to MailHog! Check http://localhost:8025")

if __name__ == "__main__":
    asyncio.run(main())
```

Ejecutar:

```bash
cd backend
poetry run python scripts/test_email.py
```

## Verificar que MailHog Está Funcionando

### 1. Comprobar que el contenedor está corriendo

```bash
docker ps | grep mailhog
```

**Salida esperada**:
```
contravento-mailhog   mailhog/mailhog:latest   Up 5 minutes   0.0.0.0:1025->1025/tcp, 0.0.0.0:8025->8025/tcp
```

### 2. Ver logs de MailHog

```bash
docker logs contravento-mailhog
```

**Salida esperada**:
```
2024/01/07 10:30:00 Using in-memory storage
2024/01/07 10:30:00 [SMTP] Binding to address: 0.0.0.0:1025
2024/01/07 10:30:00 [HTTP] Binding to address: 0.0.0.0:8025
```

### 3. Probar conectividad SMTP

```bash
# Desde dentro del contenedor backend
docker exec -it contravento-api-development nc -zv mailhog 1025

# Salida esperada: "mailhog (172.x.x.x:1025) open"
```

**Nota**: `nc` (netcat) está preinstalado en los contenedores para facilitar debugging de red.

## Troubleshooting

### Problema: No veo emails en MailHog

**Causa 1**: MailHog no está corriendo

```bash
# Verificar
docker ps | grep mailhog

# Si no aparece, iniciar Docker Full
./deploy.sh local
```

**Causa 2**: Backend usa configuración incorrecta

```bash
# Verificar variables de entorno del backend
docker exec contravento-api-development env | grep SMTP

# Debe mostrar:
# SMTP_HOST=mailhog
# SMTP_PORT=1025
```

**Solución**: Edita `.env.local` y asegúrate de que:
```bash
SMTP_HOST=mailhog  # NO localhost, NO 127.0.0.1
SMTP_PORT=1025
```

Luego reinicia:
```bash
./deploy.sh local down
./deploy.sh local
```

**Causa 3**: Emails se están enviando a consola (modo minimal)

Si usas Docker Minimal, los emails se logean en consola en lugar de enviarse a MailHog.

```bash
# Ver logs del backend
docker logs contravento-api-development | grep -i email
```

### Problema: Error "Connection refused" al enviar email

**Síntomas**:
```
[ERROR] Failed to send email: [Errno 111] Connection refused
```

**Solución 1**: Verifica que MailHog esté en la misma red Docker

```bash
# Ver redes del backend
docker inspect contravento-api-development | grep -A 5 Networks

# Debe estar en: contravento-network
```

**Solución 2**: Verifica que SMTP_HOST sea correcto

```bash
# Dentro del contenedor backend, probar conexión DNS
docker exec -it contravento-api-development ping -c 1 mailhog

# Debe responder con IP del contenedor MailHog

# Probar conectividad al puerto SMTP
docker exec -it contravento-api-development nc -zv mailhog 1025

# Debe mostrar: "mailhog (172.x.x.x:1025) open"
```

### Problema: Puerto 8025 ya en uso

```bash
# Ver qué proceso usa el puerto
lsof -i :8025        # Linux/Mac
netstat -ano | findstr :8025  # Windows

# Cambiar el puerto en docker-compose.local.yml
mailhog:
  ports:
    - "8026:8025"  # Usar puerto 8026 en host
```

Luego accede a: <http://localhost:8026>

## Diferencias entre Entornos

| Característica | SQLite Local | Docker Minimal | Docker Full |
|----------------|:------------:|:--------------:|:-----------:|
| **MailHog** | ❌ No | ❌ No | ✅ Sí |
| **Emails** | Console logs | Console logs | MailHog UI |
| **SMTP_HOST** | - | - | `mailhog` |
| **Web UI** | - | - | <http://localhost:8025> |

## Alternativas a MailHog

Si no quieres usar MailHog, tienes estas opciones:

### 1. Mailtrap (recomendado para staging)

Servicio en la nube para testing de emails:

```bash
# .env.staging
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
SMTP_TLS=true
```

**Ventajas**:
- Interfaz web más avanzada
- Análisis de deliverability
- Testing de spam

**Sitio**: <https://mailtrap.io>

### 2. Console Logging (para desarrollo rápido)

Si no necesitas ver los emails formateados:

```bash
# .env.local-minimal
SMTP_HOST=    # Vacío desactiva SMTP
```

Los emails se logean en consola del backend:

```bash
docker logs -f contravento-api-development
```

### 3. SMTP Real (solo staging/producción)

```bash
# .env.prod - SendGrid
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_TLS=true
```

## Referencias

- **MailHog GitHub**: <https://github.com/mailhog/MailHog>
- **Docker Compose Config**: [docker-compose.local.yml](../../docker-compose.local.yml)
- **Deployment Guide**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Quick Start**: [../../QUICK_START.md](../../QUICK_START.md)

---

**Última actualización**: 2026-01-08
