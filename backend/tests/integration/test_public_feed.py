"""
Integration Tests for Public Feed API

Tests public access control and feed filtering for trip listings.

Test coverage:
- FR-020: Public feed access (anonymous users)
- FR-021: Authenticated access (user's own trips + drafts)
- FR-022: Access control (owner-only actions)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User
from src.models.trip import Trip, TripStatus


@pytest.mark.integration
class TestAnonymousPublicFeedAccess:
    """Test public feed access for anonymous (non-authenticated) users."""

    async def test_anonymous_access_to_public_trips(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
    ):
        """
        Test GET /trips/public without auth → published trips only.

        Acceptance Criteria (US2-AC4):
        - Anonymous users can access public feed
        - Only published trips returned
        - Drafts are hidden
        """
        # Create 2 published trips and 1 draft
        published_trip_1 = {
            "title": "Published Trip 1",
            "description": "Este es un viaje público número uno con descripción suficiente.",
            "start_date": "2024-06-01",
            "distance_km": 100.0,
        }
        published_trip_2 = {
            "title": "Published Trip 2",
            "description": "Este es un viaje público número dos con descripción suficiente.",
            "start_date": "2024-07-01",
            "distance_km": 150.0,
        }
        draft_trip = {
            "title": "Draft Trip (should be hidden)",
            "description": "Este es un borrador que no debería aparecer públicamente.",
            "start_date": "2024-08-01",
        }

        # Create and publish first two trips
        pub1_response = await client.post("/trips", json=published_trip_1, headers=auth_headers)
        pub1_id = pub1_response.json()["data"]["trip_id"]
        await client.post(f"/trips/{pub1_id}/publish", headers=auth_headers)

        pub2_response = await client.post("/trips", json=published_trip_2, headers=auth_headers)
        pub2_id = pub2_response.json()["data"]["trip_id"]
        await client.post(f"/trips/{pub2_id}/publish", headers=auth_headers)

        # Create draft (don't publish)
        await client.post("/trips", json=draft_trip, headers=auth_headers)

        # Access public feed WITHOUT authentication
        response = await client.get("/trips/public")
        assert response.status_code == 200

        data = response.json()
        # Public feed endpoint returns {trips, pagination} directly (not wrapped in success/data)
        assert "trips" in data
        assert "pagination" in data

        trips = data["trips"]

        # Verify only published trips returned
        trip_titles = [trip["title"] for trip in trips]
        assert "Published Trip 1" in trip_titles
        assert "Published Trip 2" in trip_titles
        assert "Draft Trip (should be hidden)" not in trip_titles

        # Verify all trips have status PUBLISHED
        for trip in trips:
            assert trip["status"].upper() == "PUBLISHED"

    async def test_anonymous_access_feed_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test public feed pagination works for anonymous users."""
        # Create and publish 5 trips
        for i in range(5):
            trip_data = {
                "title": f"Public Trip {i}",
                "description": f"Descripción pública del viaje número {i} con suficiente texto.",
                "start_date": "2024-06-01",
            }
            response = await client.post("/trips", json=trip_data, headers=auth_headers)
            trip_id = response.json()["data"]["trip_id"]
            await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)

        # Get first page (limit=2, page=1)
        response_page1 = await client.get("/trips/public?limit=2&page=1")
        assert response_page1.status_code == 200

        page1_data = response_page1.json()
        assert page1_data["pagination"]["limit"] == 2
        assert page1_data["pagination"]["page"] == 1
        assert len(page1_data["trips"]) <= 2

        # Get second page
        response_page2 = await client.get("/trips/public?limit=2&page=2")
        assert response_page2.status_code == 200

        page2_data = response_page2.json()
        assert page2_data["pagination"]["limit"] == 2
        assert page2_data["pagination"]["page"] == 2

    async def test_anonymous_cannot_see_trip_owner_email(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that public feed doesn't expose user email addresses."""
        # Create and publish trip
        trip_data = {
            "title": "Privacy Test Trip",
            "description": "Verificando que el email del usuario no se expone públicamente.",
            "start_date": "2024-06-01",
        }
        response = await client.post("/trips", json=trip_data, headers=auth_headers)
        trip_id = response.json()["data"]["trip_id"]
        await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)

        # Get public feed
        feed_response = await client.get("/trips/public")
        trips = feed_response.json()["trips"]

        # Find our trip
        our_trip = next((t for t in trips if t["trip_id"] == trip_id), None)
        assert our_trip is not None

        # Verify email is not exposed
        # User info should include username but NOT email
        if "owner" in our_trip:
            assert "email" not in our_trip["owner"]
        # Public trips may not include owner info at all (privacy)


