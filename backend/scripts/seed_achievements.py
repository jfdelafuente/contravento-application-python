"""
Seed predefined achievements into the database.

T169-T170: Seeds the 9 predefined achievements per data-model.md:
1. FIRST_TRIP - First trip published
2. CENTURY - 100km total
3. VOYAGER - 1000km total
4. EXPLORER - 5 countries visited
5. PHOTOGRAPHER - 50 photos uploaded
6. GLOBETROTTER - 10 countries visited
7. MARATHONER - 5000km total
8. INFLUENCER - 100 followers
9. PROLIFIC - 25 trips published

Usage:
    python -m backend.scripts.seed_achievements
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.stats import Achievement


# All 9 predefined achievements
ACHIEVEMENTS = [
    {
        "code": "FIRST_TRIP",
        "name": "Primer Viaje",
        "description": "Publicaste tu primer viaje",
        "badge_icon": "🚴",
        "requirement_type": "trips",
        "requirement_value": 1,
    },
    {
        "code": "CENTURY",
        "name": "Centurión",
        "description": "Recorriste 100 km en total",
        "badge_icon": "💯",
        "requirement_type": "distance",
        "requirement_value": 100,
    },
    {
        "code": "VOYAGER",
        "name": "Viajero",
        "description": "Acumulaste 1000 km",
        "badge_icon": "🌍",
        "requirement_type": "distance",
        "requirement_value": 1000,
    },
    {
        "code": "EXPLORER",
        "name": "Explorador",
        "description": "Visitaste 5 países",
        "badge_icon": "🗺️",
        "requirement_type": "countries",
        "requirement_value": 5,
    },
    {
        "code": "PHOTOGRAPHER",
        "name": "Fotógrafo",
        "description": "Subiste 50 fotos",
        "badge_icon": "📷",
        "requirement_type": "photos",
        "requirement_value": 50,
    },
    {
        "code": "GLOBETROTTER",
        "name": "Trotamundos",
        "description": "Visitaste 10 países",
        "badge_icon": "✈️",
        "requirement_type": "countries",
        "requirement_value": 10,
    },
    {
        "code": "MARATHONER",
        "name": "Maratonista",
        "description": "Recorriste 5000 km",
        "badge_icon": "🏃",
        "requirement_type": "distance",
        "requirement_value": 5000,
    },
    {
        "code": "INFLUENCER",
        "name": "Influencer",
        "description": "Tienes 100 seguidores",
        "badge_icon": "⭐",
        "requirement_type": "followers",
        "requirement_value": 100,
    },
    {
        "code": "PROLIFIC",
        "name": "Prolífico",
        "description": "Publicaste 25 viajes",
        "badge_icon": "📝",
        "requirement_type": "trips",
        "requirement_value": 25,
    },
]


async def seed_achievements():
    """Seed all 9 predefined achievements into database."""
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding achievements...")

        for achievement_data in ACHIEVEMENTS:
            # Check if already exists
            result = await db.execute(
                select(Achievement).where(Achievement.code == achievement_data["code"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭️  {achievement_data['code']} already exists, skipping")
                continue

            # Create achievement
            achievement = Achievement(**achievement_data)
            db.add(achievement)
            print(f"  ✅ Created {achievement_data['code']} - {achievement_data['name']}")

        await db.commit()
        print(f"\n✨ Successfully seeded {len(ACHIEVEMENTS)} achievements!")


async def main():
    """Main entry point."""
    try:
        await seed_achievements()
    except Exception as e:
        print(f"\n❌ Error seeding achievements: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
