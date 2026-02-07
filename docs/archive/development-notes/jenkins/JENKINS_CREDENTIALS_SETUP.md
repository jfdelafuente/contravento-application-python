# Jenkins Credentials - Guía Visual de Configuración

Esta guía proporciona instrucciones paso a paso con descripciones visuales para configurar las credentials necesarias en Jenkins.

## 📋 Resumen de Credentials Necesarios

| ID Credential | Tipo | Valor Ejemplo | Uso |
|---------------|------|---------------|-----|
| `dockerhub_id` | Username with password | username: jfdelafuente<br>password: [token] | Autenticación Docker Hub |
| `vite_api_url` | Secret text | https://api.contravento.com | URL del backend para frontend |
| `vite_turnstile_site_key` | Secret text | 1x00000000000000000000AA | Cloudflare Turnstile CAPTCHA |

## 🔐 Paso 1: Acceder a Credentials Manager

### Navegación en Jenkins UI

1. **Jenkins Dashboard** (página principal)
2. Click en **"Manage Jenkins"** (menú lateral izquierdo)
3. Click en **"Manage Credentials"** (sección Security)
4. Click en **"(global)"** domain
5. Click en **"Add Credentials"** (botón a la izquierda)

### Descripción Visual

```
Jenkins Dashboard
└── Manage Jenkins
    └── Security Section
        └── Manage Credentials
            └── Stores scoped to Jenkins
                └── System
                    └── Global credentials (unrestricted)
                        └── [+ Add Credentials]
```

## 🐳 Paso 2: Configurar Docker Hub Credentials

### Formulario de Configuración

**Campos a completar:**

| Campo | Valor |
|-------|-------|
| **Kind** | `Username with password` (seleccionar del dropdown) |
| **Scope** | `Global (Jenkins, nodes, items, all child items, etc)` |
| **Username** | `jfdelafuente` |
| **Password** | `[Tu Docker Hub Access Token]` |
| **ID** | `dockerhub_id` ⚠️ **EXACTO - no cambiar** |
| **Description** | `Docker Hub credentials for pushing images` |

### ⚠️ IMPORTANTE: Usar Access Token, NO tu contraseña

**Por qué Access Token:**
- ✅ Más seguro (puede ser revocado sin cambiar contraseña)
- ✅ Permisos granulares (solo Read/Write/Delete)
- ✅ Rastreable (puedes ver cuándo fue usado)
- ✅ Requerido por Docker Hub (passwords deprecated para CLI)

### Obtener Docker Hub Access Token

**Paso a paso en Docker Hub:**

1. Login en https://hub.docker.com
2. Click en tu avatar (esquina superior derecha)
3. Click **"Account Settings"**
4. Click **"Security"** (menú lateral)
5. Scroll hasta **"Access Tokens"**
6. Click **"New Access Token"**

**Formulario de creación del token:**

| Campo | Valor |
|-------|-------|
| **Access Token Description** | `jenkins-pipeline-contravento` |
| **Access permissions** | ✅ Read<br>✅ Write<br>✅ Delete |

7. Click **"Generate"**
8. **⚠️ COPIAR EL TOKEN INMEDIATAMENTE** (solo se muestra una vez)
9. Pegar el token en el campo "Password" de Jenkins

