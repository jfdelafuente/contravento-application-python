#!/usr/bin/env python3
"""Clean all trips for a user."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.trip import Trip

async def clean_trips(username: str = "testuser"):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"[ERROR] Usuario '{username}' no encontrado")
            return
        
        # Delete all trips
        result = await db.execute(delete(Trip).where(Trip.user_id == user.id))
        await db.commit()
        
        print(f"[SUCCESS] Se eliminaron {result.rowcount} viajes de {username}")

if __name__ == "__main__":
    asyncio.run(clean_trips())
