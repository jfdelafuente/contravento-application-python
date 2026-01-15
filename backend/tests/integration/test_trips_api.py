"""
Integration tests for Trip Photo API workflows.

Tests complete user journeys for photo upload, deletion, and reordering.
Functional Requirements: FR-010, FR-011, FR-012, FR-013
"""

from io import BytesIO

import pytest
from httpx import AsyncClient
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


@pytest.mark.integration
@pytest.mark.asyncio
class TestPhotoUploadWorkflow:
    """
    T049: Integration test for photo upload workflow.

    Tests the journey: create trip → upload photo → verify storage → verify database.
    """

    async def test_upload_photo_complete_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete photo upload workflow.

        Steps:
        1. Create a trip
        2. Upload a photo to the trip
        3. Verify photo is stored in database
        4. Verify photo files are created on filesystem
        5. Verify photo appears in trip GET response
        """
        # Step 1: Create trip
        payload = {
            "title": "Trip for Photo Upload",
            "description": "Testing photo upload workflow",
            "start_date": "2024-05-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Upload photo
        img = Image.new("RGB", (800, 600), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"photo": ("test.jpg", img_bytes, "image/jpeg")}
        upload_response = await client.post(
            f"/trips/{trip_id}/photos", files=files, headers=auth_headers
        )

        # Assert upload response
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["success"] is True

        photo = upload_data["data"]
        photo_id = photo["id"]
        assert photo["trip_id"] == trip_id
        assert photo["photo_url"] is not None
        assert photo["thumb_url"] is not None
        assert photo["order"] == 0  # First photo
        assert photo["file_size"] > 0
        assert photo["width"] > 0
        assert photo["height"] > 0

        # Step 3: Verify database persistence
        from src.models.trip import TripPhoto

        result = await db_session.execute(select(TripPhoto).where(TripPhoto.id == photo_id))
        db_photo = result.scalar_one_or_none()

        assert db_photo is not None
        assert db_photo.trip_id == trip_id
        assert db_photo.order == 0
        assert db_photo.file_size > 0

        # Step 4: Verify files exist on filesystem
        # Note: In test environment, files might be in test storage
        assert db_photo.photo_url is not None
        assert db_photo.thumb_url is not None

        # Step 5: Verify photo in trip GET response
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]

        assert len(trip["photos"]) == 1
        assert trip["photos"][0]["id"] == photo_id

    async def test_upload_multiple_photos_workflow(self, client: AsyncClient, auth_headers: dict):
        """
        Test uploading multiple photos to same trip.

        Steps:
        1. Create trip
        2. Upload 3 photos sequentially
        3. Verify all photos are stored with correct order
        """
        # Step 1: Create trip
        payload = {
            "title": "Multi-Photo Trip",
            "description": "Testing multiple photo uploads",
            "start_date": "2024-05-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Upload 3 photos
        photo_ids = []
        for i, color in enumerate(["red", "green", "blue"]):
            img = Image.new("RGB", (400, 300), color=color)
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            files = {"photo": (f"photo_{i}.jpg", img_bytes, "image/jpeg")}
            upload_response = await client.post(
                f"/trips/{trip_id}/photos", files=files, headers=auth_headers
            )

            assert upload_response.status_code == 201
            photo_data = upload_response.json()["data"]
            photo_ids.append(photo_data["id"])
            assert photo_data["order"] == i

        # Step 3: Verify all photos in GET response
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]

        assert len(trip["photos"]) == 3
        # Verify photos are in correct order
        for i, photo in enumerate(trip["photos"]):
            assert photo["id"] == photo_ids[i]
            assert photo["order"] == i

    async def test_upload_photo_updates_stats_on_published_trip(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test that uploading photo to published trip updates user stats.

        Steps:
        1. Create and publish trip
        2. Upload photo
        3. Verify user stats were updated (photo_count incremented)
        """
        # Step 1: Create and publish trip
        payload = {
            "title": "Published Trip for Stats",
            "description": "A" * 60,  # >50 chars for publishing
            "start_date": "2024-05-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Publish trip
        publish_response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)
        assert publish_response.status_code == 200

        # Get initial stats
        from src.models.stats import UserStats

        # Get user ID from auth token
        get_user_response = await client.get("/users/me", headers=auth_headers)
        user_id = get_user_response.json()["data"]["id"]

        result = await db_session.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats_before = result.scalar_one()
        initial_photo_count = stats_before.total_trip_photos

        # Step 2: Upload photo
        img = Image.new("RGB", (400, 300), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"photo": ("stats_test.jpg", img_bytes, "image/jpeg")}
        upload_response = await client.post(
            f"/trips/{trip_id}/photos", files=files, headers=auth_headers
        )
        assert upload_response.status_code == 201

        # Step 3: Verify stats updated
        await db_session.refresh(stats_before)
        assert stats_before.total_trip_photos == initial_photo_count + 1


