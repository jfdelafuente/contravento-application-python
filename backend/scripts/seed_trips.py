#!/usr/bin/env python3
"""
Seed script to create sample trips for testing.

Usage:
    poetry run python scripts/seed_trips.py
    poetry run python scripts/seed_trips.py --user testuser
    poetry run python scripts/seed_trips.py --user admin --count 5
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse
from uuid import uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.trip import Trip, TripStatus, TripDifficulty, Tag, TripTag
from src.services.stats_service import StatsService

# Import all models to ensure SQLAlchemy relationships are resolved
from src.models.comment import Comment  # noqa: F401
from src.models.like import Like  # noqa: F401
from src.models.notification import Notification, NotificationArchive  # noqa: F401
from src.models.share import Share  # noqa: F401
from src.models.social import Follow  # noqa: F401
from src.models.trip import TripPhoto, TripLocation  # noqa: F401
from src.models.stats import UserStats, Achievement, UserAchievement  # noqa: F401


SAMPLE_TRIPS = [
    {
        "title": "Vía Verde del Aceite - Jaén a Córdoba",
        "description": """Un recorrido espectacular por la antigua vía del tren del aceite.

Esta ruta atraviesa olivares centenarios, puentes históricos y túneles excavados en roca. El paisaje es impresionante durante todo el año, pero especialmente hermoso en primavera cuando los olivos están en flor.

Incluye paradas en pueblos con encanto como Alcaudete, Luque y Baena. La ruta es mayormente llana y asfaltada, perfecta para ciclistas de todos los niveles.

Highlights:
- 12 túneles iluminados
- 5 viaductos con vistas panorámicas
- Gastronomía local: aceite de oliva virgen extra
- Distancia total: 128 km (dividida en 2 días)""",
        "start_date": datetime.now() - timedelta(days=30),
        "end_date": datetime.now() - timedelta(days=28),
        "distance_km": 128.5,
        "difficulty": TripDifficulty.MODERATE,
        "status": TripStatus.PUBLISHED,
        "tags": ["vías verdes", "aceite", "andalucía", "turismo"],
    },
    {
        "title": "Ruta Bikepacking Pirineos - Valle de Ordesa",
        "description": """Aventura de 5 días por el corazón de los Pirineos aragoneses con acampada libre.

El Valle de Ordesa es uno de los lugares más espectaculares de España para hacer bikepacking. Esta ruta combina senderos técnicos, pistas forestales y carreteras secundarias de montaña.

Equipamiento llevado:
- Tienda ultraligera (1.2kg)
- Saco de dormir -5°C
- Hornillo y combustible
- Alforjas Ortlieb (40L total)
- Comida para 5 días

Dificultad técnica alta debido a los desniveles acumulados (+8000m) y algunas secciones de sendero expuesto. Recomendado solo para ciclistas con experiencia en montaña.

El paisaje compensa con creces el esfuerzo: cascadas, lagos glaciares, bosques de hayas y pinos negros, fauna salvaje (rebeco, quebrantahuesos).""",
        "start_date": datetime.now() - timedelta(days=60),
        "end_date": datetime.now() - timedelta(days=55),
        "distance_km": 320.0,
        "difficulty": TripDifficulty.DIFFICULT,
        "status": TripStatus.PUBLISHED,
        "tags": ["bikepacking", "montaña", "pirineos", "camping"],
    },
    {
        "title": "Camino de Santiago en Bici - Etapa León a Astorga",
        "description": """Primera etapa de mi Camino Francés en bicicleta. Salida desde la catedral de León hasta Astorga.

Ruta bien señalizada siguiendo las flechas amarillas del Camino. Terreno mixto: asfalto, pista de tierra y algún tramo de sendero.

Conocí peregrinos de todo el mundo. La energía del Camino es única, diferente a cualquier otra ruta ciclista.

Paradas obligatorias:
- Catedral de León (espectacular vidrieras)
- Hospital de Órbigo (puente medieval)
- Astorga (Palacio de Gaudí)

Mañana continúo hacia Ponferrada. El plan es llegar a Santiago en 10 días.""",
        "start_date": datetime.now() - timedelta(days=10),
        "end_date": datetime.now() - timedelta(days=10),
        "distance_km": 52.0,
        "difficulty": TripDifficulty.EASY,
        "status": TripStatus.PUBLISHED,
        "tags": ["camino de santiago", "cultural", "peregrino"],
    },
    {
        "title": "Vuelta al Lago de Sanabria - Zamora",
        "description": """Ruta circular alrededor del lago glaciar más grande de España. Paisaje de alta montaña con aguas cristalinas.

Salida y llegada en Ribadelago. La ruta bordea el lago por pistas forestales y senderos en buen estado. Hay tramos con vistas espectaculares al agua.

Recomendación: madrugar para evitar el viento de la tarde que puede ser bastante fuerte en la zona del embalse.

