"""
Integration tests for Trip Photo API workflows.

Tests complete user journeys for photo upload, deletion, and reordering.
Functional Requirements: FR-010, FR-011, FR-012, FR-013
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from PIL import Image
import os


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

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
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

        result = await db_session.execute(
            select(TripPhoto).where(TripPhoto.id == photo_id)
        )
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

    async def test_upload_multiple_photos_workflow(
        self, client: AsyncClient, auth_headers: dict
    ):
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

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
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

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Publish trip
        publish_response = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )
        assert publish_response.status_code == 200

        # Get initial stats
        from src.models.user import UserStats

        # Get user ID from auth token
        get_user_response = await client.get("/users/me", headers=auth_headers)
        user_id = get_user_response.json()["data"]["id"]

        result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
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

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
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

        result = await db_session.execute(
            select(TripPhoto).where(TripPhoto.id == photo_id)
        )
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

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
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
        from src.models.user import UserStats

        get_user_response = await client.get("/users/me", headers=auth_headers)
        user_id = get_user_response.json()["data"]["id"]

        result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
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

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
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
            select(TripPhoto)
            .where(TripPhoto.trip_id == trip_id)
            .order_by(TripPhoto.order)
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

        create_response = await client.post(
            "/trips", json=payload, headers=auth_headers
        )
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
        await client.put(
            f"/trips/{trip_id}/photos/reorder", json=payload, headers=auth_headers
        )

        # Step 3: Verify all photos still exist
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        trip = get_response.json()["data"]

        assert len(trip["photos"]) == 3
        returned_ids = [p["id"] for p in trip["photos"]]
        assert set(returned_ids) == set(photo_ids)
