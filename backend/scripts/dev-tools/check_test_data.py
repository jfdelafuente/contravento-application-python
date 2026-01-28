#!/usr/bin/env python3
"""Script para verificar datos de test (usuarios y trips)."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.trip import Trip


async def main():
    """Verificar usuarios y trips en la base de datos."""
    async with AsyncSessionLocal() as db:
        # Listar usuarios
        users_result = await db.execute(select(User.username, User.email, User.id))
        users = users_result.fetchall()

        print("=== USUARIOS DISPONIBLES ===")
        print(f"Total: {len(users)}")
        print()
        for username, email, user_id in users:
            print(f"  {username:20} {email}")

        # Contar trips por usuario
        print("\n=== TRIPS POR USUARIO ===")
        for username, email, user_id in users:
            trips_result = await db.execute(
                select(func.count(Trip.trip_id))
                .where(Trip.user_id == user_id)
            )
            count = trips_result.scalar()
            print(f"  {username:20} {count} trips")


if __name__ == "__main__":
    asyncio.run(main())
