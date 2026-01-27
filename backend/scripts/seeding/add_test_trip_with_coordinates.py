"""
Script to create a test trip with GPS coordinates for fullscreen testing.

Creates a trip with 3 locations in Spain with valid GPS coordinates.
"""

import sqlite3
from datetime import date
import uuid


def create_test_trip():
    """Create a test trip with GPS coordinates."""

    # Connect to SQLite database
    conn = sqlite3.connect('contravento_dev.db')
    cursor = conn.cursor()

    # Get testuser
    cursor.execute("SELECT user_id FROM users WHERE username = 'testuser'")
    user_row = cursor.fetchone()

    if not user_row:
        print("❌ Usuario 'testuser' no encontrado.")
        print("💡 Ejecuta: poetry run python scripts/create_verified_user.py")
        conn.close()
        return

    user_id = user_row[0]

    # Generate UUID for trip
    trip_id = str(uuid.uuid4())

    # Create trip
    cursor.execute("""
        INSERT INTO trips (
            trip_id, user_id, title, description, start_date, end_date,
            distance_km, difficulty, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        trip_id,
        user_id,
        "Ruta de Prueba - Fullscreen Test",
        "Viaje de prueba con coordenadas GPS para validar modo pantalla completa del mapa. Incluye 3 ubicaciones en España: Madrid, Valencia y Barcelona.",
        "2024-06-01",
        "2024-06-03",
        450.5,
        "moderate",
        "PUBLISHED"
    ))

    # Create locations with GPS coordinates
    locations = [
        {
            "location_id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "name": "Madrid",
            "latitude": 40.4168,
            "longitude": -3.7038,
            "sequence": 1
        },
        {
            "location_id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "name": "Valencia",
            "latitude": 39.4699,
            "longitude": -0.3763,
            "sequence": 2
        },
        {
            "location_id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "name": "Barcelona",
            "latitude": 41.3851,
            "longitude": 2.1734,
            "sequence": 3
        }
    ]

    for loc in locations:
        cursor.execute("""
            INSERT INTO trip_locations (
                location_id, trip_id, name, latitude, longitude, sequence, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            loc["location_id"],
            loc["trip_id"],
            loc["name"],
            loc["latitude"],
            loc["longitude"],
            loc["sequence"]
        ))

    conn.commit()

    print("✅ Viaje de prueba creado exitosamente!")
    print(f"📍 Trip ID: {trip_id}")
    print(f"📍 Título: Ruta de Prueba - Fullscreen Test")
    print(f"📍 Ubicaciones: {len(locations)}")
    print("\n🗺️  Coordenadas GPS:")
    for loc in locations:
        print(f"   {loc['sequence']}. {loc['name']}: ({loc['latitude']}, {loc['longitude']})")
    print(f"\n🌐 URL: http://localhost:5173/users/testuser/trips/{trip_id}")
    print("\n✨ Instrucciones:")
    print("   1. Abre la URL en tu navegador")
    print("   2. Desplázate hasta la sección del mapa")
    print("   3. Busca el botón de pantalla completa en la esquina superior derecha del mapa")
    print("   4. Haz click para probar T104 y T105")

    conn.close()


if __name__ == "__main__":
    create_test_trip()
