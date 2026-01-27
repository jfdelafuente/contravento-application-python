"""
Script to create the first admin user for ContraVento.

This script creates a verified admin user with default or custom credentials.
Designed for initial setup when no admin exists yet.

Usage:
    # Create default admin
    poetry run python scripts/create_admin.py

    # Create custom admin
    poetry run python scripts/create_admin.py --username myadmin --email admin@mycompany.com --password "MySecurePass123!"

Default credentials (if no arguments provided):
    Username: admin
    Email: admin@contravento.com
    Password: AdminPass123!
    Role: ADMIN (verified)

This script:
1. Checks if an admin already exists (warns if yes)
2. Creates admin user with verified email
3. Sets role to ADMIN automatically
4. Displays credentials for first login
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.models.user import User, UserProfile, UserRole
from src.schemas.auth import RegisterRequest
from src.services.auth_service import AuthService

# Import all models to ensure SQLAlchemy relationships are resolved
# This prevents "failed to locate a name" errors when using User model
from src.models.comment import Comment  # noqa: F401
from src.models.like import Like  # noqa: F401
from src.models.notification import Notification, NotificationArchive  # noqa: F401
from src.models.share import Share  # noqa: F401
from src.models.social import Follow  # noqa: F401
from src.models.trip import Trip, TripPhoto, TripLocation, Tag, TripTag  # noqa: F401
from src.models.stats import UserStats, Achievement, UserAchievement  # noqa: F401


async def check_existing_admin(db) -> bool:
    """
    Check if any admin user already exists.

    Args:
        db: Database session

    Returns:
        True if admin exists, False otherwise
    """
    result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
    admin_users = result.scalars().all()

    if admin_users:
        print("\nADVERTENCIA: Ya existen usuarios administradores:")
        for admin in admin_users:
            print(f"  - {admin.username} ({admin.email})")
        print()
        return True

    return False


async def create_admin_user(username: str, email: str, password: str, force: bool = False):
    """
    Create an admin user with verified email.

    Args:
        username: Admin username
        email: Admin email
        password: Admin password
        force: If True, create even if admins already exist

    Returns:
        User object if successful, None otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin already exists (unless --force)
            if not force:
                admin_exists = await check_existing_admin(db)
                if admin_exists:
                    response = input("Crear un administrador adicional? (s/N): ")
                    if response.lower() not in ["s", "si", "y", "yes"]:
                        print("\n[INFO] Operacion cancelada")
                        return None

            # Check if this specific user already exists
            result = await db.execute(
                select(User).where(
                    (User.username == username.lower()) | (User.email == email.lower())
                )
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"\nERROR: Usuario ya existe:")
                print(f"  Username: {existing_user.username}")
                print(f"  Email: {existing_user.email}")
                print(f"  Rol: {existing_user.role.value}")

                # Offer to promote if not admin
                if existing_user.role != UserRole.ADMIN:
                    response = input("\nPromover este usuario a administrador? (s/N): ")
                    if response.lower() in ["s", "si", "y", "yes"]:
                        existing_user.role = UserRole.ADMIN
                        existing_user.is_verified = True
                        await db.commit()
                        await db.refresh(existing_user)

                        print("\n" + "=" * 60)
                        print("USUARIO PROMOVIDO A ADMINISTRADOR")
                        print("=" * 60)
                        print(f"Username: {existing_user.username}")
                        print(f"Email: {existing_user.email}")
                        print(f"Rol: {existing_user.role.value}")
                        print("=" * 60)

                        return existing_user

                return None

            # Create new admin user
            print(f"\n[INFO] Creando usuario administrador '{username}'...")
            auth_service = AuthService(db)

            register_data = RegisterRequest(username=username, email=email, password=password)

            # Register user
            user_response = await auth_service.register(register_data)
            print(f"[OK] Usuario registrado: {user_response.username}")

            # Fetch the actual user object
            result = await db.execute(select(User).where(User.id == user_response.user_id))
            user = result.scalar_one()

            # Verify and promote to admin
            user.is_verified = True
            user.role = UserRole.ADMIN
            await db.commit()
            await db.refresh(user)

            print("[OK] Email verificado automaticamente")
            print("[OK] Rol asignado: ADMIN")

            # Display admin info
            print("\n" + "=" * 60)
            print("ADMINISTRADOR CREADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password: {password}")
            print(f"User ID: {user.id}")
            print(f"Rol: {user.role.value}")
            print("Verificado: Si")
            print(f"Activo: {'Si' if user.is_active else 'No'}")
            print("=" * 60)
            print("\nIMPORTANTE: Guarda estas credenciales en un lugar seguro.")
            print("   El password no se puede recuperar desde la base de datos.")
            print()

            return user

        except ValueError as e:
            print(f"\nERROR: Error de validacion: {e}")
            print("\nRequisitos del password:")
            print("  - Minimo 8 caracteres")
            print("  - Al menos una letra mayuscula")
            print("  - Al menos una letra minuscula")
            print("  - Al menos un numero")
            return None
        except Exception as e:
            print(f"\nERROR: Error inesperado: {e}")
            import traceback

            traceback.print_exc()
            return None


async def main():
    """Main function to create admin user."""
    parser = argparse.ArgumentParser(
        description="Create the first admin user for ContraVento",
        epilog="If no arguments provided, creates default admin with username 'admin'",
    )
    parser.add_argument("--username", type=str, help="Admin username (default: admin)")
    parser.add_argument("--email", type=str, help="Admin email (default: admin@contravento.com)")
    parser.add_argument(
        "--password",
        type=str,
        help="Admin password (default: AdminPass123!)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Create admin even if others already exist (skip confirmation)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("CREACION DE ADMINISTRADOR - CONTRAVENTO")
    print("=" * 60)
    print()

    # Use defaults if not provided
    username = args.username or "admin"
    email = args.email or "admin@contravento.com"
    password = args.password or "AdminPass123!"

    # Show what we're about to create
    print("[INFO] Creando administrador con las siguientes credenciales:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)} (oculto)")
    print()

    # Create admin
    user = await create_admin_user(
        username=username, email=email, password=password, force=args.force
    )

    if user:
        print("\nAdministrador creado exitosamente!")
        print("\nPuedes hacer login con:")
        print("  POST /auth/login")
        print(f'  {{"login": "{username}", "password": "{password}"}}')
        print()
        print("Acceso a endpoints administrativos:")
        print("  - POST   /admin/cycling-types")
        print("  - PUT    /admin/cycling-types/{code}")
        print("  - DELETE /admin/cycling-types/{code}")
        print()
    else:
        print("\nNo se pudo crear el administrador")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
