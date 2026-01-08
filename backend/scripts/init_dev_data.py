"""
Initialize development database with seed data.

This script combines:
1. Seeding achievements (seed_achievements.py)
2. Seeding cycling types (seed_cycling_types.py)
3. Creating admin user (create_admin.py)
4. Creating test users (create_verified_user.py)

Usage:
    python scripts/init_dev_data.py

Environment:
    - Only runs in development/testing environments (APP_ENV != production)
    - Safe to run multiple times (idempotent)
    - Skips if data already exists
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


async def main():
    """Initialize development database with seed data."""
    print("=" * 70)
    print("INICIALIZACION DE BASE DE DATOS - DESARROLLO")
    print("=" * 70)
    print()

    # Safety check: Don't run in production
    if settings.app_env == "production":
        print("❌ ERROR: Este script no debe ejecutarse en producción")
        print("   APP_ENV actual: production")
        sys.exit(1)

    print(f"✅ Entorno: {settings.app_env}")
    print()

    # Import here to avoid circular imports
    from scripts.seed_achievements import seed_achievements
    from scripts.seed_cycling_types import seed_cycling_types
    from scripts.create_admin import create_admin_user
    from scripts.create_verified_user import create_verified_user

    # Step 1: Seed achievements
    print("📋 Paso 1/4: Cargando achievements predefinidos")
    print("-" * 70)
    try:
        await seed_achievements()
    except Exception as e:
        print(f"\n❌ Error al cargar achievements: {e}")
        import traceback

        traceback.print_exc()
        # Continue anyway

    print()
    print()

    # Step 2: Seed cycling types
    print("🚴 Paso 2/4: Cargando tipos de ciclismo")
    print("-" * 70)
    try:
        await seed_cycling_types(force=False)
    except Exception as e:
        print(f"\n❌ Error al cargar cycling types: {e}")
        import traceback

        traceback.print_exc()
        # Continue anyway

    print()
    print()

    # Step 3: Create admin user
    print("🔐 Paso 3/4: Creando usuario administrador")
    print("-" * 70)
    try:
        admin = await create_admin_user(
            username="admin",
            email="admin@contravento.com",
            password="AdminPass123!",
            force=True,  # Skip confirmation in automated setup
        )
        if admin:
            print(f"[OK] Admin creado: {admin.username}")
    except Exception as e:
        print(f"\n❌ Error al crear admin: {e}")
        import traceback

        traceback.print_exc()
        # Continue anyway

    print()
    print()

    # Step 4: Create test users
    print("👥 Paso 4/4: Creando usuarios de prueba")
    print("-" * 70)

    # User 1: testuser
    print("\n[INFO] Creando usuario: testuser...")
    user1 = await create_verified_user(
        username="testuser", email="test@example.com", password="TestPass123!"
    )

    # User 2: maria_garcia
    print("\n[INFO] Creando usuario: maria_garcia...")
    user2 = await create_verified_user(
        username="maria_garcia", email="maria@example.com", password="SecurePass456!"
    )

    # Summary
    print()
    print("=" * 70)
    print("✨ INICIALIZACION COMPLETADA")
    print("=" * 70)

    print("\n📌 Usuarios disponibles para login:")
    print("  • admin / admin@contravento.com / AdminPass123! (ADMIN)")
    if user1:
        print("  • testuser / test@example.com / TestPass123! (USER)")
    if user2:
        print("  • maria_garcia / maria@example.com / SecurePass456! (USER)")

    print("\n📖 Ejemplo de login:")
    print("  POST /auth/login")
    print('  {"login": "admin", "password": "AdminPass123!"}')
    print("  o")
    print('  {"login": "testuser", "password": "TestPass123!"}')

    print("\n✅ Base de datos lista para desarrollo")
    print()


if __name__ == "__main__":
    asyncio.run(main())