Llevé la bici de montaña (ruedas 29") y fue perfecta para este terreno. Tubeless recomendado para evitar pinchazos en las zonas pedregosas.""",
        "start_date": datetime.now() - timedelta(days=5),
        "end_date": datetime.now() - timedelta(days=5),
        "distance_km": 45.0,
        "difficulty": TripDifficulty.MODERATE,
        "status": TripStatus.PUBLISHED,
        "tags": ["mtb", "lago", "zamora", "naturaleza"],
    },
    {
        "title": "Borrador: Planificando la Transpirenaica",
        "description": """Ideas para la gran aventura del verano próximo: cruzar los Pirineos de mar a mar.

Ruta prevista: Cabo de Creus (Mediterráneo) hasta Hondarribia (Cantábrico). Aproximadamente 800km y 20.000m de desnivel positivo.

Todavía investigando la mejor época (junio o septiembre para evitar el calor extremo). Necesito decidir si ir por la vertiente norte (Francia) o sur (España).

Material a preparar:
- Bici: decidir entre gravel o MTB
- Alforjas: probar setup bikepacking vs portabultos tradicional
- Presupuesto: calcular alojamientos vs acampada libre

Cualquier consejo es bienvenido!""",
        "start_date": datetime.now() + timedelta(days=120),
        "end_date": datetime.now() + timedelta(days=135),
        "distance_km": 800.0,
        "difficulty": TripDifficulty.VERY_DIFFICULT,
        "status": TripStatus.DRAFT,
        "tags": ["transpirenaica", "proyecto", "verano"],
    },
]


async def get_or_create_tag(db, tag_name: str) -> Tag:
    """Get existing tag or create new one."""
    normalized = tag_name.lower().strip()

    result = await db.execute(
        select(Tag).where(Tag.normalized == normalized)
    )
    tag = result.scalar_one_or_none()

    if not tag:
        tag = Tag(
            name=tag_name,
            normalized=normalized,
            usage_count=0
        )
        db.add(tag)
        await db.flush()

    return tag


async def seed_trips(username: str = "testuser", count: int = None):
    """Create sample trips for testing."""
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"[ERROR] Usuario '{username}' no encontrado")
            print(f"   Crea el usuario primero con: poetry run python scripts/create_verified_user.py --username {username}")
            return

        # Initialize StatsService
        stats_service = StatsService(db)

        # Determine how many trips to create
        trips_to_create = SAMPLE_TRIPS[:count] if count else SAMPLE_TRIPS

        print(f"Creando {len(trips_to_create)} viajes para {user.username}...")

        created_count = 0
        published_count = 0
        for trip_data in trips_to_create:
            # Extract tags from trip_data
            tag_names = trip_data.pop("tags", [])

            # Set published_at for published trips
            is_published = trip_data.get("status") == TripStatus.PUBLISHED
            if is_published:
                trip_data["published_at"] = datetime.now()

            # Create trip
            trip = Trip(
                trip_id=str(uuid4()),
                user_id=user.id,
                **trip_data
            )
            db.add(trip)
            await db.flush()

            # Add tags via TripTag association
            for tag_name in tag_names:
                tag = await get_or_create_tag(db, tag_name)

                # Create TripTag association
                trip_tag = TripTag(trip_id=trip.trip_id, tag_id=tag.tag_id)
                db.add(trip_tag)

                # Increment tag usage
                tag.usage_count += 1

            await db.flush()

            # Update user stats for published trips
            if is_published:
                # For sample data, assume Spain (ES) if no location data
                country_code = "ES"
                photos_count = 0  # Sample trips have no photos yet
                trip_date = trip.start_date.date() if trip.start_date else datetime.now().date()

                await stats_service.update_stats_on_trip_publish(
                    user_id=user.id,
                    distance_km=trip.distance_km,
                    country_code=country_code,
                    photos_count=photos_count,
                    trip_date=trip_date,
                )
                published_count += 1

            status_marker = "[DRAFT]" if trip.status == TripStatus.DRAFT else "[OK]"
            print(f"  {status_marker} {trip.title[:50]}... ({trip.distance_km}km, {trip.difficulty.value})")
            created_count += 1

        await db.commit()

        print(f"\n[SUCCESS] Se crearon {created_count} viajes exitosamente")
        print(f"   Usuario: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Viajes publicados: {published_count} (estadísticas actualizadas)")
        print(f"   Borradores: {created_count - published_count}")
        print(f"\nPrueba en: http://localhost:5173/feed")


async def list_existing_trips(username: str = "testuser"):
    """List existing trips for user."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"[ERROR] Usuario '{username}' no encontrado")
            return

        result = await db.execute(
            select(Trip).where(Trip.user_id == user.id)
        )
        trips = result.scalars().all()

        if not trips:
            print(f"[INFO] El usuario '{username}' no tiene viajes")
            return

        print(f"Viajes de {username} ({len(trips)} total):")
        for trip in trips:
            status_marker = "[DRAFT]" if trip.status == TripStatus.DRAFT else "[OK]"
            print(f"  {status_marker} {trip.title[:60]}")
            print(f"     ID: {trip.trip_id}")
            print(f"     Distancia: {trip.distance_km}km | Dificultad: {trip.difficulty.value}")


def main():
    parser = argparse.ArgumentParser(description="Seed sample trips for testing")
    parser.add_argument(
        "--user",
        default="testuser",
        help="Username to create trips for (default: testuser)"
    )
    parser.add_argument(
        "--count",
        type=int,
        help="Number of trips to create (default: all 5 sample trips)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing trips instead of creating new ones"
    )

    args = parser.parse_args()

    if args.list:
        asyncio.run(list_existing_trips(args.user))
    else:
        asyncio.run(seed_trips(args.user, args.count))


if __name__ == "__main__":
    main()
