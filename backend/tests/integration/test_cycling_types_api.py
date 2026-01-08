"""
Integration tests for cycling types API endpoints.

Tests complete workflows for managing cycling types via API.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cycling_type import CyclingType
from src.models.user import User


@pytest.mark.integration
@pytest.mark.asyncio
class TestPublicCyclingTypesEndpoint:
    """Integration tests for public cycling types endpoint."""

    async def test_get_cycling_types_returns_only_active(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Test that GET /cycling-types returns only active types.

        Steps:
        1. Create active and inactive cycling types
        2. Call public endpoint
        3. Verify only active types are returned
        """
        # Step 1: Create test data
        active1 = CyclingType(
            code="mountain", display_name="Mountain", description="MTB", is_active=True
        )
        active2 = CyclingType(code="road", display_name="Road", description="Road cycling", is_active=True)
        inactive = CyclingType(
            code="gravel", display_name="Gravel", description="Gravel riding", is_active=False
        )

        db_session.add_all([active1, active2, inactive])
        await db_session.commit()

        # Step 2: Call endpoint
        response = await client.get("/cycling-types")

        # Step 3: Verify results
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        codes = {item["code"] for item in data}
        assert codes == {"mountain", "road"}

        # Verify structure
        for item in data:
            assert "code" in item
            assert "display_name" in item
            assert "description" in item
            assert "id" not in item  # Public endpoint shouldn't expose internal IDs

    async def test_get_cycling_types_no_auth_required(self, client: AsyncClient):
        """Test that GET /cycling-types doesn't require authentication."""
        # Act
        response = await client.get("/cycling-types")

        # Assert - should not return 401
        assert response.status_code in [200, 404]  # 200 if types exist, 404 if not


