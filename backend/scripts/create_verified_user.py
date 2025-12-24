"""
Script to create and verify a test user in development.

Usage:
    # Create default test users
    poetry run python scripts/create_verified_user.py

    # Create a specific user
    poetry run python scripts/create_verified_user.py --username john --email john@example.com --password SecurePass123!

    # Verify an existing user by email
    poetry run python scripts/create_verified_user.py --verify-email test@example.com

This script:
1. Registers a new user
2. Automatically verifies their email (bypassing email verification)
3. Displays the user credentials for testing
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.user import User, UserProfile
from src.models.stats import UserStats, Achievement, UserAchievement
from src.models.social import Follow
from src.services.auth_service import AuthService
from src.schemas.auth import RegisterRequest


async def create_verified_user(username: str, email: str, password: str):
    """
    Create a user and automatically verify their email.

    Args:
        username: Username for the new user
        email: Email address
        password: Password (must meet strength requirements)

    Returns:
        User object if successful, None otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists
            result = await db.execute(
                select(User).where(
                    (User.username == username.lower()) | (User.email == email.lower())
                )
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"[ERROR] Usuario ya existe:")
                print(f"  Username: {existing_user.username}")
                print(f"  Email: {existing_user.email}")
                print(f"  Verificado: {'Si' if existing_user.is_verified else 'No'}")

                # Offer to verify if not verified
                if not existing_user.is_verified:
                    print("\n[INFO] El usuario existe pero no esta verificado.")
                    existing_user.is_verified = True
                    await db.commit()
                    print("[OK] Usuario verificado exitosamente!")

                return existing_user

            # Create new user
            print(f"\n[INFO] Creando usuario '{username}'...")
            auth_service = AuthService(db)

            register_data = RegisterRequest(
                username=username,
                email=email,
                password=password
            )

            # Register user
            user_response = await auth_service.register(register_data)
            print(f"[OK] Usuario registrado: {user_response.username}")

            # Fetch the actual user object
            result = await db.execute(
                select(User).where(User.id == user_response.user_id)
            )
            user = result.scalar_one()

            # Verify the user automatically (bypass email verification)
            user.is_verified = True
            await db.commit()
            await db.refresh(user)

            print(f"[OK] Email verificado automaticamente")

            # Display user info
            print("\n" + "="*60)
            print("USUARIO CREADO Y VERIFICADO")
            print("="*60)
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password: {password}")
            print(f"User ID: {user.id}")
            print(f"Verificado: Si")
            print(f"Activo: {'Si' if user.is_active else 'No'}")
            print("="*60)

            return user

        except ValueError as e:
            print(f"[ERROR] Error de validacion: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return None


async def verify_user_by_email(email: str):
    """
    Verify an existing user by email.

    Args:
        email: Email address of the user to verify

    Returns:
        User object if successful, None otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            # Find user by email
            result = await db.execute(
                select(User).where(User.email == email.lower())
            )
            user = result.scalar_one_or_none()

            if not user:
                print(f"[ERROR] No se encontro usuario con email: {email}")
                return None

            print(f"\n[INFO] Usuario encontrado:")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Verificado: {'Si' if user.is_verified else 'No'}")

            if user.is_verified:
                print("\n[INFO] El usuario ya esta verificado.")
                return user

            # Verify the user
            user.is_verified = True
            await db.commit()
            await db.refresh(user)

            print("\n[OK] Usuario verificado exitosamente!")

            # Display user info
            print("\n" + "="*60)
            print("USUARIO VERIFICADO")
            print("="*60)
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"User ID: {user.id}")
            print(f"Verificado: Si")
            print(f"Activo: {'Si' if user.is_active else 'No'}")
            print("="*60)

            return user

        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    """Main function to create test users or verify existing ones."""
    parser = argparse.ArgumentParser(
        description="Create and verify test users for development"
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Username for the new user"
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Email address for the new user"
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Password for the new user (min 8 chars, uppercase, lowercase, number)"
    )
    parser.add_argument(
        "--verify-email",
        type=str,
        help="Email of existing user to verify"
    )

    args = parser.parse_args()

    print("="*60)
    print("CREADOR DE USUARIOS VERIFICADOS - DESARROLLO")
    print("="*60)
    print()

    # If verify-email flag is provided, only verify that user
    if args.verify_email:
        await verify_user_by_email(args.verify_email)
        return

    # If custom user credentials provided, create that user
    if args.username and args.email and args.password:
        print(f"[INFO] Creando usuario personalizado '{args.username}'...")
        user = await create_verified_user(
            username=args.username,
            email=args.email,
            password=args.password
        )

        if user:
            print("\n[OK] Usuario creado exitosamente!")
            print("\nPuedes hacer login con:")
            print("  POST /auth/login")
            print(f'  {{"login": "{args.username}", "password": "{args.password}"}}')
        return

    # If only some arguments provided, show error
    if args.username or args.email or args.password:
        print("[ERROR] Debes proporcionar --username, --email y --password juntos")
        print("\nUso:")
        print("  poetry run python scripts/create_verified_user.py --username john --email john@example.com --password SecurePass123!")
        return

    # Default behavior: create default test users
    print("[INFO] Creando usuario de prueba por defecto...")
    user1 = await create_verified_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123!"
    )

    if user1:
        print("\n[OK] Usuario de prueba creado exitosamente!")

    print("\n" + "-"*60)

    # Additional test user with different credentials
    print("\n[INFO] Creando segundo usuario de prueba...")
    user2 = await create_verified_user(
        username="maria_garcia",
        email="maria@example.com",
        password="SecurePass456!"
    )

    if user2:
        print("\n[OK] Segundo usuario creado exitosamente!")

    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    print("\nPuedes hacer login con cualquiera de estos usuarios:")
    print("  POST /auth/login")
    print('  {"login": "testuser", "password": "TestPass123!"}')
    print("  o")
    print('  {"login": "maria_garcia", "password": "SecurePass456!"}')
    print()


if __name__ == "__main__":
    asyncio.run(main())