**Ejemplo de token** (no usar, es de ejemplo):
```
dckr_pat_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

### Verificación Post-Creación

Después de guardar, deberías ver:

```
Global credentials (unrestricted)
├── dockerhub_id (jfdelafuente/****** - Docker Hub credentials for pushing images)
```

## 🌐 Paso 3: Configurar Frontend API URL

### Formulario de Configuración

**Campos a completar:**

| Campo | Valor |
|-------|-------|
| **Kind** | `Secret text` (seleccionar del dropdown) |
| **Scope** | `Global (Jenkins, nodes, items, all child items, etc)` |
| **Secret** | `https://api.contravento.com` |
| **ID** | `vite_api_url` ⚠️ **EXACTO - no cambiar** |
| **Description** | `Frontend API URL for production builds` |

### Valores por Entorno

Dependiendo del entorno de deployment, usar estos valores:

| Entorno | URL | Cuándo Usar |
|---------|-----|-------------|
| **Local Development** | `http://localhost:8000` | Solo para desarrollo local |
| **Staging** | `https://api-staging.contravento.com` | Testing pre-producción |
| **Production** | `https://api.contravento.com` | Deployment a producción |

**Recomendación**: Crear un credential por entorno usando Jenkins Folders (ver más abajo).

### ⚠️ Nota sobre CORS

Si el frontend y backend están en dominios diferentes, asegúrate de:

1. Configurar CORS en el backend (`backend/src/config.py`):
   ```python
   CORS_ORIGINS = "https://contravento.com,https://www.contravento.com"
   ```

2. Usar HTTPS (no HTTP) en producción

## 🔒 Paso 4: Configurar Cloudflare Turnstile Key

### Formulario de Configuración

**Campos a completar:**

| Campo | Valor |
|-------|-------|
| **Kind** | `Secret text` (seleccionar del dropdown) |
| **Scope** | `Global (Jenkins, nodes, items, all child items, etc)` |
| **Secret** | `[Tu Cloudflare Turnstile Site Key]` |
| **ID** | `vite_turnstile_site_key` ⚠️ **EXACTO - no cambiar** |
| **Description** | `Cloudflare Turnstile site key for CAPTCHA` |

### Obtener Cloudflare Turnstile Site Key

**Paso a paso en Cloudflare:**

1. Login en https://dash.cloudflare.com
2. En el menú lateral, click **"Turnstile"**
3. Si no tienes un widget, click **"Add widget"**
4. Configurar el widget:

| Campo | Valor |
|-------|-------|
| **Widget name** | `ContraVento Production` |
| **Domain** | `contravento.com` |
| **Widget mode** | `Managed` (recomendado) |

5. Click **"Create"**
6. Copiar el **"Site Key"** (empieza con `0x4...`)
7. Pegar el Site Key en el campo "Secret" de Jenkins

### Testing Keys vs Production Keys

**Para Testing/Staging** (siempre pasan):
```
Site Key: 1x00000000000000000000AA
Secret Key: 1x0000000000000000000000000000000AA
```

**Para Production**:
- Usar el Site Key real de Cloudflare
- ⚠️ NO usar testing keys en producción (bypass de seguridad)

### Verificación del Site Key

Puedes verificar que el Site Key funciona con este HTML de prueba:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
</head>
<body>
    <div class="cf-turnstile" data-sitekey="TU_SITE_KEY_AQUI"></div>
</body>
</html>
```

Si el widget aparece → Site Key es válido ✅

## ✅ Paso 5: Verificar Credentials Configurados

### Opción A: Verificación Visual (UI)

1. Ir a **Manage Jenkins** → **Manage Credentials** → **Global**
2. Deberías ver exactamente 3 credentials:

```
Global credentials (unrestricted)
├── dockerhub_id (jfdelafuente/****** - Docker Hub credentials...)
├── vite_api_url (****** - Frontend API URL...)
└── vite_turnstile_site_key (****** - Cloudflare Turnstile site key...)
```

### Opción B: Verificación via Script Console

1. Ir a **Manage Jenkins** → **Script Console**
2. Pegar este script Groovy:

```groovy
import com.cloudbees.plugins.credentials.CredentialsProvider
import jenkins.model.Jenkins

def creds = CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardCredentials.class,
    Jenkins.instance,
    null,
    null
)

println "=== Credentials Configurados ==="
println "Total: ${creds.size()}"
println ""

def requiredIds = ['dockerhub_id', 'vite_api_url', 'vite_turnstile_site_key']

requiredIds.each { id ->
    def found = creds.find { it.id == id }
    if (found) {
        println "✅ ${id} - OK"
        println "   Description: ${found.description ?: 'N/A'}"
    } else {
        println "❌ ${id} - FALTA"
    }
    println ""
}

println "=== Todos los Credentials ==="
creds.each { c ->
    println "ID: ${c.id}"
    println "   Type: ${c.class.simpleName}"
    println "   Description: ${c.description ?: 'N/A'}"
    println ""
}
```

3. Click **"Run"**

**Output esperado:**

```
=== Credentials Configurados ===
Total: 3

✅ dockerhub_id - OK
   Description: Docker Hub credentials for pushing images

✅ vite_api_url - OK
   Description: Frontend API URL for production builds

✅ vite_turnstile_site_key - OK
   Description: Cloudflare Turnstile site key for CAPTCHA

=== Todos los Credentials ===
ID: dockerhub_id
   Type: UsernamePasswordCredentialsImpl
   Description: Docker Hub credentials for pushing images

ID: vite_api_url
   Type: StringCredentialsImpl
   Description: Frontend API URL for production builds

ID: vite_turnstile_site_key
   Type: StringCredentialsImpl
   Description: Cloudflare Turnstile site key for CAPTCHA
```

### Opción C: Test Dry-Run del Pipeline

1. Crear un Pipeline de prueba
2. Usar este Jenkinsfile simplificado:

```groovy
pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub_id')
        VITE_API_URL = credentials('vite_api_url')
        VITE_TURNSTILE_SITE_KEY = credentials('vite_turnstile_site_key')
    }

    stages {
        stage('Verify Credentials') {
            steps {
                sh '''
                    echo "=== Credentials Test ==="
                    echo "Docker Hub User: $DOCKERHUB_CREDENTIALS_USR"
                    echo "Docker Hub Pass: ******** (hidden)"
                    echo "API URL: $VITE_API_URL"
                    echo "Turnstile Key: ${VITE_TURNSTILE_SITE_KEY:0:10}... (partial)"
                    echo "=== All credentials loaded successfully ==="
                '''
            }
        }
    }
}
```

3. Ejecutar **"Build Now"**
4. Verificar logs - deberías ver las variables (sin valores sensibles expuestos)

## 🏢 Paso 6: Credentials por Entorno (Avanzado)

### Crear Estructura de Folders

Para gestionar diferentes entornos (staging, production) con diferentes valores:

1. **Dashboard** → **New Item**
2. **Item name**: `staging`
3. **Type**: `Folder`
4. Click **OK**
5. Repetir para `production`

### Configurar Credentials en cada Folder

**En folder `staging`:**

1. Entrar al folder **staging**
2. Click **"Credentials"** (menú lateral)
3. Click **"(global)"**
4. Click **"Add Credentials"**
5. Crear las 3 credentials con valores de staging:

| ID | Valor Staging |
|----|---------------|
| `vite_api_url` | `https://api-staging.contravento.com` |
| `vite_turnstile_site_key` | `1x00000000000000000000AA` (testing key) |
| `dockerhub_id` | (mismo que global) |

**En folder `production`:**

Repetir el proceso con valores de producción:

| ID | Valor Production |
|----|---------------|
| `vite_api_url` | `https://api.contravento.com` |
| `vite_turnstile_site_key` | `[Real Cloudflare Site Key]` |
| `dockerhub_id` | (mismo que global) |

### Crear Pipelines en cada Folder

**Estructura final:**

```
Jenkins
├── staging/
│   ├── Credentials (staging values)
│   └── Pipeline Job "contravento-pipeline"
└── production/
    ├── Credentials (production values)
    └── Pipeline Job "contravento-pipeline"
```

**Ventaja**: Mismo Jenkinsfile, diferentes valores por entorno automáticamente.

## 🔧 Troubleshooting

### Error: "No such property: credentials for class: groovy.lang.Binding"

**Causa**: Jenkins Credentials Plugin no instalado

**Solución**:
1. **Manage Jenkins** → **Manage Plugins**
2. Tab **"Available"**
3. Buscar: `Credentials Plugin`
4. Instalar y reiniciar Jenkins

### Error: "Credentials 'dockerhub_id' not found"

**Causa**: ID del credential incorrecto o no existe

**Solución**:
1. Verificar que el ID es exactamente `dockerhub_id` (case-sensitive)
2. Verificar que está en scope "Global"
3. Ejecutar script de verificación (Opción B arriba)

### Error: "VITE_API_URL is null"

**Causa**: Credential es tipo incorrecto o no está en scope correcto

**Solución**:
1. Verificar que `vite_api_url` es tipo **"Secret text"** (no Username/Password)
2. Verificar que Scope = Global
3. Re-crear el credential si es necesario

### Warning: "Credentials shown in logs"

**Causa**: Logging inadecuado en pipeline

**Solución**:
- ❌ NO hacer: `echo "API URL: $VITE_API_URL"`
- ✅ HACER: `echo "API URL: ${VITE_API_URL:0:10}..."` (solo primeros caracteres)
- ✅ MEJOR: No loggear credentials en absoluto

Jenkins automáticamente enmascara credentials, pero mejor prevenir.

## 📚 Recursos Adicionales

### Documentación Oficial

- [Jenkins Credentials Plugin](https://plugins.jenkins.io/credentials/)
- [Using Credentials in Pipeline](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#handling-credentials)
- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/)

### Best Practices

1. ✅ **Rotar tokens regularmente** (cada 90 días)
2. ✅ **Usar Access Tokens en lugar de passwords**
3. ✅ **Un credential por entorno** (via Folders)
4. ✅ **Descripción clara** en cada credential
5. ✅ **Mínimos permisos necesarios** (principo de least privilege)
6. ❌ **NO compartir credentials** entre proyectos no relacionados
7. ❌ **NO hardcodear secrets** en Jenkinsfile
8. ❌ **NO usar testing keys** en producción

### Security Checklist

Antes de ir a producción, verificar:

- [ ] Docker Hub Access Token tiene permisos mínimos (Read/Write, no Admin)
- [ ] Turnstile Site Key es de producción (no testing key)
- [ ] API URL usa HTTPS (no HTTP)
- [ ] Credentials están en scope adecuado (Global o Folder)
- [ ] No hay secrets hardcodeados en código
- [ ] Logs del pipeline no exponen valores sensibles
- [ ] Access tokens tienen fecha de rotación planificada

---

**Última actualización**: 2026-01-22
**Autor**: Claude + @jfdelafuente
**Estado**: ✅ Documentación completa y verificada
