"""
Integration tests for GPS Trip Creation Wizard full workflow.

Feature: 017-gps-trip-wizard
Phase: 6 (US6 - Publish Trip with Atomic Transaction)
Task: T063 (integration tests for POST /trips/gpx-wizard)

Test Coverage:
- POST /trips/gpx-wizard (atomic trip creation with GPX file)
- Transaction rollback on error
- Full wizard end-to-end flow

Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml
"""

import io
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.gpx import GPXFile
from src.models.trip import Trip, TripStatus


@pytest.mark.integration
@pytest.mark.asyncio
class TestGPXWizardPublishWorkflow:
    """
    Integration tests for POST /trips/gpx-wizard endpoint (atomic trip creation).

    This endpoint creates a trip, uploads the GPX file, and stores telemetry
    in a single atomic transaction. If any step fails, the entire operation is rolled back.

    Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml (lines 224-422)
    """

    @pytest.fixture
    def gpx_fixtures_dir(self) -> Path:
        """Path to GPX test fixtures directory."""
        return Path(__file__).parent.parent / "fixtures" / "gpx"

    async def test_create_trip_with_gpx_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        gpx_fixtures_dir: Path,
    ):
        """
        Test successful atomic trip creation with GPX file.

        Contract: lines 292-346 (201 response example)

        Given: Valid trip data and GPX file with elevation
        When: POST /trips/gpx-wizard with multipart/form-data
        Then: Returns 201 with created trip including GPX metadata
        And: Trip is created in database with PUBLISHED status
        And: GPXFile record is linked to trip
        And: Telemetry data is stored in GPXFile
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"
        assert gpx_file_path.exists(), f"Fixture not found: {gpx_file_path}"

        # Prepare multipart form data
        with open(gpx_file_path, "rb") as f:
            files = {"gpx_file": ("short_route.gpx", f, "application/gpx+xml")}

            form_data = {
                "title": "Ruta Bikepacking Test",
                "description": "Esta es una descripción de prueba con más de 50 caracteres para cumplir con la validación mínima requerida.",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "privacy": "public",
            }

            response = await client.post(
                "/trips/gpx-wizard", headers=auth_headers, files=files, data=form_data
            )

        # Assert response structure
        assert response.status_code == 201, f"Unexpected status: {response.text}"
        data = response.json()

        assert data["success"] is True
        assert data["error"] is None
        assert "data" in data

        # Assert trip data structure
        trip_data = data["data"]
        assert "trip_id" in trip_data
        assert trip_data["title"] == "Ruta Bikepacking Test"
        assert trip_data["description"] == form_data["description"]
        assert trip_data["start_date"] == "2024-06-01"
        assert trip_data["end_date"] == "2024-06-05"
        assert trip_data["privacy"] == "public"
        assert trip_data["status"] == "PUBLISHED"  # Auto-published

        # Assert GPX metadata is included
        assert "gpx_file" in trip_data
        gpx_metadata = trip_data["gpx_file"]
        assert gpx_metadata is not None
        assert "gpx_file_id" in gpx_metadata
        assert "total_distance_km" in gpx_metadata
        assert "elevation_gain" in gpx_metadata
        assert "difficulty" in gpx_metadata
        assert gpx_metadata["has_elevation"] is True

        # Verify trip was created in database
        trip_id = trip_data["trip_id"]
        result = await db_session.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = result.scalar_one_or_none()

        assert trip is not None
        assert trip.title == "Ruta Bikepacking Test"
        assert trip.status == TripStatus.PUBLISHED
        assert trip.distance_km == gpx_metadata["total_distance_km"]
        assert trip.difficulty == gpx_metadata["difficulty"]

        # Verify GPX file was created and linked
        result = await db_session.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        gpx_file = result.scalar_one_or_none()

        assert gpx_file is not None
        assert gpx_file.gpx_file_id == gpx_metadata["gpx_file_id"]
        assert gpx_file.total_distance_km > 0
        assert gpx_file.elevation_gain is not None
        assert gpx_file.has_elevation is True

    async def test_create_trip_without_gpx_elevation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        gpx_fixtures_dir: Path,
    ):
        """
        Test trip creation with GPX file without elevation data.

        Given: Valid trip data and GPX file without elevation
        When: POST /trips/gpx-wizard with multipart/form-data
        Then: Returns 201 with trip and GPX metadata
        And: has_elevation is false
        And: elevation fields are null
        And: difficulty is calculated from distance only
        """
        gpx_file_path = gpx_fixtures_dir / "no_elevation.gpx"
        assert gpx_file_path.exists(), f"Fixture not found: {gpx_file_path}"

        with open(gpx_file_path, "rb") as f:
            files = {"gpx_file": ("no_elevation.gpx", f, "application/gpx+xml")}

            form_data = {
                "title": "Ruta sin Elevación",
                "description": "Descripción de prueba para ruta sin datos de elevación, con más de cincuenta caracteres requeridos.",
                "start_date": "2024-07-01",
                "privacy": "private",
            }

            response = await client.post(
                "/trips/gpx-wizard", headers=auth_headers, files=files, data=form_data
            )

        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        trip_data = data["data"]

        # Assert GPX metadata
        gpx_metadata = trip_data["gpx_file"]
        assert gpx_metadata["has_elevation"] is False
        assert gpx_metadata["elevation_gain"] is None
        assert gpx_metadata["elevation_loss"] is None
        assert gpx_metadata["total_distance_km"] > 0

        # Verify in database
        trip_id = trip_data["trip_id"]
        result = await db_session.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        gpx_file = result.scalar_one_or_none()

        assert gpx_file is not None
        assert gpx_file.has_elevation is False
        assert gpx_file.elevation_gain is None

    async def test_create_trip_validation_error_title_too_long(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test validation error when title exceeds 200 characters.

        Contract: lines 348-363 (400 validation error example)

        Given: Trip data with title > 200 characters
        When: POST /trips/gpx-wizard
        Then: Returns 400 with field-specific error message
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"gpx_file": ("short_route.gpx", f, "application/gpx+xml")}

            # Title with 201 characters
            long_title = "a" * 201

            form_data = {
                "title": long_title,
                "description": "Descripción válida con más de cincuenta caracteres necesarios para pasar la validación.",
                "start_date": "2024-06-01",
                "privacy": "public",
            }

            response = await client.post(
                "/trips/gpx-wizard", headers=auth_headers, files=files, data=form_data
            )

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["data"] is None
        assert "error" in data

        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert "title" in error["message"].lower()
        assert error["field"] == "title"

    async def test_create_trip_validation_error_description_too_short(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test validation error when description is less than 50 characters.

        Given: Trip data with description < 50 characters
        When: POST /trips/gpx-wizard
        Then: Returns 400 with field-specific error for description
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"gpx_file": ("short_route.gpx", f, "application/gpx+xml")}

            form_data = {
                "title": "Ruta válida",
                "description": "Too short",  # Only 9 characters
                "start_date": "2024-06-01",
                "privacy": "public",
            }

            response = await client.post(
                "/trips/gpx-wizard", headers=auth_headers, files=files, data=form_data
            )

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        error = data["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert "description" in error["message"].lower() or "50" in error["message"]
        assert error["field"] == "description"

    async def test_create_trip_invalid_gpx_file(self, client: AsyncClient, auth_headers: dict):
        """
        Test error when GPX file is corrupted or invalid.

        Contract: lines 383-397 (400 invalid GPX example)

        Given: Invalid/corrupted GPX file
        When: POST /trips/gpx-wizard
        Then: Returns 400 with GPX-specific error message
        """
        # Create invalid GPX content
        invalid_gpx = b"This is not a valid GPX file"

        files = {"gpx_file": ("invalid.gpx", io.BytesIO(invalid_gpx), "application/gpx+xml")}

        form_data = {
            "title": "Ruta Test",
            "description": "Descripción con más de cincuenta caracteres para cumplir validación necesaria.",
            "start_date": "2024-06-01",
            "privacy": "public",
        }

        response = await client.post(
            "/trips/gpx-wizard", headers=auth_headers, files=files, data=form_data
        )

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        error = data["error"]
        assert error["code"] in ["INVALID_GPX_FILE", "INVALID_FILE_TYPE"]
        assert "gpx" in error["message"].lower()
        assert error["field"] == "gpx_file"

    async def test_create_trip_missing_gpx_file(self, client: AsyncClient, auth_headers: dict):
        """
        Test error when GPX file is not provided.

        Contract: lines 365-376 (400 missing file example)

        Given: Trip data without GPX file
        When: POST /trips/gpx-wizard
        Then: Returns 400 with missing file error
        """
        form_data = {
            "title": "Ruta sin GPX",
            "description": "Descripción con más de cincuenta caracteres para cumplir validación.",
            "start_date": "2024-06-01",
            "privacy": "public",
        }

        response = await client.post("/trips/gpx-wizard", headers=auth_headers, data=form_data)

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        error = data["error"]
        assert error["code"] == "MISSING_FILE"
        assert "gpx" in error["message"].lower() or "archivo" in error["message"].lower()
        assert error["field"] == "gpx_file"

    async def test_create_trip_file_too_large(self, client: AsyncClient, auth_headers: dict):
        """
        Test error when GPX file exceeds 10MB size limit.

        Contract: lines 399-413 (413 file too large example)

        Given: GPX file > 10MB
        When: POST /trips/gpx-wizard
        Then: Returns 413 with file size error
        """
        # Create a large file (11MB)
        large_content = b"<gpx>" + (b"x" * (11 * 1024 * 1024)) + b"</gpx>"

        files = {"gpx_file": ("large.gpx", io.BytesIO(large_content), "application/gpx+xml")}

        form_data = {
            "title": "Ruta con GPX grande",
            "description": "Descripción con más de cincuenta caracteres necesarios para validación.",
            "start_date": "2024-06-01",
            "privacy": "public",
        }

        response = await client.post(
            "/trips/gpx-wizard", headers=auth_headers, files=files, data=form_data
        )

        assert response.status_code == 413
        data = response.json()

        assert data["success"] is False
        error = data["error"]
        assert error["code"] == "FILE_TOO_LARGE"
        assert "10" in error["message"] or "MB" in error["message"]

    async def test_create_trip_unauthorized(self, client: AsyncClient, gpx_fixtures_dir: Path):
        """
        Test that endpoint requires authentication.

        Contract: lines 415-422 (401 unauthorized example)

        Given: No authentication headers
        When: POST /trips/gpx-wizard
        Then: Returns 401 unauthorized
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"gpx_file": ("short_route.gpx", f, "application/gpx+xml")}

            form_data = {
                "title": "Ruta Test",
                "description": "Descripción con más de cincuenta caracteres.",
                "start_date": "2024-06-01",
                "privacy": "public",
            }

            response = await client.post(
                "/trips/gpx-wizard", files=files, data=form_data  # No auth_headers
            )

        assert response.status_code == 401

    async def test_create_trip_database_rollback_on_error(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        gpx_fixtures_dir: Path,
    ):
        """
        Test that trip creation is rolled back if GPX processing fails.

        This tests the atomic transaction behavior: if any step fails after
        trip creation (e.g., GPX upload fails), the trip should be rolled back.

        Given: Valid trip data but simulated GPX processing failure
        When: POST /trips/gpx-wizard
        Then: Returns error response
        And: No trip or GPX file records are created in database
        """
        # This test requires a way to simulate GPX processing failure
        # For now, we'll use an invalid GPX file that will fail during processing

        invalid_gpx = b"<?xml version='1.0'?><gpx><trk><trkseg></trkseg></trk></gpx>"

        files = {"gpx_file": ("empty.gpx", io.BytesIO(invalid_gpx), "application/gpx+xml")}

        form_data = {
            "title": "Ruta que debería fallar",
            "description": "Esta descripción tiene más de cincuenta caracteres necesarios.",
            "start_date": "2024-06-01",
            "privacy": "public",
        }

        # Get initial trip count
        result = await db_session.execute(select(Trip))
        initial_trip_count = len(result.scalars().all())

        response = await client.post(
            "/trips/gpx-wizard", headers=auth_headers, files=files, data=form_data
        )

        # Should return error
        assert response.status_code in [400, 500]

        # Verify no trip was created (rollback successful)
        result = await db_session.execute(select(Trip))
        final_trip_count = len(result.scalars().all())

        assert final_trip_count == initial_trip_count, "Trip should be rolled back on error"