@pytest.mark.integration
@pytest.mark.asyncio
class TestAdminCyclingTypesWorkflow:
    """Integration tests for admin cycling types workflow."""

    async def test_complete_crud_workflow(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test complete CRUD workflow for cycling types.

        Steps:
        1. Register and login as admin
        2. Create new cycling type
        3. List all types (verify creation)
        4. Get specific type by code
        5. Update the type
        6. Verify it appears in public endpoint
        7. Soft delete the type
        8. Verify it's gone from public endpoint but exists in admin
        9. Hard delete the type
        10. Verify it's completely gone
        """
        # Step 1: Setup authenticated user
        username = sample_user_data["username"]
        password = sample_user_data["password"]

        register_response = await client.post("/auth/register", json=sample_user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["data"]["user_id"]

        # Verify user
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post("/auth/login", json={"login": username, "password": password})
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Create new cycling type
        create_data = {
            "code": "cyclocross",
            "display_name": "Cyclocross",
            "description": "Mixed terrain racing with obstacles",
            "is_active": True,
        }

        create_response = await client.post(
            "/admin/cycling-types", json=create_data, headers=auth_headers
        )

        assert create_response.status_code == 201
        create_result = create_response.json()
        assert create_result["success"] is True
        assert create_result["data"]["code"] == "cyclocross"
        created_id = create_result["data"]["id"]

        # Step 3: List all types
        list_response = await client.get("/admin/cycling-types", headers=auth_headers)
        assert list_response.status_code == 200
        types_list = list_response.json()
        assert any(t["code"] == "cyclocross" for t in types_list)

        # Step 4: Get specific type by code
        get_response = await client.get("/admin/cycling-types/cyclocross", headers=auth_headers)
        assert get_response.status_code == 200
        type_data = get_response.json()
        assert type_data["code"] == "cyclocross"
        assert type_data["display_name"] == "Cyclocross"

        # Step 5: Update the type
        update_data = {"display_name": "Cyclocross Pro", "description": "Professional cyclocross racing"}

        update_response = await client.put(
            "/admin/cycling-types/cyclocross", json=update_data, headers=auth_headers
        )

        assert update_response.status_code == 200
        update_result = update_response.json()
        assert update_result["success"] is True
        assert update_result["data"]["display_name"] == "Cyclocross Pro"

        # Step 6: Verify in public endpoint
        public_response = await client.get("/cycling-types")
        assert public_response.status_code == 200
        public_types = public_response.json()
        assert any(t["code"] == "cyclocross" for t in public_types)

        # Step 7: Soft delete
        soft_delete_response = await client.delete(
            "/admin/cycling-types/cyclocross", headers=auth_headers
        )
        assert soft_delete_response.status_code == 204

        # Step 8: Verify gone from public but exists in admin
        public_response = await client.get("/cycling-types")
        public_types = public_response.json()
        assert not any(t["code"] == "cyclocross" for t in public_types)

        admin_response = await client.get(
            "/admin/cycling-types?active_only=false", headers=auth_headers
        )
        admin_types = admin_response.json()
        assert any(t["code"] == "cyclocross" and not t["is_active"] for t in admin_types)

        # Step 9: Hard delete
        hard_delete_response = await client.delete(
            "/admin/cycling-types/cyclocross?hard=true", headers=auth_headers
        )
        assert hard_delete_response.status_code == 204

        # Step 10: Verify completely gone
        final_response = await client.get(
            "/admin/cycling-types?active_only=false", headers=auth_headers
        )
        final_types = final_response.json()
        assert not any(t["code"] == "cyclocross" for t in final_types)

    async def test_create_duplicate_code_fails(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers
    ):
        """Test that creating a cycling type with duplicate code fails."""
        # Arrange - create existing type
        existing = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        db_session.add(existing)
        await db_session.commit()

        # Act - try to create duplicate
        create_data = {"code": "mountain", "display_name": "Mountain 2", "is_active": True}

        response = await client.post("/admin/cycling-types", json=create_data, headers=auth_headers)

        # Assert
        assert response.status_code == 400
        response_json = response.json()
        # Handle both detail structures
        if "detail" in response_json:
            error_msg = (
                response_json["detail"]["message"]
                if isinstance(response_json["detail"], dict)
                else str(response_json["detail"])
            )
        else:
            error_msg = response_json.get("error", {}).get("message", "")
        assert "ya existe" in error_msg.lower()

    async def test_update_nonexistent_type_fails(self, client: AsyncClient, auth_headers):
        """Test that updating non-existent cycling type fails."""
        # Arrange
        update_data = {"display_name": "New Name"}

        # Act
        response = await client.put(
            "/admin/cycling-types/nonexistent", json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code == 404
        response_json = response.json()
        if "detail" in response_json:
            error_msg = (
                response_json["detail"]["message"]
                if isinstance(response_json["detail"], dict)
                else str(response_json["detail"])
            )
        else:
            error_msg = response_json.get("error", {}).get("message", "")
        assert "no se encontró" in error_msg.lower()

    async def test_delete_nonexistent_type_fails(self, client: AsyncClient, auth_headers):
        """Test that deleting non-existent cycling type fails."""
        # Act
        response = await client.delete("/admin/cycling-types/nonexistent", headers=auth_headers)

        # Assert
        assert response.status_code == 404
        response_json = response.json()
        if "detail" in response_json:
            error_msg = (
                response_json["detail"]["message"]
                if isinstance(response_json["detail"], dict)
                else str(response_json["detail"])
            )
        else:
            error_msg = response_json.get("error", {}).get("message", "")
        assert "no se encontró" in error_msg.lower()

    async def test_admin_endpoints_require_authentication(self, client: AsyncClient):
        """Test that admin endpoints return 401 without authentication."""
        # Test GET all
        response = await client.get("/admin/cycling-types")
        assert response.status_code == 401

        # Test GET by code
        response = await client.get("/admin/cycling-types/mountain")
        assert response.status_code == 401

        # Test POST
        response = await client.post(
            "/admin/cycling-types", json={"code": "test", "display_name": "Test", "is_active": True}
        )
        assert response.status_code == 401

        # Test PUT
        response = await client.put("/admin/cycling-types/test", json={"display_name": "New"})
        assert response.status_code == 401

        # Test DELETE
        response = await client.delete("/admin/cycling-types/test")
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
class TestCyclingTypeValidation:
    """Integration tests for cycling type validation in profile updates."""

    async def test_profile_update_validates_against_active_types(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that profile update validates cycling_type against active types in DB.

        Steps:
        1. Create active and inactive cycling types
        2. Register and login user
        3. Try to update profile with active type (should succeed)
        4. Try to update profile with inactive type (should fail)
        5. Try to update profile with non-existent type (should fail)
        """
        # Step 1: Create test cycling types
        active = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        inactive = CyclingType(code="road", display_name="Road", is_active=False)
        db_session.add_all([active, inactive])
        await db_session.commit()

        # Step 2: Setup authenticated user
        username = sample_user_data["username"]
        password = sample_user_data["password"]

        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        login_response = await client.post("/auth/login", json={"login": username, "password": password})
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 3: Update with active type (should succeed)
        update_response = await client.put(
            f"/users/{username}/profile", json={"cycling_type": "mountain"}, headers=auth_headers
        )

        assert update_response.status_code == 200
        assert update_response.json()["success"] is True

        # Step 4: Update with inactive type (should fail)
        update_response = await client.put(
            f"/users/{username}/profile", json={"cycling_type": "road"}, headers=auth_headers
        )

        assert update_response.status_code == 400
        response_json = update_response.json()
        if "detail" in response_json:
            error_msg = (
                response_json["detail"]["message"]
                if isinstance(response_json["detail"], dict)
                else str(response_json["detail"])
            )
        else:
            error_msg = response_json.get("error", {}).get("message", "")
        assert "tipo de ciclismo" in error_msg.lower()

        # Step 5: Update with non-existent type (should fail)
        update_response = await client.put(
            f"/users/{username}/profile", json={"cycling_type": "invalid"}, headers=auth_headers
        )

        assert update_response.status_code == 400
        response_json = update_response.json()
        if "detail" in response_json:
            error_msg = (
                response_json["detail"]["message"]
                if isinstance(response_json["detail"], dict)
                else str(response_json["detail"])
            )
        else:
            error_msg = response_json.get("error", {}).get("message", "")
        assert "tipo de ciclismo" in error_msg.lower()
