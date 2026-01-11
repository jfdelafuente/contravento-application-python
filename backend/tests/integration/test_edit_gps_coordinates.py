"""
Integration tests for GPS Coordinates Editing (User Story 3 - Phase 6).

Tests for PUT /trips/{trip_id} with coordinate updates.

T055: Integration test for updating GPS coordinates on existing trips
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
@pytest.mark.asyncio
class TestEditGPSCoordinatesWorkflow:
    """
    T055: Integration test for PUT /trips/{trip_id} with coordinate updates.

    Tests User Story 3: Edit GPS Coordinates for Existing Trips (Phase 6)

    Validates that users can add, update, and remove GPS coordinates from existing trip locations.
    """

    async def test_update_existing_coordinates(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test updating existing GPS coordinates on a trip.

        Steps:
        1. Create trip with GPS coordinates
        2. Update coordinates with new values
        3. Verify coordinates were updated
        """
        # Step 1: Create trip with coordinates
        payload = {
            "title": "Ruta con Coordenadas Originales",
            "description": "Descripción de prueba con más de 50 caracteres para validación correcta",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "distance_km": 250.5,
            "difficulty": "moderate",
            "locations": [
                {
                    "name": "Madrid",
                    "latitude": 40.0,  # Incorrect coordinate
                    "longitude": -3.0,  # Incorrect coordinate
                },
                {
                    "name": "Valencia",
                    "latitude": 39.0,  # Incorrect coordinate
                    "longitude": -0.3,  # Incorrect coordinate
                },
            ],
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Update coordinates with correct values
        update_payload = {
            "title": "Ruta con Coordenadas Actualizadas",
            "description": "Descripción actualizada con coordenadas GPS correctas de cada ciudad",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "distance_km": 350.0,
            "difficulty": "moderate",
            "locations": [
                {
                    "name": "Madrid",
                    "latitude": 40.416775,  # Corrected coordinate
                    "longitude": -3.703790,  # Corrected coordinate
                },
                {
                    "name": "Valencia",
                    "latitude": 39.469907,  # Corrected coordinate
                    "longitude": -0.376288,  # Corrected coordinate
                },
            ],
        }

        update_response = await client.put(
            f"/trips/{trip_id}", json=update_payload, headers=auth_headers
        )
        assert update_response.status_code == 200

        # Step 3: Verify coordinates were updated
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        assert get_response.status_code == 200

        data = get_response.json()["data"]
        assert len(data["locations"]) == 2

        # Verify Madrid coordinates
        madrid = next(loc for loc in data["locations"] if loc["name"] == "Madrid")
        assert madrid["latitude"] == pytest.approx(40.416775, abs=0.000001)
        assert madrid["longitude"] == pytest.approx(-3.703790, abs=0.000001)

        # Verify Valencia coordinates
        valencia = next(loc for loc in data["locations"] if loc["name"] == "Valencia")
        assert valencia["latitude"] == pytest.approx(39.469907, abs=0.000001)
        assert valencia["longitude"] == pytest.approx(-0.376288, abs=0.000001)

    async def test_add_coordinates_to_location_without_gps(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test adding GPS coordinates to a location that previously had none.

        Steps:
        1. Create trip with location without coordinates
        2. Update trip adding coordinates to that location
        3. Verify coordinates were added
        """
        # Step 1: Create trip without coordinates
        payload = {
            "title": "Ruta Sin Coordenadas",
            "description": "Viaje histórico creado antes de que existiera la funcionalidad GPS",
            "start_date": "2023-05-01",
            "locations": [
                {"name": "Sevilla"},  # No coordinates
                {"name": "Córdoba"},  # No coordinates
            ],
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Verify no coordinates initially
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        data = get_response.json()["data"]
        assert data["locations"][0]["latitude"] is None
        assert data["locations"][0]["longitude"] is None

        # Step 2: Add coordinates to Sevilla
        update_payload = {
            "title": "Ruta Con Coordenadas Añadidas",
            "description": "Ahora con coordenadas GPS para visualización en el mapa del viaje",
            "start_date": "2023-05-01",
            "locations": [
                {
                    "name": "Sevilla",
                    "latitude": 37.389092,  # Added coordinate
                    "longitude": -5.984459,  # Added coordinate
                },
                {
                    "name": "Córdoba",
                    "latitude": 37.888175,  # Added coordinate
                    "longitude": -4.779383,  # Added coordinate
                },
            ],
        }

        update_response = await client.put(
            f"/trips/{trip_id}", json=update_payload, headers=auth_headers
        )
        assert update_response.status_code == 200

        # Step 3: Verify coordinates were added
        final_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        data = final_response.json()["data"]

        sevilla = next(loc for loc in data["locations"] if loc["name"] == "Sevilla")
        assert sevilla["latitude"] == pytest.approx(37.389092, abs=0.000001)
        assert sevilla["longitude"] == pytest.approx(-5.984459, abs=0.000001)

        cordoba = next(loc for loc in data["locations"] if loc["name"] == "Córdoba")
        assert cordoba["latitude"] == pytest.approx(37.888175, abs=0.000001)
        assert cordoba["longitude"] == pytest.approx(-4.779383, abs=0.000001)

    async def test_remove_coordinates_from_location(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test removing GPS coordinates from a location.

        Steps:
        1. Create trip with GPS coordinates
        2. Update trip removing coordinates
        3. Verify coordinates were removed (null values)
        """
        # Step 1: Create trip with coordinates
        payload = {
            "title": "Ruta con Coordenadas a Eliminar",
            "description": "Viaje con coordenadas GPS que serán eliminadas posteriormente en prueba",
            "start_date": "2024-03-01",
            "locations": [
                {
                    "name": "Barcelona",
                    "latitude": 41.385064,
                    "longitude": 2.173404,
                },
                {
                    "name": "Girona",
                    "latitude": 41.983334,
                    "longitude": 2.816667,
                },
            ],
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Remove coordinates from Barcelona (keep Girona)
        update_payload = {
            "title": "Ruta con Coordenadas Parcialmente Eliminadas",
            "description": "Coordenadas de Barcelona eliminadas, Girona mantiene sus coordenadas GPS",
            "start_date": "2024-03-01",
            "locations": [
                {
                    "name": "Barcelona",
                    # No latitude/longitude = null
                },
                {
                    "name": "Girona",
                    "latitude": 41.983334,
                    "longitude": 2.816667,
                },
            ],
        }

        update_response = await client.put(
            f"/trips/{trip_id}", json=update_payload, headers=auth_headers
        )
        assert update_response.status_code == 200

        # Step 3: Verify Barcelona coordinates are null, Girona coordinates remain
        final_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        data = final_response.json()["data"]

        barcelona = next(loc for loc in data["locations"] if loc["name"] == "Barcelona")
        assert barcelona["latitude"] is None
        assert barcelona["longitude"] is None

        girona = next(loc for loc in data["locations"] if loc["name"] == "Girona")
        assert girona["latitude"] == pytest.approx(41.983334, abs=0.000001)
        assert girona["longitude"] == pytest.approx(2.816667, abs=0.000001)

    async def test_mixed_locations_some_with_gps_some_without(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test trip with mixed locations (some with GPS, some without).

        Steps:
        1. Create trip with mixed locations
        2. Verify both types are stored correctly
        3. Update adding coordinates to one without GPS
        4. Verify update worked correctly
        """
        # Step 1: Create trip with mixed locations
        payload = {
            "title": "Ruta Mixta GPS",
            "description": "Viaje con algunas ubicaciones con coordenadas y otras sin ellas para prueba",
            "start_date": "2024-04-01",
            "locations": [
                {
                    "name": "Granada",
                    "latitude": 37.177336,
                    "longitude": -3.598557,
                },
                {
                    "name": "Málaga",
                    # No coordinates
                },
                {
                    "name": "Cádiz",
                    "latitude": 36.529461,
                    "longitude": -6.292337,
                },
            ],
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Verify initial state
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        data = get_response.json()["data"]

        granada = next(loc for loc in data["locations"] if loc["name"] == "Granada")
        assert granada["latitude"] is not None

        malaga = next(loc for loc in data["locations"] if loc["name"] == "Málaga")
        assert malaga["latitude"] is None

        # Step 3: Add coordinates to Málaga
        update_payload = {
            "title": "Ruta Mixta GPS Actualizada",
            "description": "Ahora Málaga también tiene coordenadas GPS añadidas al viaje existente",
            "start_date": "2024-04-01",
            "locations": [
                {
                    "name": "Granada",
                    "latitude": 37.177336,
                    "longitude": -3.598557,
                },
                {
                    "name": "Málaga",
                    "latitude": 36.721261,  # Added
                    "longitude": -4.421408,  # Added
                },
                {
                    "name": "Cádiz",
                    "latitude": 36.529461,
                    "longitude": -6.292337,
                },
            ],
        }

        update_response = await client.put(
            f"/trips/{trip_id}", json=update_payload, headers=auth_headers
        )
        assert update_response.status_code == 200

        # Step 4: Verify all locations now have coordinates
        final_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        data = final_response.json()["data"]

        for loc in data["locations"]:
            assert loc["latitude"] is not None
            assert loc["longitude"] is not None
