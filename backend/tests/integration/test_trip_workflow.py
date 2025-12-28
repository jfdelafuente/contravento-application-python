"""
Integration tests for Trip creation and publication workflows.

Tests complete user journeys for Travel Diary feature.
Functional Requirements: FR-001, FR-002, FR-003, FR-007
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date


@pytest.mark.integration
@pytest.mark.asyncio
class TestTripCreationWorkflow:
    """
    T029: Integration test for complete trip creation workflow.

    Tests the journey: create draft → add tags → add locations → verify persistence.
    """

    async def test_create_minimal_trip_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test creating a minimal trip and verifying database persistence.

        Steps:
        1. Create trip with minimal required fields
        2. Verify trip is created with status=draft
        3. Verify trip is persisted in database
        4. Verify trip can be retrieved via GET endpoint
        """
        # Step 1: Create trip
        payload = {
            "title": "Vía Verde del Aceite",
            "description": "Un recorrido precioso entre olivos centenarios...",
            "start_date": "2024-05-15",
        }

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )

        # Step 2: Verify creation response
        assert create_response.status_code == 201
        data = create_response.json()
        assert data["success"] is True

        trip = data["data"]
        trip_id = trip["trip_id"]
        assert trip["status"] == "draft"
        assert trip["title"] == payload["title"]
        assert trip["published_at"] is None

        # Step 3: Verify database persistence
        from src.models.trip import Trip

        result = await db_session.execute(select(Trip).where(Trip.trip_id == trip_id))
        db_trip = result.scalar_one_or_none()

        assert db_trip is not None
        assert db_trip.title == payload["title"]
        assert db_trip.description == payload["description"]
        assert str(db_trip.start_date) == payload["start_date"]
        assert db_trip.status.value == "draft"

        # Step 4: Verify retrieval via GET
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        assert get_response.status_code == 200

        retrieved_trip = get_response.json()["data"]
        assert retrieved_trip["trip_id"] == trip_id
        assert retrieved_trip["title"] == payload["title"]

    async def test_create_trip_with_tags_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test creating trip with tags and verifying tag creation/association.

        Steps:
        1. Create trip with tags
        2. Verify tags are created in database
        3. Verify tags are associated with trip
        4. Verify tag usage_count is updated
        """
        # Step 1: Create trip with tags
        payload = {
            "title": "Camino de Santiago",
            "description": "Peregrinación en bicicleta por el Camino Francés",
            "start_date": "2024-06-01",
            "tags": ["camino", "peregrinación", "bikepacking"],
        }

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
        assert create_response.status_code == 201

        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Verify tags in database
        from src.models.trip import Tag, TripTag

        result = await db_session.execute(select(Tag))
        tags = result.scalars().all()

        # At least 3 tags should exist (could be more from other tests)
        tag_names = [tag.name for tag in tags]
        assert "camino" in tag_names
        assert "peregrinación" in tag_names
        assert "bikepacking" in tag_names

        # Step 3: Verify trip-tag associations
        result = await db_session.execute(
            select(TripTag).where(TripTag.trip_id == trip_id)
        )
        trip_tags = result.scalars().all()
        assert len(trip_tags) == 3

        # Step 4: Verify tag usage count
        result = await db_session.execute(
            select(Tag).where(Tag.name == "camino")
        )
        camino_tag = result.scalar_one()
        assert camino_tag.usage_count >= 1

    async def test_create_trip_with_locations_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test creating trip with locations and verifying sequence ordering.

        Steps:
        1. Create trip with multiple locations
        2. Verify locations are created in database
        3. Verify locations are ordered by sequence
        4. Verify locations appear in correct order in GET response
        """
        # Step 1: Create trip with locations
        payload = {
            "title": "Transpirenaica",
            "description": "Cruce completo de los Pirineos de este a oeste",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
            "distance_km": 850.5,
            "difficulty": "very_difficult",
            "locations": [
                {"name": "Hendaya", "country": "Francia"},
                {"name": "Roncesvalles", "country": "España"},
                {"name": "Jaca", "country": "España"},
                {"name": "Llansa", "country": "España"},
            ],
        }

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
        assert create_response.status_code == 201

        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Verify locations in database
        from src.models.trip import TripLocation

        result = await db_session.execute(
            select(TripLocation)
            .where(TripLocation.trip_id == trip_id)
            .order_by(TripLocation.sequence)
        )
        locations = result.scalars().all()

        # Step 3: Verify count and sequence
        assert len(locations) == 4
        assert locations[0].name == "Hendaya"
        assert locations[0].sequence == 0
        assert locations[1].name == "Roncesvalles"
        assert locations[1].sequence == 1
        assert locations[3].name == "Llansa"
        assert locations[3].sequence == 3

        # Step 4: Verify GET response order
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip_locations = get_response.json()["data"]["locations"]

        assert len(trip_locations) == 4
        assert trip_locations[0]["name"] == "Hendaya"
        assert trip_locations[1]["name"] == "Roncesvalles"
        assert trip_locations[3]["name"] == "Llansa"

    async def test_create_trip_with_all_fields_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test creating trip with all optional fields populated.

        Verifies complete data model persistence and retrieval.
        """
        # Arrange
        payload = {
            "title": "Ruta del Cares",
            "description": "<p>Espectacular ruta por el desfiladero del Cares en Picos de Europa</p>",
            "start_date": "2024-08-10",
            "end_date": "2024-08-12",
            "distance_km": 85.3,
            "difficulty": "difficult",
            "locations": [
                {"name": "Caín", "country": "España"},
                {"name": "Poncebos", "country": "España"},
            ],
            "tags": ["montaña", "asturias", "picos de europa"],
        }

        # Act
        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )

        # Assert
        assert create_response.status_code == 201
        trip = create_response.json()["data"]

        # Verify all fields
        assert trip["title"] == payload["title"]
        assert trip["description"] == payload["description"]
        assert trip["start_date"] == payload["start_date"]
        assert trip["end_date"] == payload["end_date"]
        assert trip["distance_km"] == payload["distance_km"]
        assert trip["difficulty"] == payload["difficulty"]
        assert len(trip["locations"]) == 2
        assert len(trip["tags"]) == 3


@pytest.mark.integration
@pytest.mark.asyncio
class TestTripPublicationWorkflow:
    """
    T030: Integration test for trip publication workflow.

    Tests the journey: create draft → validate → publish → verify visibility.
    """

    async def test_publish_valid_trip_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete publication workflow for a valid trip.

        Steps:
        1. Create draft trip with valid data
        2. Verify initial status is 'draft'
        3. Publish trip
        4. Verify status changed to 'published'
        5. Verify published_at timestamp is set
        6. Verify trip appears in database as published
        """
        # Step 1: Create draft trip
        payload = {
            "title": "Vía Verde de la Sierra",
            "description": "A" * 60,  # Exactly 60 chars (>= 50 required for publish)
            "start_date": "2024-05-01",
            "distance_km": 36.0,
            "difficulty": "easy",
        }

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
        assert create_response.status_code == 201

        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Verify initial draft status
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]
        assert trip["status"] == "draft"
        assert trip["published_at"] is None

        # Step 3: Publish trip
        publish_response = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )
        assert publish_response.status_code == 200

        # Step 4: Verify status changed
        publish_data = publish_response.json()["data"]
        assert publish_data["status"] == "published"

        # Step 5: Verify published_at is set
        assert publish_data["published_at"] is not None

        # Step 6: Verify database persistence
        from src.models.trip import Trip

        result = await db_session.execute(select(Trip).where(Trip.trip_id == trip_id))
        db_trip = result.scalar_one()

        assert db_trip.status.value == "published"
        assert db_trip.published_at is not None

    async def test_publish_trip_validation_failure_workflow(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test publication validation failure workflow.

        Steps:
        1. Create trip with short description (< 50 chars)
        2. Attempt to publish
        3. Verify publication is rejected with validation error
        4. Verify trip remains in draft status
        """
        # Step 1: Create trip with short description
        payload = {
            "title": "Test Trip",
            "description": "Too short",  # Only ~9 chars
            "start_date": "2024-05-01",
        }

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Attempt to publish
        publish_response = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )

        # Step 3: Verify rejection
        assert publish_response.status_code == 400
        error_data = publish_response.json()

        assert error_data["success"] is False
        assert error_data["error"]["code"] == "VALIDATION_ERROR"
        assert "descripción" in error_data["error"]["message"].lower()
        assert "50" in error_data["error"]["message"]

        # Step 4: Verify still draft
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]
        assert trip["status"] == "draft"

    async def test_publish_trip_twice_idempotency(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test publishing already-published trip is idempotent.

        Steps:
        1. Create and publish trip
        2. Publish again
        3. Verify second publish succeeds (idempotent)
        4. Verify published_at timestamp doesn't change
        """
        # Step 1: Create and publish
        payload = {
            "title": "Test Idempotency",
            "description": "A" * 60,
            "start_date": "2024-05-01",
        }

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        first_publish = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )
        first_published_at = first_publish.json()["data"]["published_at"]

        # Step 2: Publish again
        second_publish = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )

        # Step 3: Verify success
        assert second_publish.status_code == 200

        # Step 4: Verify timestamp unchanged (or implementation decision)
        second_published_at = second_publish.json()["data"]["published_at"]
        # This tests idempotency - published_at should remain the same
        assert first_published_at == second_published_at

    async def test_draft_to_published_workflow_with_tags(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test that publishing a trip preserves all associated data.

        Steps:
        1. Create trip with tags, locations, all fields
        2. Publish trip
        3. Verify all associated data is preserved
        4. Verify tag usage_count is maintained
        """
        # Step 1: Create complete trip
        payload = {
            "title": "Complete Trip for Publication",
            "description": "<p>" + "A" * 100 + "</p>",
            "start_date": "2024-05-01",
            "end_date": "2024-05-05",
            "distance_km": 200.0,
            "difficulty": "moderate",
            "locations": [
                {"name": "Madrid", "country": "España"},
                {"name": "Toledo", "country": "España"},
            ],
            "tags": ["cultura", "patrimonio"],
        }

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Publish
        publish_response = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )
        assert publish_response.status_code == 200

        # Step 3: Verify all data preserved
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]

        assert trip["status"] == "published"
        assert len(trip["locations"]) == 2
        assert len(trip["tags"]) == 2
        assert trip["distance_km"] == payload["distance_km"]
        assert trip["difficulty"] == payload["difficulty"]

        # Step 4: Verify tag usage_count
        from src.models.trip import Tag

        result = await db_session.execute(
            select(Tag).where(Tag.name == "cultura")
        )
        cultura_tag = result.scalar_one_or_none()
        assert cultura_tag is not None
        assert cultura_tag.usage_count >= 1