@pytest.mark.integration
class TestAuthenticatedFeedAccess:
    """Test feed access for authenticated users."""

    async def test_authenticated_access_includes_own_drafts(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """
        Test GET /trips with auth → includes user's own drafts.

        Acceptance Criteria (US2-AC4):
        - Authenticated users see all published trips
        - Authenticated users see their own drafts
        - Cannot see other users' drafts
        """
        # Create 1 published trip and 1 draft
        published_data = {
            "title": "My Published Trip",
            "description": "Este es un viaje publicado con descripción completa y suficiente.",
            "start_date": "2024-06-01",
        }
        draft_data = {
            "title": "My Draft Trip",
            "description": "Este es un borrador personal del usuario autenticado.",
            "start_date": "2024-07-01",
        }

        # Create and publish first trip
        pub_response = await client.post("/trips", json=published_data, headers=auth_headers)
        pub_id = pub_response.json()["data"]["trip_id"]
        await client.post(f"/trips/{pub_id}/publish", headers=auth_headers)

        # Create draft (don't publish)
        draft_response = await client.post("/trips", json=draft_data, headers=auth_headers)
        draft_id = draft_response.json()["data"]["trip_id"]

        # Get user's own trips with authentication
        username = test_user.username
        response = await client.get(f"/users/{username}/trips", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # User trips endpoint returns standard {success, data} structure
        assert data["success"] is True
        trips = data["data"]["trips"]

        # Verify both published and draft are returned
        trip_ids = [trip["trip_id"] for trip in trips]
        assert pub_id in trip_ids
        assert draft_id in trip_ids

        # Verify trip statuses
        pub_trip = next(t for t in trips if t["trip_id"] == pub_id)
        draft_trip = next(t for t in trips if t["trip_id"] == draft_id)

        assert pub_trip["status"].upper() == "PUBLISHED"
        assert draft_trip["status"].upper() == "DRAFT"

    async def test_authenticated_cannot_see_others_drafts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test that authenticated users cannot see other users' drafts."""
        # Create another user
        from tests.helpers import create_user

        other_user = await create_user(
            db_session,
            username="other_user",
            email="other@example.com",
            password="OtherPass123!",
        )

        # Create draft as other user (direct database insert)
        draft_trip = Trip(
            user_id=other_user.id,
            title="Other User's Draft",
            description="Draft by another user",
            start_date="2024-06-01",
            status=TripStatus.DRAFT,
        )
        db_session.add(draft_trip)
        await db_session.commit()
        await db_session.refresh(draft_trip)

        # Try to access other user's trips with current user's auth
        response = await client.get(f"/users/{other_user.username}/trips", headers=auth_headers)

        # Depending on implementation:
        # Option 1: Returns only published trips (drafts filtered out)
        # Option 2: Returns 403 Forbidden
        if response.status_code == 200:
            trips = response.json()["data"]["trips"]
            # Verify other user's draft is NOT in the list
            draft_ids = [t["trip_id"] for t in trips if t["status"].upper() == "DRAFT"]
            assert draft_trip.trip_id not in draft_ids
        elif response.status_code == 403:
            # Access forbidden to other user's trips
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


@pytest.mark.integration
class TestAccessControl:
    """Test access control for trip editing and deletion."""

    async def test_owner_can_edit_own_trip(self, client: AsyncClient, auth_headers: dict):
        """
        Test owner can edit their own trip.

        Acceptance Criteria (US2-AC4):
        - Owner can edit/update their trips
        - PUT /trips/{trip_id} succeeds for owner
        """
        # Create trip
        trip_data = {
            "title": "Original Title",
            "description": "Original description with enough text for validation purposes.",
            "start_date": "2024-06-01",
        }
        response = await client.post("/trips", json=trip_data, headers=auth_headers)
        trip_id = response.json()["data"]["trip_id"]

        # Update trip as owner
        update_data = {
            "title": "Updated Title",
            "description": "Updated description with enough text for validation purposes.",
        }
        update_response = await client.put(
            f"/trips/{trip_id}", json=update_data, headers=auth_headers
        )

        assert update_response.status_code == 200
        updated_trip = update_response.json()["data"]
        assert updated_trip["title"] == "Updated Title"

    async def test_owner_can_delete_own_trip(self, client: AsyncClient, auth_headers: dict):
        """
        Test owner can delete their own trip.

        Acceptance Criteria (US2-AC4):
        - Owner can delete their trips
        - DELETE /trips/{trip_id} succeeds for owner
        """
        # Create trip
        trip_data = {
            "title": "Trip to Delete",
            "description": "This trip will be deleted by its owner for testing purposes.",
            "start_date": "2024-06-01",
        }
        response = await client.post("/trips", json=trip_data, headers=auth_headers)
        trip_id = response.json()["data"]["trip_id"]

        # Delete trip as owner
        delete_response = await client.delete(f"/trips/{trip_id}", headers=auth_headers)

        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True

        # Verify trip is deleted
        get_response = await client.get(f"/trips/{trip_id}", headers=auth_headers)
        assert get_response.status_code == 404

    async def test_non_owner_cannot_edit_trip(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """
        Test non-owner cannot edit another user's trip.

        Acceptance Criteria (US2-AC4):
        - Non-owner cannot edit others' trips
        - PUT /trips/{trip_id} returns 403 for non-owner
        """
        # Create another user
        from tests.helpers import create_user

        other_user = await create_user(
            db_session,
            username="other_user_edit",
            email="other_edit@example.com",
            password="OtherPass123!",
        )

        # Create trip as other user
        other_trip = Trip(
            user_id=other_user.id,
            title="Other User's Trip",
            description="Trip created by another user for access control testing.",
            start_date="2024-06-01",
            status=TripStatus.PUBLISHED,
        )
        db_session.add(other_trip)
        await db_session.commit()
        await db_session.refresh(other_trip)

        # Try to edit as current user (not owner)
        update_data = {
            "title": "Hacked Title",
            "description": "Attempting unauthorized edit",
        }
        update_response = await client.put(
            f"/trips/{other_trip.trip_id}",
            json=update_data,
            headers=auth_headers,
        )

        # Should return 403 Forbidden
        assert update_response.status_code == 403
        error = update_response.json()
        assert error["success"] is False
        assert "error" in error

    async def test_non_owner_cannot_delete_trip(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """
        Test non-owner cannot delete another user's trip.

        Acceptance Criteria (US2-AC4):
        - Non-owner cannot delete others' trips
        - DELETE /trips/{trip_id} returns 403 for non-owner
        """
        # Create another user
        from tests.helpers import create_user

        other_user = await create_user(
            db_session,
            username="other_user_delete",
            email="other_delete@example.com",
            password="OtherPass123!",
        )

        # Create trip as other user
        other_trip = Trip(
            user_id=other_user.id,
            title="Other User's Trip to Delete",
            description="Trip that should not be deletable by non-owner.",
            start_date="2024-06-01",
            status=TripStatus.PUBLISHED,
        )
        db_session.add(other_trip)
        await db_session.commit()
        await db_session.refresh(other_trip)

        # Try to delete as current user (not owner)
        delete_response = await client.delete(f"/trips/{other_trip.trip_id}", headers=auth_headers)

        # Should return 403 Forbidden
        assert delete_response.status_code == 403
        error = delete_response.json()
        assert error["success"] is False

        # Verify trip still exists
        result = await db_session.execute(select(Trip).where(Trip.trip_id == other_trip.trip_id))
        still_exists = result.scalar_one_or_none()
        assert still_exists is not None

    async def test_anonymous_cannot_edit_trip(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test that anonymous (unauthenticated) users cannot edit trips."""
        # Create trip
        trip_data = {
            "title": "Trip for Anonymous Edit Test",
            "description": "Testing that anonymous users cannot edit trips.",
            "start_date": "2024-06-01",
        }
        response = await client.post("/trips", json=trip_data, headers=auth_headers)
        trip_id = response.json()["data"]["trip_id"]

        # Try to edit WITHOUT authentication
        update_data = {
            "title": "Anonymous Hack Attempt",
        }
        update_response = await client.put(f"/trips/{trip_id}", json=update_data)

        # Should return 401 Unauthorized
        assert update_response.status_code == 401

    async def test_anonymous_cannot_delete_trip(self, client: AsyncClient, auth_headers: dict):
        """Test that anonymous users cannot delete trips."""
        # Create trip
        trip_data = {
            "title": "Trip for Anonymous Delete Test",
            "description": "Testing that anonymous users cannot delete trips.",
            "start_date": "2024-06-01",
        }
        response = await client.post("/trips", json=trip_data, headers=auth_headers)
        trip_id = response.json()["data"]["trip_id"]

        # Try to delete WITHOUT authentication
        delete_response = await client.delete(f"/trips/{trip_id}")

        # Should return 401 Unauthorized
        assert delete_response.status_code == 401
