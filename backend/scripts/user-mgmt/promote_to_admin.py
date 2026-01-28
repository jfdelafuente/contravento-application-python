"""
Script to promote an existing user to admin role.

Usage:
    # Promote by username
    poetry run python scripts/promote_to_admin.py --username testuser

    # Promote by email
    poetry run python scripts/promote_to_admin.py --email test@example.com

    # Demote admin to user
    poetry run python scripts/promote_to_admin.py --username testuser --demote

This script updates an existing user's role to ADMIN (or USER if demoting).
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.models.user import User, UserRole

# Import all models to ensure SQLAlchemy relationships are resolved
from src.models.comment import Comment  # noqa: F401
from src.models.like import Like  # noqa: F401
from src.models.notification import Notification, NotificationArchive  # noqa: F401
from src.models.share import Share  # noqa: F401
from src.models.social import Follow  # noqa: F401
from src.models.trip import Trip, TripPhoto, TripLocation, Tag, TripTag  # noqa: F401
from src.models.stats import UserStats, Achievement, UserAchievement  # noqa: F401


async def promote_user(username: str = None, email: str = None, demote: bool = False):
    """
    Promote a user to admin role (or demote to user).

    Args:
        username: Username to promote
        email: Email to promote (alternative to username)
        demote: If True, demote to USER role instead of promoting to ADMIN

    Returns:
        True if successful, False otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            # Find user by username or email
            query = select(User)
            if username:
                query = query.where(User.username == username.lower())
                identifier = f"username '{username}'"
            elif email:
                query = query.where(User.email == email.lower())
                identifier = f"email '{email}'"
            else:
                print("[ERROR] Debes proporcionar --username o --email")
                return False

            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                print(f"[ERROR] No se encontró usuario con {identifier}")
                return False

            # Display current user info
            print("\n[INFO] Usuario encontrado:")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Rol actual: {user.role.value}")
            print(f"  Verificado: {'Sí' if user.is_verified else 'No'}")
            print(f"  Activo: {'Sí' if user.is_active else 'No'}")

            # Check if role change is needed
            target_role = UserRole.USER if demote else UserRole.ADMIN
            action = "degradar" if demote else "promover"

            if user.role == target_role:
                print(f"\n[INFO] El usuario ya tiene el rol {target_role.value.upper()}")
                return True

            # Change role
            user.role = target_role
            await db.commit()
            await db.refresh(user)

            # Display success message
            print("\n" + "=" * 60)
            print(f"{'DEGRADACIÓN' if demote else 'PROMOCIÓN'} EXITOSA")
            print("=" * 60)
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Rol anterior: {UserRole.ADMIN.value if demote else UserRole.USER.value}")
            print(f"Rol nuevo: {user.role.value}")
            print("=" * 60)

            if not demote:
                print("\n[OK] El usuario ahora puede acceder a endpoints administrativos:")
                print("  - POST   /admin/cycling-types")
                print("  - PUT    /admin/cycling-types/{code}")
                print("  - DELETE /admin/cycling-types/{code}")
                print("  - etc.")

            return True

        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            import traceback

            traceback.print_exc()
            return False


async def main():
    """Main function to promote/demote users."""
    parser = argparse.ArgumentParser(
        description="Promote user to admin role or demote admin to user"
    )
    parser.add_argument("--username", type=str, help="Username of user to promote/demote")
    parser.add_argument("--email", type=str, help="Email of user to promote/demote")
    parser.add_argument(
        "--demote",
        action="store_true",
        help="Demote from ADMIN to USER instead of promoting",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("GESTOR DE ROLES - ADMINISTRADOR")
    print("=" * 60)
    print()

    # Validate arguments
    if not args.username and not args.email:
        print("[ERROR] Debes proporcionar --username o --email")
        print("\nEjemplos:")
        print("  # Promover a admin")
        print("  poetry run python scripts/promote_to_admin.py --username testuser")
        print("  poetry run python scripts/promote_to_admin.py --email test@example.com")
        print("\n  # Degradar a usuario regular")
        print("  poetry run python scripts/promote_to_admin.py --username testuser --demote")
        return

    if args.username and args.email:
        print("[ERROR] Proporciona solo --username O --email, no ambos")
        return

    # Promote/demote user
    success = await promote_user(username=args.username, email=args.email, demote=args.demote)

    if success:
        print("\n[OK] Operación completada exitosamente!")
    else:
        print("\n[ERROR] No se pudo completar la operación")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
