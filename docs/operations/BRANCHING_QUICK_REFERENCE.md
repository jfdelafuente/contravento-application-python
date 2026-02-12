# Branching & CI/CD - Quick Reference

**Para documentación completa**: [BRANCHING_STRATEGY_CICD.md](BRANCHING_STRATEGY_CICD.md)

---

## 🌳 Modelo de Ramas

```
main (production)          ← v1.3.0, v1.2.1, v1.2.0
  ↑
  │ PR + Approval Manual
  │
develop (staging)          ← Auto-deploy
  ↑
  ├── feature/019-followers-tooltip
  ├── feature/020-notifications
  ├── bugfix/fix-gpx-upload
  └── hotfix/v1.2.1-auth-bug (también a main)
```

---

## 📌 Ramas Principales

| Rama | Propósito | Deploy | Protection |
|------|-----------|--------|------------|
| **`main`** | Producción | Auto + Approval | ✅ Max |
| **`develop`** | Staging | Auto | ✅ Moderate |

---

## 🔀 Tipos de Ramas

| Tipo | Naming | Desde | Hacia | Duración |
|------|--------|-------|-------|----------|
| **Feature** | `feature/NNN-name` | develop | develop | 1-14 días |
| **Bugfix** | `bugfix/fix-issue` | develop | develop | 1-3 días |
| **Hotfix** | `hotfix/vX.Y.Z-issue` | main | main + develop | Horas |
| **Release** | `release/vX.Y.0` | develop | main + develop | 1-2 días |

---

## 🚀 Workflows Comunes

### 1. Nueva Feature

```bash
git checkout develop && git pull
git checkout -b feature/019-followers-tooltip

# ... desarrollo ...
git push origin feature/019-followers-tooltip

# Crear PR: feature → develop
# Después de merge → Auto-deploy a staging
```

### 2. Release a Producción

```bash
# PR en GitHub: develop → main
# Title: "Release v1.3.0: Features X, Y, Z"
# Approval requerido
# Después de merge → Auto-deploy a production + Tag v1.3.0
```

### 3. Hotfix Crítico

```bash
git checkout main && git pull
git checkout -b hotfix/v1.2.1-critical-bug

# ... fix ...
git push origin hotfix/v1.2.1-critical-bug

# PR: hotfix → main (urgente)
# Después de merge → Backport a develop
```

---

## 🏷️ Versionado (SemVer)

```
vMAJOR.MINOR.PATCH

v1.2.1 → v1.3.0  (new features)
v1.3.0 → v1.3.1  (bug fix)
v1.3.1 → v2.0.0  (breaking changes)
```

---

## 📝 Commit Messages

```
<type>(<scope>): <subject>

feat(dashboard): add followers tooltip
fix(gpx): resolve upload timeout
docs(api): update authentication guide
chore(deps): bump react to 18.3.0
```

**Types**: feat, fix, docs, chore, refactor, test, perf

---

## ✅ CI/CD Pipeline (Semi-Automático)

### Feature → Develop
1. PR created
2. Tests run (backend + frontend + E2E)
3. Quality checks (linters, coverage)
4. Approval + Merge
5. **Auto-build staging images** → Push to Docker Hub
6. **Manual deploy**: SSH + `./deploy.sh staging --pull-latest`

### Develop → Main
1. Release PR created
2. All tests + build
3. Approval + Merge
4. **Auto-build production images** → Push to Docker Hub
5. **Create Git tag** (v1.3.0)
6. **Generate changelog**
7. **Manual deploy**: SSH + `./deploy.sh prod --pull-version v1.3.0`

---

## 🔥 Comandos Rápidos

```bash
# Sincronizar con develop
git checkout develop && git pull origin develop

# Crear feature
git checkout -b feature/NNN-name develop

# Ver ramas locales
git branch

# Ver ramas remotas
git branch -r

# Eliminar rama local
git branch -d feature/NNN-name

# Eliminar rama remota
git push origin --delete feature/NNN-name

# Crear tag
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0

# Ver tags
git tag -l
```

---

## 🚨 Reglas de Oro

1. ❌ **NUNCA** commitear directo a `main` o `develop`
2. ✅ **SIEMPRE** crear PR (incluso para cambios pequeños)
3. ✅ **SIEMPRE** esperar CI antes de mergear
4. ✅ **SIEMPRE** eliminar rama después de merge
5. ⚠️ **NUNCA** force push a `main`
6. ⚠️ **PRECAUCIÓN** con force push a `develop`

---

## 📊 Estado Actual del Proyecto

**Última actualización**: 2026-02-12

```
main        ← v1.0.0 (por crear)
develop     ← 964 commits ahead (necesita release)
```

**Acción inmediata requerida**:
1. Crear PR: develop → main
2. Mergear y tag como v1.0.0
3. Esto establece baseline para future releases

---

## 🔗 Links Útiles

- [Estrategia Completa](BRANCHING_STRATEGY_CICD.md)
- [CI/CD Pipeline](../../.github/workflows/README.md)
- [Deployment Guide](../deployment/README.md)
- [Contributing Guide](../../CONTRIBUTING.md) *(por crear)*

---

**Para dudas**: Ver [FAQ](BRANCHING_STRATEGY_CICD.md#8-preguntas-frecuentes) en documento completo
