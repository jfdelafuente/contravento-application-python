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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select
from database import AsyncSessionLocal
from models.user import User
from models.trip import Trip, TripStatus, TripDifficulty
from models.tag import Tag


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
        "difficulty": TripDifficulty.EXTREME,
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
            print(f"❌ Error: Usuario '{username}' no encontrado")
            print(f"   Crea el usuario primero con: poetry run python scripts/create_verified_user.py --username {username}")
            return

        # Determine how many trips to create
        trips_to_create = SAMPLE_TRIPS[:count] if count else SAMPLE_TRIPS

        print(f"📝 Creando {len(trips_to_create)} viajes para {user.username}...")

        created_count = 0
        for trip_data in trips_to_create:
            # Extract tags from trip_data
            tag_names = trip_data.pop("tags", [])

            # Create trip
            trip = Trip(
                trip_id=uuid4(),
                user_id=user.user_id,
                **trip_data
            )
            db.add(trip)
            await db.flush()

            # Add tags
            for tag_name in tag_names:
                tag = await get_or_create_tag(db, tag_name)
                trip.tags.append(tag)
                tag.usage_count += 1

            await db.flush()

            status_emoji = "📄" if trip.status == TripStatus.DRAFT else "✅"
            print(f"  {status_emoji} {trip.title[:50]}... ({trip.distance_km}km, {trip.difficulty.value})")
            created_count += 1

        await db.commit()

        print(f"\n✅ Se crearon {created_count} viajes exitosamente")
        print(f"   Usuario: {user.username}")
        print(f"   Email: {user.email}")
        print(f"\n🌐 Prueba en: http://localhost:3001/trips")


async def list_existing_trips(username: str = "testuser"):
    """List existing trips for user."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"❌ Usuario '{username}' no encontrado")
            return

        result = await db.execute(
            select(Trip).where(Trip.user_id == user.user_id)
        )
        trips = result.scalars().all()

        if not trips:
            print(f"📭 El usuario '{username}' no tiene viajes")
            return

        print(f"📋 Viajes de {username} ({len(trips)} total):")
        for trip in trips:
            status_emoji = "📄" if trip.status == TripStatus.DRAFT else "✅"
            print(f"  {status_emoji} {trip.title[:60]}")
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
