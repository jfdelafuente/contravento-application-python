# Pre-Push Quality Checks

Automated scripts to verify code quality before pushing to prevent CI/CD failures.

## 🚀 Quick Start

### Linux/Mac (Bash)

```bash
# Make script executable (first time only)
chmod +x pre-push-check.sh

# Run checks
./pre-push-check.sh
```

### Windows (PowerShell)

```powershell
# Run checks
.\pre-push-check.ps1
```

---

## ✅ What Gets Checked

### Backend (Python/FastAPI)
1. **Black** - Code formatting (auto-fixes if needed)
2. **Ruff** - Linting (imports, style, best practices)
3. **Mypy** - Type checking (warnings allowed)
4. **Pytest** - Unit/integration tests with ≥90% coverage

### Frontend (React/TypeScript)
1. **ESLint** - JavaScript/TypeScript linting
2. **TypeScript** - Type checking
3. **Vitest** - Unit tests

---

## 📋 Output Example

```
╔════════════════════════════════════════════════╗
║   ContraVento - Pre-Push Quality Checks       ║
╚════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐍 BACKEND CHECKS (Python/FastAPI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/4] Running Black formatter...
  ✓ Black: Code formatting is correct
[2/4] Running Ruff linter...
  ✓ Ruff: No linting errors
[3/4] Running Mypy type checker...
  ✓ Mypy: Type checking passed
[4/4] Running Pytest with coverage (≥90% required)...
  ✓ Pytest: All tests passed with ≥90% coverage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚛️  FRONTEND CHECKS (React/TypeScript)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/3] Running ESLint...
  ✓ ESLint: No linting errors
[2/3] Running TypeScript type checker...
  ✓ TypeScript: Type checking passed
[3/3] Running Vitest unit tests...
  ✓ Vitest: All unit tests passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ALL CHECKS PASSED!
   You can safely push your changes.

Next steps:
  1. git add .
  2. git commit -m "your message"
  3. git push origin <branch-name>
```

---

## 🔧 Manual Checks (Alternative)

If you prefer running checks individually:

### Backend
```bash
cd backend

# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/

# Run tests
poetry run pytest --cov=src --cov-fail-under=90
```

### Frontend
```bash
cd frontend

# Lint code
npm run lint

# Type check
npm run type-check

# Run tests
npm run test:unit
```

---

## ⚙️ Configuration

### Backend Configuration
- **Black**: `backend/pyproject.toml` → `[tool.black]`
- **Ruff**: `backend/pyproject.toml` → `[tool.ruff]`
- **Mypy**: `backend/pyproject.toml` → `[tool.mypy]`
- **Pytest**: `backend/pyproject.toml` → `[tool.pytest.ini_options]`

### Frontend Configuration
- **ESLint**: `frontend/.eslintrc.cjs`
- **TypeScript**: `frontend/tsconfig.json`
- **Vitest**: `frontend/vite.config.ts`

---

## 🚨 Common Issues

### Issue: "Permission denied" on Linux/Mac
```bash
chmod +x pre-push-check.sh
```

### Issue: "Script cannot be loaded" on Windows
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
PowerShell -ExecutionPolicy Bypass -File .\pre-push-check.ps1
```

### Issue: Black formatting fails
**Solution**: Run Black auto-format:
```bash
cd backend
poetry run black src/ tests/
```

### Issue: Coverage < 90%
**Solution**: Add more tests or check `htmlcov/index.html` for uncovered lines:
```bash
cd backend
poetry run pytest --cov=src --cov-report=html
# Open backend/htmlcov/index.html in browser
```

### Issue: ESLint errors
**Solution**: Some errors can be auto-fixed:
```bash
cd frontend
npm run lint -- --fix
```

---

## 🎯 Integration with Git Hooks (Optional)

To automatically run checks before every push:

### Using Husky (Recommended)
```bash
# Install husky
npm install --save-dev husky

# Enable Git hooks
npx husky install

# Add pre-push hook
npx husky add .husky/pre-push "./pre-push-check.sh"
```

### Manual Git Hook
```bash
# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
./pre-push-check.sh
EOF

# Make executable
chmod +x .git/hooks/pre-push
```

---

## 📊 CI/CD Workflows

These local checks mirror the GitHub Actions workflows:

- `.github/workflows/ci.yml` - Main CI/CD pipeline
- `.github/workflows/backend-tests.yml` - Backend-specific tests
- `.github/workflows/frontend-tests.yml` - Frontend-specific tests

Running the pre-push script ensures your code will pass all CI/CD checks.

---

## 💡 Tips

1. **Run checks frequently**: Don't wait until push time
2. **Fix issues incrementally**: Easier than fixing many at once
3. **Enable auto-save formatting**: Configure your IDE to run Black/ESLint on save
4. **Review coverage reports**: Aim for meaningful tests, not just coverage %
5. **Commit formatted code**: Always run Black before committing

---

## 🆘 Need Help?

- **Backend issues**: Check `backend/pyproject.toml` configuration
- **Frontend issues**: Check `frontend/.eslintrc.cjs` and `tsconfig.json`
- **CI/CD issues**: Review GitHub Actions logs at `https://github.com/jfdelafuente/contravento-application-python/actions`

---

**Last updated**: 2026-01-20