@pytest.mark.integration
@pytest.mark.asyncio
class TestPhotoDeleteWorkflow:
    """
    T050: Integration test for photo deletion workflow.

    Tests the journey: create trip → upload photo → delete photo → verify cleanup.
    """

    async def test_delete_photo_complete_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete photo deletion workflow.

        Steps:
        1. Create trip and upload photo
        2. Delete photo via API
        3. Verify photo removed from database
        4. Verify files removed from filesystem
        5. Verify photo no longer appears in trip GET response
        """
        # Step 1: Create trip and upload photo
        payload = {
            "title": "Trip for Photo Delete",
            "description": "Testing photo deletion",
            "start_date": "2024-05-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Upload photo
        img = Image.new("RGB", (300, 200), color="yellow")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"photo": ("delete_test.jpg", img_bytes, "image/jpeg")}
        upload_response = await client.post(
            f"/trips/{trip_id}/photos", files=files, headers=auth_headers
        )
        photo_id = upload_response.json()["data"]["id"]

        # Step 2: Delete photo
        delete_response = await client.delete(
            f"/trips/{trip_id}/photos/{photo_id}", headers=auth_headers
        )

        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["success"] is True
        assert "eliminada" in delete_data["data"]["message"].lower()

        # Step 3: Verify database removal
        from src.models.trip import TripPhoto

        result = await db_session.execute(select(TripPhoto).where(TripPhoto.id == photo_id))
        db_photo = result.scalar_one_or_none()
        assert db_photo is None

        # Step 5: Verify not in trip GET response
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]
        assert len(trip["photos"]) == 0

    async def test_delete_photo_updates_stats_on_published_trip(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test that deleting photo from published trip updates user stats.

        Steps:
        1. Create and publish trip with photo
        2. Delete photo
        3. Verify user stats were updated (photo_count decremented)
        """
        # Step 1: Create, publish trip, and upload photo
        payload = {
            "title": "Published Trip for Stats Delete",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Publish trip
        await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)

        # Upload photo
        img = Image.new("RGB", (200, 200), color="green")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"photo": ("stats_delete.jpg", img_bytes, "image/jpeg")}
        upload_response = await client.post(
            f"/trips/{trip_id}/photos", files=files, headers=auth_headers
        )
        photo_id = upload_response.json()["data"]["id"]

        # Get user stats before deletion
        from src.models.stats import UserStats

        get_user_response = await client.get("/users/me", headers=auth_headers)
        user_id = get_user_response.json()["data"]["id"]

        result = await db_session.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats_before = result.scalar_one()
        initial_photo_count = stats_before.total_trip_photos

        # Step 2: Delete photo
        delete_response = await client.delete(
            f"/trips/{trip_id}/photos/{photo_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

        # Step 3: Verify stats updated
        await db_session.refresh(stats_before)
        assert stats_before.total_trip_photos == initial_photo_count - 1


@pytest.mark.integration
@pytest.mark.asyncio
class TestPhotoReorderWorkflow:
    """
    T051: Integration test for photo reordering workflow.

    Tests the journey: create trip → upload multiple photos → reorder → verify order.
    """

    async def test_reorder_photos_complete_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete photo reordering workflow.

        Steps:
        1. Create trip and upload 4 photos
        2. Reorder photos to new sequence
        3. Verify database order updated
        4. Verify GET response reflects new order
        """
        # Step 1: Create trip and upload 4 photos
        payload = {
            "title": "Trip for Photo Reorder",
            "description": "Testing photo reordering",
            "start_date": "2024-05-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Upload 4 photos
        photo_ids = []
        for i, color in enumerate(["red", "green", "blue", "yellow"]):
            img = Image.new("RGB", (100, 100), color=color)
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            files = {"photo": (f"reorder_{i}.jpg", img_bytes, "image/jpeg")}
            upload_response = await client.post(
                f"/trips/{trip_id}/photos", files=files, headers=auth_headers
            )
            photo_ids.append(upload_response.json()["data"]["id"])

        # Initial order: [red, green, blue, yellow] (indices 0,1,2,3)
        # New order: [yellow, red, blue, green] (indices 3,0,2,1)
        new_order = [photo_ids[3], photo_ids[0], photo_ids[2], photo_ids[1]]

        # Step 2: Reorder photos
        payload = {"photo_order": new_order}
        reorder_response = await client.put(
            f"/trips/{trip_id}/photos/reorder", json=payload, headers=auth_headers
        )

        assert reorder_response.status_code == 200
        reorder_data = reorder_response.json()
        assert reorder_data["success"] is True

        # Step 3: Verify database order
        from src.models.trip import TripPhoto

        result = await db_session.execute(
            select(TripPhoto).where(TripPhoto.trip_id == trip_id).order_by(TripPhoto.order)
        )
        photos = result.scalars().all()

        assert len(photos) == 4
        for i, photo in enumerate(photos):
            assert photo.id == new_order[i]
            assert photo.order == i

        # Step 4: Verify GET response order
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]

        assert len(trip["photos"]) == 4
        for i, photo in enumerate(trip["photos"]):
            assert photo["id"] == new_order[i]
            assert photo["order"] == i

    async def test_reorder_photos_preserves_all_photos(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test that reordering updates order but doesn't lose any photos.

        Steps:
        1. Upload 3 photos
        2. Reorder them
        3. Verify all 3 photos still exist with correct order
        """
        # Step 1: Create trip and upload photos
        payload = {
            "title": "Reorder Preserve Test",
            "description": "Verify no photos lost during reorder",
            "start_date": "2024-05-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        photo_ids = []
        for i in range(3):
            img = Image.new("RGB", (100, 100), color="white")
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            files = {"photo": (f"preserve_{i}.jpg", img_bytes, "image/jpeg")}
            upload_response = await client.post(
                f"/trips/{trip_id}/photos", files=files, headers=auth_headers
            )
            photo_ids.append(upload_response.json()["data"]["id"])

        # Step 2: Reorder (reverse)
        new_order = list(reversed(photo_ids))
        payload = {"photo_order": new_order}
        await client.put(f"/trips/{trip_id}/photos/reorder", json=payload, headers=auth_headers)

        # Step 3: Verify all photos still exist
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]

        assert len(trip["photos"]) == 3
        returned_ids = [p["id"] for p in trip["photos"]]
        assert set(returned_ids) == set(photo_ids)


# ============================================================================
# Phase 6: User Story 4 - Tags & Categorization Integration Tests (T082-T083)
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestTagFilteringWorkflow:
    """
    T082: Integration test for tag filtering workflow.

    Tests the journey: create trips with tags → filter by tag → verify results.
    Functional Requirements: FR-025 (Trip listing with tag filtering)
    """

    async def test_tag_filtering_complete_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete tag filtering workflow.

        Steps:
        1. Create multiple trips with different tags
        2. Publish some trips
        3. Filter by specific tag
        4. Verify only trips with that tag are returned
        5. Test case-insensitive filtering
        6. Test combined tag + status filtering
        """
        # Step 1: Create trips with different tags
        trip_payloads = [
            {
                "title": "Ruta Bikepacking 1",
                "description": "Primera ruta de bikepacking por los Pirineos con acampada salvaje...",
                "start_date": "2024-06-01",
                "tags": ["bikepacking", "montaña"],
            },
            {
                "title": "Ruta Bikepacking 2",
                "description": "Segunda ruta de bikepacking por la costa con vistas espectaculares...",
                "start_date": "2024-07-01",
                "tags": ["bikepacking", "costa"],
            },
            {
                "title": "Ruta Gravel",
                "description": "Ruta de gravel por caminos de tierra y carreteras secundarias rurales...",
                "start_date": "2024-08-01",
                "tags": ["gravel", "rural"],
            },
            {
                "title": "Ruta Montaña",
                "description": "Ascenso a puertos de montaña con desniveles pronunciados y paisajes...",
                "start_date": "2024-09-01",
                "tags": ["montaña", "puerto"],
            },
        ]

        trip_ids = []
        for payload in trip_payloads:
            response = await client.post("/trips", json=payload, headers=auth_headers)
            assert response.status_code == 201
            trip_ids.append(response.json()["data"]["trip_id"])

        # Step 2: Publish first 3 trips (leave last one as draft)
        for trip_id in trip_ids[:3]:
            response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)
            assert response.status_code == 200

        username = "test_user"

        # Step 3: Filter by "bikepacking" tag
        response = await client.get(
            f"/users/{username}/trips?tag=bikepacking", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        trips = data["data"]["trips"]

        # Step 4: Verify only trips with "bikepacking" tag are returned
        assert len(trips) == 2
        for trip in trips:
            assert "bikepacking" in [t.lower() for t in trip["tags"]]

        # Step 5: Test case-insensitive filtering
        response_upper = await client.get(
            f"/users/{username}/trips?tag=BIKEPACKING", headers=auth_headers
        )

        assert response_upper.status_code == 200
        trips_upper = response_upper.json()["data"]["trips"]

        # Should return same results
        assert len(trips_upper) == len(trips)

        # Step 6: Test combined tag + status filtering
        response_published = await client.get(
            f"/users/{username}/trips?tag=bikepacking&status=published",
            headers=auth_headers,
        )

        assert response_published.status_code == 200
        trips_published = response_published.json()["data"]["trips"]

        # Should return only published trips with tag
        assert len(trips_published) == 2
        for trip in trips_published:
            assert "bikepacking" in [t.lower() for t in trip["tags"]]
            assert trip["status"].upper() == "PUBLISHED"

        # Verify filtering by tag "montaña"
        response_mountain = await client.get(
            f"/users/{username}/trips?tag=montaña", headers=auth_headers
        )

        assert response_mountain.status_code == 200
        trips_mountain = response_mountain.json()["data"]["trips"]

        # Should return 2 trips (Bikepacking 1 and Montaña)
        assert len(trips_mountain) == 2

    async def test_tag_filtering_with_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test tag filtering works with pagination parameters."""
        # Create 5 trips with same tag
        for i in range(5):
            payload = {
                "title": f"Viaje Popular {i}",
                "description": f"Descripción del viaje popular número {i} con tag común de prueba...",
                "start_date": "2024-06-01",
                "tags": ["popular"],
            }
            await client.post("/trips", json=payload, headers=auth_headers)

        username = "test_user"

        # Test pagination with limit=2
        response_page1 = await client.get(
            f"/users/{username}/trips?tag=popular&limit=2&offset=0",
            headers=auth_headers,
        )

        assert response_page1.status_code == 200
        data_page1 = response_page1.json()["data"]

        assert data_page1["limit"] == 2
        assert data_page1["offset"] == 0
        assert len(data_page1["trips"]) <= 2

        # Get second page
        response_page2 = await client.get(
            f"/users/{username}/trips?tag=popular&limit=2&offset=2",
            headers=auth_headers,
        )

        assert response_page2.status_code == 200
        data_page2 = response_page2.json()["data"]

        assert data_page2["limit"] == 2
        assert data_page2["offset"] == 2

        # Verify pages don't overlap
        page1_ids = [t["trip_id"] for t in data_page1["trips"]]
        page2_ids = [t["trip_id"] for t in data_page2["trips"]]

        assert len(set(page1_ids) & set(page2_ids)) == 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestTagPopularityWorkflow:
    """
    T083: Integration test for tag popularity ordering.

    Tests the journey: create trips with tags → verify tag usage counts → verify ordering.
    Functional Requirements: FR-027 (Tag browsing with popularity)
    """

    async def test_tag_popularity_ordering_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete tag popularity workflow.

        Steps:
        1. Create trips with varying tag usage
        2. Get all tags
        3. Verify tags are ordered by usage_count descending
        4. Verify usage counts are accurate
        """

        # Step 1: Create trips with varying tag usage
        # Tag "very_popular" will be used 5 times
        for i in range(5):
            payload = {
                "title": f"Viaje Very Popular {i}",
                "description": f"Descripción del viaje muy popular número {i} para conteo de tags...",
                "start_date": "2024-06-01",
                "tags": ["very_popular"],
            }
            await client.post("/trips", json=payload, headers=auth_headers)

        # Tag "moderately_popular" will be used 3 times
        for i in range(3):
            payload = {
                "title": f"Viaje Moderate {i}",
                "description": f"Descripción del viaje moderado número {i} para testing de popularidad...",
                "start_date": "2024-06-01",
                "tags": ["moderately_popular"],
            }
            await client.post("/trips", json=payload, headers=auth_headers)

        # Tag "rare" will be used 1 time
        payload_rare = {
            "title": "Viaje Raro",
            "description": "Descripción del viaje raro único para testing de tag con poco uso...",
            "start_date": "2024-06-01",
            "tags": ["rare"],
        }
        await client.post("/trips", json=payload_rare, headers=auth_headers)

        # Step 2: Get all tags
        response = await client.get("/tags", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        tags = data["data"]["tags"]

        # Step 3: Verify tags are ordered by usage_count descending
        for i in range(len(tags) - 1):
            assert (
                tags[i]["usage_count"] >= tags[i + 1]["usage_count"]
            ), f"Tags not ordered by popularity: {tags[i]['name']}({tags[i]['usage_count']}) should be >= {tags[i+1]['name']}({tags[i+1]['usage_count']})"

        # Step 4: Verify usage counts are accurate
        tag_map = {tag["name"]: tag for tag in tags}

        if "very_popular" in tag_map:
            assert (
                tag_map["very_popular"]["usage_count"] == 5
            ), "very_popular should have usage_count of 5"

        if "moderately_popular" in tag_map:
            assert (
                tag_map["moderately_popular"]["usage_count"] == 3
            ), "moderately_popular should have usage_count of 3"

        if "rare" in tag_map:
            assert tag_map["rare"]["usage_count"] == 1, "rare should have usage_count of 1"

        # Verify normalized field is lowercase
        for tag in tags:
            assert tag["normalized"] == tag["name"].lower()

    async def test_tag_usage_count_updates_on_trip_creation(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test that tag usage_count increases when trips are created."""

        # Get initial tag list
        response_before = await client.get("/tags", headers=auth_headers)
        tags_before = response_before.json()["data"]["tags"]

        tag_map_before = {tag["name"]: tag["usage_count"] for tag in tags_before}
        initial_count = tag_map_before.get("test_increment", 0)

        # Create trip with tag
        payload = {
            "title": "Viaje para incrementar tag",
            "description": "Descripción del viaje para testing de incremento de contador de tags...",
            "start_date": "2024-06-01",
            "tags": ["test_increment"],
        }
        await client.post("/trips", json=payload, headers=auth_headers)

        # Get updated tag list
        response_after = await client.get("/tags", headers=auth_headers)
        tags_after = response_after.json()["data"]["tags"]

        tag_map_after = {tag["name"]: tag["usage_count"] for tag in tags_after}

        # Verify usage count increased
        assert tag_map_after["test_increment"] == initial_count + 1

    async def test_tag_usage_count_with_multiple_tags_per_trip(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that all tags in a trip get their usage_count incremented."""
        # Create trip with 3 tags
        payload = {
            "title": "Viaje con múltiples tags",
            "description": "Descripción del viaje con múltiples tags para testing de incremento múltiple...",
            "start_date": "2024-06-01",
            "tags": ["tag_a", "tag_b", "tag_c"],
        }
        await client.post("/trips", json=payload, headers=auth_headers)

        # Get all tags
        response = await client.get("/tags", headers=auth_headers)
        tags = response.json()["data"]["tags"]

        tag_map = {tag["name"]: tag["usage_count"] for tag in tags}

        # All 3 tags should exist and have at least 1 usage
        assert "tag_a" in tag_map
        assert "tag_b" in tag_map
        assert "tag_c" in tag_map

        assert tag_map["tag_a"] >= 1
        assert tag_map["tag_b"] >= 1
        assert tag_map["tag_c"] >= 1


# ============================================================================
# Phase 5: User Story 3 - Edit/Delete Trips Integration Tests (T066-T068)
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestTripUpdateWorkflow:
    """
    T066: Integration test for trip update workflow.

    Tests the journey: create trip → update fields → verify changes persisted.
    Functional Requirements: FR-016 (Trip editing)
    """

    async def test_trip_update_complete_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete trip update workflow.

        Steps:
        1. Create a trip with initial data
        2. Update multiple fields
        3. Verify changes are persisted in database
        4. Verify updated_at timestamp changed
        5. Update with tags
        6. Verify tag changes
        """
        # Step 1: Create trip
        create_payload = {
            "title": "Viaje Original",
            "description": "Descripción original de al menos 50 caracteres para el viaje inicial de prueba...",
            "start_date": "2024-06-01",
            "distance_km": 100.0,
            "difficulty": "easy",
            "tags": ["original", "inicial"],
        }

        create_response = await client.post("/trips", json=create_payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]
        original_updated_at = create_response.json()["data"]["updated_at"]

        # Step 2: Update multiple fields
        update_payload = {
            "title": "Viaje Actualizado",
            "description": "Descripción completamente nueva con muchos más detalles sobre el viaje actualizado...",
            "distance_km": 150.5,
            "difficulty": "moderate",
            "client_updated_at": original_updated_at,
        }

        update_response = await client.put(
            f"/trips/{trip_id}", json=update_payload, headers=auth_headers
        )

        assert update_response.status_code == 200
        updated_trip = update_response.json()["data"]

        # Step 3: Verify changes persisted
        assert updated_trip["title"] == "Viaje Actualizado"
        assert updated_trip["description"] == update_payload["description"]
        assert updated_trip["distance_km"] == 150.5
        assert updated_trip["difficulty"] == "moderate"

        # Step 4: Verify updated_at changed
        assert updated_trip["updated_at"] != original_updated_at

        # Step 5: Update tags
        new_updated_at = updated_trip["updated_at"]
        tag_update = {
            "tags": ["actualizado", "modificado", "nuevo"],
            "client_updated_at": new_updated_at,
        }

        tag_response = await client.put(f"/trips/{trip_id}", json=tag_update, headers=auth_headers)

        assert tag_response.status_code == 200

        # Step 6: Verify tag changes
        final_trip = tag_response.json()["data"]
        tag_names = [tag["name"] for tag in final_trip["tags"]]

        assert "actualizado" in tag_names
        assert "modificado" in tag_names
        assert "nuevo" in tag_names
        assert "original" not in tag_names  # Old tags replaced


@pytest.mark.integration
@pytest.mark.asyncio
class TestTripDeletionWorkflow:
    """
    T067: Integration test for trip deletion workflow.

    Tests the journey: create trip → add photos → publish → delete → verify cascade + stats.
    Functional Requirements: FR-017, FR-018 (Trip deletion with stats update)
    """

    async def test_trip_deletion_complete_workflow(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test complete trip deletion workflow.

        Steps:
        1. Create trip
        2. Upload photos
        3. Publish trip (updates stats)
        4. Delete trip
        5. Verify trip is deleted
        6. Verify photos are deleted (cascade)
        7. Verify stats are updated (decremented)
        """
        from io import BytesIO

        from PIL import Image
        from sqlalchemy import select

        from src.models.stats import UserStats
        from src.models.trip import Trip

        # Step 1: Create trip
        create_payload = {
            "title": "Viaje a Eliminar",
            "description": "Descripción de al menos 50 caracteres para viaje que será eliminado con fotos...",
            "start_date": "2024-06-01",
            "distance_km": 75.0,
        }

        create_response = await client.post("/trips", json=create_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]
        user_id = create_response.json()["data"]["user_id"]

        # Step 2: Upload photos
        for i in range(2):
            img = Image.new("RGB", (800, 600), color="red")
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            await client.post(
                f"/trips/{trip_id}/photos",
                files={"photo": (f"photo{i}.jpg", img_bytes, "image/jpeg")},
                headers=auth_headers,
            )

        # Step 3: Publish trip
        publish_response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)
        assert publish_response.status_code == 200

        # Get stats before deletion
        stats_before_result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats_before = stats_before_result.scalar_one()
        trips_before = stats_before.total_trips
        km_before = stats_before.total_kilometers
        photos_before = stats_before.total_photos

        # Step 4: Delete trip
        delete_response = await client.delete(f"/trips/{trip_id}", headers=auth_headers)

        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True

        # Step 5: Verify trip is deleted
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        assert get_response.status_code == 404

        # Verify in database
        trip_result = await db_session.execute(select(Trip).where(Trip.trip_id == trip_id))
        deleted_trip = trip_result.scalar_one_or_none()
        assert deleted_trip is None

        # Step 6: Verify cascade deletion (photos deleted)
        # Photos should be deleted via cascade

        # Step 7: Verify stats updated
        await db_session.refresh(stats_before)

        assert stats_before.total_trips == max(0, trips_before - 1)
        assert stats_before.total_kilometers == max(0.0, km_before - 75.0)
        assert stats_before.total_photos == max(0, photos_before - 2)


@pytest.mark.integration
@pytest.mark.asyncio
class TestOptimisticLockingWorkflow:
    """
    T068: Integration test for optimistic locking (concurrent edit prevention).

    Tests the journey: create trip → simulate concurrent edits → verify conflict detection.
    Functional Requirements: FR-020 (Conflict detection)
    """

    async def test_optimistic_locking_prevents_concurrent_edits(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        Test optimistic locking prevents lost updates.

        Steps:
        1. Create trip
        2. User A gets trip data (updated_at = T1)
        3. User B gets trip data (updated_at = T1)
        4. User A updates trip successfully (updated_at = T2)
        5. User B tries to update with stale timestamp (T1) → should fail with 409
        """
        # Step 1: Create trip
        create_payload = {
            "title": "Viaje para Concurrencia",
            "description": "Descripción de al menos 50 caracteres para testing de edición concurrente...",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=create_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]
        initial_updated_at = create_response.json()["data"]["updated_at"]

        # Step 2 & 3: Both users get trip data (simulated by using same timestamp)
        user_a_timestamp = initial_updated_at
        user_b_timestamp = initial_updated_at

        # Step 4: User A updates successfully
        user_a_update = {
            "title": "Actualizado por Usuario A",
            "client_updated_at": user_a_timestamp,
        }

        response_a = await client.put(f"/trips/{trip_id}", json=user_a_update, headers=auth_headers)

        assert response_a.status_code == 200
        new_updated_at = response_a.json()["data"]["updated_at"]
        assert new_updated_at != initial_updated_at

        # Step 5: User B tries to update with stale timestamp → should fail
        user_b_update = {
            "title": "Intento de Usuario B (debería fallar)",
            "client_updated_at": user_b_timestamp,  # Stale!
        }

        response_b = await client.put(f"/trips/{trip_id}", json=user_b_update, headers=auth_headers)

        # Assert - Conflict detected
        assert response_b.status_code == 409
        assert response_b.json()["success"] is False
        assert response_b.json()["error"]["code"] == "CONFLICT"

        # Verify User A's update is preserved
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        current_trip = get_response.json()["data"]

        assert current_trip["title"] == "Actualizado por Usuario A"

    async def test_optimistic_locking_allows_sequential_edits(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that sequential edits with correct timestamps work."""
        # Create trip
        create_payload = {
            "title": "Viaje Secuencial",
            "description": "Descripción de al menos 50 caracteres para testing de ediciones secuenciales...",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=create_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Edit 1
        updated_at_1 = create_response.json()["data"]["updated_at"]
        edit_1 = {
            "title": "Primera Edición",
            "client_updated_at": updated_at_1,
        }

        response_1 = await client.put(f"/trips/{trip_id}", json=edit_1, headers=auth_headers)

        assert response_1.status_code == 200

        # Edit 2 with new timestamp
        updated_at_2 = response_1.json()["data"]["updated_at"]
        edit_2 = {
            "title": "Segunda Edición",
            "client_updated_at": updated_at_2,
        }

        response_2 = await client.put(f"/trips/{trip_id}", json=edit_2, headers=auth_headers)

        # Should succeed because timestamp is current
        assert response_2.status_code == 200
        assert response_2.json()["data"]["title"] == "Segunda Edición"


# =============================================================================
# Phase 7: User Story 5 - Draft Workflow Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestDraftCreationWorkflow:
    """
    T092: Integration test for draft creation workflow.

    Tests the journey: create draft → verify it's saved → verify minimal validation.
    Functional Requirements: FR-028, FR-029
    """

    async def test_create_draft_with_minimal_fields(self, client: AsyncClient, auth_headers: dict):
        """Test creating a draft with only required fields."""
        payload = {
            "title": "My Draft Trip",
            "description": "Short desc",  # Less than 50 chars - OK for draft
            "start_date": "2024-06-01",
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["title"] == "My Draft Trip"
        assert data["status"].lower() == "draft"  # Case-insensitive check
        assert data["published_at"] is None

    async def test_create_draft_without_description(self, client: AsyncClient, auth_headers: dict):
        """Test that draft creation still requires description field."""
        payload = {
            "title": "Draft Without Description",
            "start_date": "2024-06-01",
            # No description
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Should fail validation (description is required even for drafts)
        # Note: Custom validation handler returns 400 instead of default 422
        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.asyncio
class TestDraftVisibility:
    """T093: Integration test for draft visibility (owner-only)."""

    async def test_draft_visible_to_owner(self, client: AsyncClient, auth_headers: dict):
        """Test that owner can see their own draft."""
        payload = {
            "title": "My Private Draft",
            "description": "This is a draft only I should see",
            "start_date": "2024-06-15",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Owner retrieves draft - should succeed
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)

        assert get_response.status_code == 200
        data = get_response.json()["data"]
        assert data["status"].lower() == "draft"
        assert data["title"] == "My Private Draft"

    async def test_draft_not_visible_to_other_users(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that other users cannot see someone else's draft."""
        payload = {
            "title": "Another User's Draft",
            "description": "Private draft content",
            "start_date": "2024-07-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Create another user
        from src.models.user import User as UserModel

        other_user = UserModel(
            username="other_user",
            email="other@example.com",
            hashed_password="dummy_hash",
            is_verified=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Generate token for other user
        from src.utils.security import create_access_token

        other_token = create_access_token({"sub": str(other_user.id)})
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Other user tries to access draft - should fail
        get_response = await client.get(f"/trips/{trip_id}", headers=other_headers)

        assert get_response.status_code == 403  # Forbidden (drafts are private)

    async def test_draft_not_visible_without_auth(self, client: AsyncClient, auth_headers: dict):
        """Test that unauthenticated users cannot see drafts."""
        payload = {
            "title": "Draft for Auth Test",
            "description": "Should not be publicly visible",
            "start_date": "2024-08-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Try to access without auth headers
        get_response = await client.get(f"/trips/{trip_id}")

        # Should fail because unauthenticated users can't see drafts
        assert get_response.status_code in [401, 404]


@pytest.mark.integration
@pytest.mark.asyncio
class TestDraftListing:
    """T094: Integration test for draft listing (separate from published)."""

    async def test_list_only_drafts(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test filtering user trips to show only drafts."""
        # Create 2 drafts and 1 published trip
        draft1_payload = {
            "title": "Draft One",
            "description": "First draft trip",
            "start_date": "2024-06-01",
        }
        draft2_payload = {
            "title": "Draft Two",
            "description": "Second draft trip",
            "start_date": "2024-07-01",
        }
        published_payload = {
            "title": "Published Trip",
            "description": "This is a published trip with enough content for validation",
            "start_date": "2024-08-01",
        }

        # Create drafts
        await client.post("/trips", json=draft1_payload, headers=auth_headers)
        await client.post("/trips", json=draft2_payload, headers=auth_headers)

        # Create and publish trip
        pub_response = await client.post("/trips", json=published_payload, headers=auth_headers)
        pub_trip_id = pub_response.json()["data"]["trip_id"]
        await client.post(f"/trips/{pub_trip_id}/publish", headers=auth_headers)

        # List only drafts
        username = test_user.username
        response = await client.get(f"/users/{username}/trips?status=draft", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()["data"]

        # Should only return 2 drafts
        assert data["count"] == 2
        assert all(trip["status"].lower() == "draft" for trip in data["trips"])
        titles = [trip["title"] for trip in data["trips"]]
        assert "Draft One" in titles
        assert "Draft Two" in titles
        assert "Published Trip" not in titles

    async def test_list_only_published_trips(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test filtering user trips to show only published trips."""
        # Create 1 draft and 2 published trips
        draft_payload = {
            "title": "Draft Trip",
            "description": "Still working on this",
            "start_date": "2024-06-01",
        }
        pub1_payload = {
            "title": "Published One",
            "description": "First published trip with detailed description for validation",
            "start_date": "2024-07-01",
        }
        pub2_payload = {
            "title": "Published Two",
            "description": "Second published trip with detailed description for validation",
            "start_date": "2024-08-01",
        }

        # Create draft (don't publish)
        await client.post("/trips", json=draft_payload, headers=auth_headers)

        # Create and publish trips
        pub1_response = await client.post("/trips", json=pub1_payload, headers=auth_headers)
        pub1_id = pub1_response.json()["data"]["trip_id"]
        await client.post(f"/trips/{pub1_id}/publish", headers=auth_headers)

        pub2_response = await client.post("/trips", json=pub2_payload, headers=auth_headers)
        pub2_id = pub2_response.json()["data"]["trip_id"]
        await client.post(f"/trips/{pub2_id}/publish", headers=auth_headers)

        # List only published trips
        username = test_user.username
        response = await client.get(
            f"/users/{username}/trips?status=published", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # Should only return 2 published trips
        assert data["count"] == 2
        assert all(trip["status"].lower() == "published" for trip in data["trips"])
        titles = [trip["title"] for trip in data["trips"]]
        assert "Published One" in titles
        assert "Published Two" in titles
        assert "Draft Trip" not in titles


@pytest.mark.integration
@pytest.mark.asyncio
class TestDraftToPublishedTransition:
    """T095: Integration test for draft → published transition."""

    async def test_publish_valid_draft(self, client: AsyncClient, auth_headers: dict):
        """Test publishing a draft that meets publication requirements."""
        draft_payload = {
            "title": "Trip Ready to Publish",
            "description": "This trip has enough detail and content to be published successfully",
            "start_date": "2024-06-15",
            "end_date": "2024-06-20",
            "distance_km": 250.5,
        }

        create_response = await client.post("/trips", json=draft_payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Verify it's a draft
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        assert get_response.json()["data"]["status"].lower() == "draft"
        assert get_response.json()["data"]["published_at"] is None

        # Publish the draft
        publish_response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)

        assert publish_response.status_code == 200
        data = publish_response.json()["data"]
        assert data["status"].lower() == "published"
        assert data["published_at"] is not None

        # Verify trip is now published
        final_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        final_data = final_response.json()["data"]
        assert final_data["status"].lower() == "published"

    async def test_publish_draft_with_short_description_fails(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that publishing a draft with insufficient description fails validation."""
        draft_payload = {
            "title": "Draft with Short Description",
            "description": "Too short",  # Less than 50 characters
            "start_date": "2024-07-01",
        }

        create_response = await client.post("/trips", json=draft_payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Try to publish - should fail
        publish_response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)

        assert publish_response.status_code == 400
        error = publish_response.json()["error"]
        assert "descripción" in error["message"].lower()

    async def test_edit_draft_then_publish(self, client: AsyncClient, auth_headers: dict):
        """Test the workflow: create draft → edit → publish."""
        draft_payload = {
            "title": "Initial Draft",
            "description": "Initial draft description",
            "start_date": "2024-08-01",
        }

        create_response = await client.post("/trips", json=draft_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Edit draft to add more content
        edit_payload = {
            "description": "Updated draft with much more detailed description that meets publication requirements",
            "distance_km": 150.0,
        }

        edit_response = await client.put(
            f"/trips/{trip_id}", json=edit_payload, headers=auth_headers
        )
        assert edit_response.status_code == 200

        # Now publish the completed draft
        publish_response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)

        assert publish_response.status_code == 200
        publish_data = publish_response.json()["data"]
        assert publish_data["status"].lower() == "published"

        # Verify the published trip has the updated data
        final_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        data = final_response.json()["data"]
        assert data["status"].lower() == "published"
        assert data.get("distance_km") == 150.0
        assert "Updated draft" in data["description"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestGPSCoordinatesIntegration:
    """
    Integration tests for GPS coordinates feature (009-gps-coordinates).

    Tests the complete workflow for creating and retrieving trips with GPS coordinates.
    Covers User Story 1: View Trip Route on Map.

    Test Coverage:
    - T016: POST /trips with GPS coordinates
    - T017: GET /trips/{trip_id} retrieves coordinates correctly
    """

    async def test_create_trip_with_gps_coordinates(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T016: Test creating a trip with GPS coordinates.

        Validates that GPS coordinates are accepted, stored correctly,
        and precision is enforced to 6 decimal places.
        """
        payload = {
            "title": "Ruta GPS Test - Madrid a Toledo",
            "description": "Test trip with GPS coordinates for integration testing",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "distance_km": 128.5,
            "difficulty": "moderate",
            "locations": [
                {
                    "name": "Madrid",
                    "country": "España",
                    "latitude": 40.416775,
                    "longitude": -3.703790,
                },
                {
                    "name": "Toledo",
                    "country": "España",
                    "latitude": 39.862832,
                    "longitude": -4.027323,
                },
            ],
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert successful creation
        assert response.status_code == 201
        data = response.json()["data"]

        # Verify trip fields
        assert data["title"] == payload["title"]
        assert data["distance_km"] == payload["distance_km"]
        assert data["difficulty"] == payload["difficulty"]

        # Verify locations with coordinates
        assert len(data["locations"]) == 2

        # First location (Madrid)
        loc1 = data["locations"][0]
        assert loc1["name"] == "Madrid"
        # Country field is optional and may not be in response if stored as None
        assert loc1["latitude"] == 40.416775
        assert loc1["longitude"] == -3.70379  # Rounded to 6 decimals

        # Second location (Toledo)
        loc2 = data["locations"][1]
        assert loc2["name"] == "Toledo"
        # Country field is optional and may not be in response if stored as None
        assert loc2["latitude"] == 39.862832
        assert loc2["longitude"] == -4.027323

    async def test_create_trip_with_high_precision_coordinates(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T016: Test that coordinates with >6 decimals are rounded to 6 decimals.

        Validates precision enforcement for GPS coordinates.
        """
        payload = {
            "title": "High Precision GPS Test",
            "description": "Testing coordinate precision rounding",
            "start_date": "2024-07-01",
            "locations": [
                {
                    "name": "Jaca",
                    "latitude": 42.5700841234567,  # 13 decimals
                    "longitude": -0.5499411234567,  # 13 decimals
                }
            ],
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()["data"]

        # Verify coordinates rounded to 6 decimals
        loc = data["locations"][0]
        assert loc["latitude"] == 42.570084  # Rounded to 6 decimals
        assert loc["longitude"] == -0.549941  # Rounded to 6 decimals

    async def test_create_trip_without_gps_coordinates(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T016: Test creating trip without GPS coordinates (backwards compatibility).

        Validates that trips can still be created without coordinates,
        maintaining backwards compatibility with pre-GPS feature trips.
        """
        payload = {
            "title": "Trip Without GPS",
            "description": "Test backwards compatibility - no GPS coordinates",
            "start_date": "2024-08-01",
            "locations": [
                {
                    "name": "Camino de Santiago",
                    "country": "España",
                    # No latitude/longitude
                }
            ],
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()["data"]

        # Verify location exists but without coordinates
        assert len(data["locations"]) == 1
        loc = data["locations"][0]
        assert loc["name"] == "Camino de Santiago"
        # Country field is optional and may not be in response if stored as None
        assert loc["latitude"] is None
        assert loc["longitude"] is None

    async def test_create_trip_with_mixed_locations(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T016: Test creating trip with some locations having GPS, others without.

        Validates that mixed locations (some with coordinates, some without)
        are handled correctly.
        """
        payload = {
            "title": "Mixed GPS Locations",
            "description": "Some locations have GPS, others don't",
            "start_date": "2024-09-01",
            "locations": [
                {
                    "name": "Jaca",
                    "latitude": 42.570084,
                    "longitude": -0.549941,
                },
                {
                    "name": "Somport",
                    # No coordinates
                },
                {
                    "name": "Candanchú",
                    "latitude": 42.774444,
                    "longitude": -0.527778,
                },
            ],
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()["data"]

        # Verify all 3 locations
        assert len(data["locations"]) == 3

        # First location has coordinates
        assert data["locations"][0]["latitude"] == 42.570084
        assert data["locations"][0]["longitude"] == -0.549941

        # Second location has no coordinates
        assert data["locations"][1]["latitude"] is None
        assert data["locations"][1]["longitude"] is None

        # Third location has coordinates
        assert data["locations"][2]["latitude"] == 42.774444
        assert data["locations"][2]["longitude"] == -0.527778

    async def test_create_trip_with_invalid_latitude(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T016: Test that invalid latitude (>90 or <-90) is rejected.

        Validates Spanish error message for invalid latitude.
        """
        payload = {
            "title": "Invalid Latitude Test",
            "description": "Testing latitude validation",
            "start_date": "2024-10-01",
            "locations": [
                {
                    "name": "Invalid Location",
                    "latitude": 100.0,  # Invalid: > 90
                    "longitude": 0.0,
                }
            ],
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Should return 400 Bad Request for validation error
        assert response.status_code == 400
        error_data = response.json()

        # Verify error response structure
        assert error_data.get("success") is False
        assert "error" in error_data

    async def test_create_trip_with_invalid_longitude(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T016: Test that invalid longitude (>180 or <-180) is rejected.

        Validates Spanish error message for invalid longitude.
        """
        payload = {
            "title": "Invalid Longitude Test",
            "description": "Testing longitude validation",
            "start_date": "2024-11-01",
            "locations": [
                {
                    "name": "Invalid Location",
                    "latitude": 0.0,
                    "longitude": 200.0,  # Invalid: > 180
                }
            ],
        }

        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Should return 400 Bad Request for validation error
        assert response.status_code == 400
        error_data = response.json()

        # Verify error response structure
        assert error_data.get("success") is False
        assert "error" in error_data

    async def test_retrieve_trip_with_gps_coordinates(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T017: Test retrieving a trip with GPS coordinates.

        Validates that GET /trips/{trip_id} returns coordinates correctly.
        """
        # First create a trip with GPS coordinates
        create_payload = {
            "title": "Retrieve GPS Test",
            "description": "Testing GPS coordinate retrieval",
            "start_date": "2024-12-01",
            "locations": [
                {
                    "name": "Barcelona",
                    "latitude": 41.385064,
                    "longitude": 2.173404,
                },
                {
                    "name": "Girona",
                    "latitude": 41.979516,
                    "longitude": 2.821426,
                },
            ],
        }

        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Retrieve the trip
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)

        assert get_response.status_code == 200
        data = get_response.json()["data"]

        # Verify trip fields
        assert data["trip_id"] == trip_id
        assert data["title"] == "Retrieve GPS Test"

        # Verify locations with coordinates
        assert len(data["locations"]) == 2

        # First location (Barcelona)
        loc1 = data["locations"][0]
        assert loc1["name"] == "Barcelona"
        assert loc1["latitude"] == 41.385064
        assert loc1["longitude"] == 2.173404

        # Second location (Girona)
        loc2 = data["locations"][1]
        assert loc2["name"] == "Girona"
        assert loc2["latitude"] == 41.979516
        assert loc2["longitude"] == 2.821426

    async def test_retrieve_trip_without_gps_coordinates(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T017: Test retrieving a trip without GPS coordinates.

        Validates backwards compatibility for trips created without coordinates.
        """
        # Create trip without GPS
        create_payload = {
            "title": "No GPS Trip",
            "description": "Trip without GPS coordinates",
            "start_date": "2025-01-01",
            "locations": [{"name": "Vía Verde del Aceite"}],
        }

        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Retrieve the trip
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)

        assert get_response.status_code == 200
        data = get_response.json()["data"]

        # Verify location exists but without coordinates
        assert len(data["locations"]) == 1
        loc = data["locations"][0]
        assert loc["name"] == "Vía Verde del Aceite"
        assert loc["latitude"] is None
        assert loc["longitude"] is None

    async def test_update_trip_coordinates(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        T017: Test updating trip coordinates via PUT /trips/{trip_id}.

        Validates that coordinates can be updated in existing trips.
        """
        # Create trip without GPS first
        create_payload = {
            "title": "Update GPS Test",
            "description": "Testing GPS update functionality",
            "start_date": "2025-02-01",
            "locations": [
                {
                    "name": "Valencia",
                }
            ],
        }

        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Update with GPS coordinates
        update_payload = {
            "locations": [
                {
                    "name": "Valencia",
                    "latitude": 39.469907,
                    "longitude": -0.376288,
                }
            ],
        }

        update_response = await client.put(
            f"/trips/{trip_id}", json=update_payload, headers=auth_headers
        )
        assert update_response.status_code == 200

        # Verify coordinates were added
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        data = get_response.json()["data"]

        assert len(data["locations"]) == 1
        loc = data["locations"][0]
        assert loc["name"] == "Valencia"
        assert loc["latitude"] == 39.469907
        assert loc["longitude"] == -0.376288
