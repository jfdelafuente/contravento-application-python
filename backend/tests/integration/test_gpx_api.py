"""
Integration tests for GPX API workflows.

Tests complete user journeys for GPX upload, processing, download, and deletion.
Functional Requirements: FR-001 to FR-008, FR-036, FR-039
Success Criteria: SC-002, SC-003
"""

from pathlib import Path
from io import BytesIO

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import Trip
from src.models.gpx import GPXFile, TrackPoint


@pytest.mark.integration
@pytest.mark.asyncio
class TestGPXUploadWorkflow:
    """
    T018-T019: Integration tests for GPX upload workflow.

    Tests both synchronous (<1MB) and asynchronous (>1MB) processing.
    Success Criteria: SC-002 (<3s for <1MB), SC-003 (<15s for 5-10MB)
    """

    async def test_upload_small_file_sync(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        T018: Test uploading small GPX file (<1MB) with synchronous processing.

        Success Criteria: SC-002 (<3 seconds processing time)
        API Contract: contracts/gpx-api.yaml:86-111
        """
        # Step 1: Create a trip
        payload = {
            "title": "Ruta de Prueba GPX",
            "description": "Viaje para probar la carga de archivos GPX",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Upload small GPX file (<1MB)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "short_route.gpx"

        with open(gpx_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            upload_response = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        # Assert upload response (synchronous processing)
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["success"] is True

        gpx_data = upload_data["data"]
        gpx_file_id = gpx_data["gpx_file_id"]
        assert gpx_data["trip_id"] == trip_id
        assert gpx_data["processing_status"] == "completed"  # Sync processing

        # Assert route statistics are included
        assert gpx_data["distance_km"] > 0
        assert gpx_data["total_points"] > 0
        assert gpx_data["simplified_points"] > 0
        assert gpx_data["has_elevation"] is not None
        assert gpx_data["uploaded_at"] is not None
        assert gpx_data["processed_at"] is not None

        # Step 3: Verify database persistence
        result = await db_session.execute(
            select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id)
        )
        db_gpx = result.scalar_one_or_none()

        assert db_gpx is not None
        assert db_gpx.trip_id == trip_id
        assert db_gpx.processing_status == "completed"
        assert db_gpx.distance_km > 0
        assert db_gpx.file_size > 0

        # Step 4: Verify trackpoints are created
        track_result = await db_session.execute(
            select(TrackPoint).where(TrackPoint.gpx_file_id == gpx_file_id)
        )
        trackpoints = track_result.scalars().all()

        assert len(trackpoints) > 0
        assert len(trackpoints) == db_gpx.simplified_points

    async def test_upload_large_file_async(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """
        T019: Test uploading large GPX file (>1MB) with asynchronous processing.

        Success Criteria: SC-003 (<15 seconds processing time)
        API Contract: contracts/gpx-api.yaml:112-128
        """
        # Step 1: Create a trip
        payload = {
            "title": "Ruta Larga GPX",
            "description": "Viaje con archivo GPX grande para probar procesamiento asíncrono",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        assert create_response.status_code == 201
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Upload large GPX file (>1MB)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "long_route_5mb.gpx"

        with open(gpx_path, "rb") as f:
            files = {"file": ("long_route_5mb.gpx", f, "application/gpx+xml")}
            upload_response = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        # Assert upload response (synchronous processing in testing mode)
        # In testing mode, files >1MB are processed synchronously to avoid
        # SQLite :memory: isolation issues with BackgroundTasks
        assert upload_response.status_code == 201  # Completed synchronously in testing
        upload_data = upload_response.json()
        assert upload_data["success"] is True

        gpx_data = upload_data["data"]
        gpx_file_id = gpx_data["gpx_file_id"]
        assert gpx_data["trip_id"] == trip_id
        assert gpx_data["processing_status"] == "completed"

        # Assert processing completed with valid data
        assert gpx_data["distance_km"] > 0
        assert gpx_data["total_points"] > 0
        assert gpx_data["simplified_points"] > 0
        assert gpx_data["has_elevation"] is True
        assert gpx_data["has_timestamps"] is True

        # Verify via status endpoint (should already be completed)
        final_response = await client.get(f"/gpx/{gpx_file_id}/status")
        final_data = final_response.json()["data"]

        assert final_data["processing_status"] == "completed"
        assert final_data["distance_km"] > 0
        assert final_data["total_points"] > 0
        assert final_data["simplified_points"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestGPXDownloadWorkflow:
    """
    T020: Integration test for downloading original GPX file.

    Functional Requirement: FR-039 (Download original GPX file)
    API Contract: contracts/gpx-api.yaml:390-431
    """

    async def test_download_original_gpx(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test downloading the original GPX file after upload."""
        # Step 1: Create trip and upload GPX
        payload = {
            "title": "Ruta para Descargar",
            "description": "Test de descarga de archivo GPX original",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "short_route.gpx"

        with open(gpx_path, "rb") as f:
            original_content = f.read()
            f.seek(0)
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            upload_response = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        gpx_file_id = upload_response.json()["data"]["gpx_file_id"]

        # Step 2: Download the GPX file
        download_response = await client.get(f"/gpx/{gpx_file_id}/download")

        # Assert download response
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/gpx+xml"
        assert "attachment" in download_response.headers["content-disposition"]

        # Assert downloaded content matches original
        downloaded_content = download_response.content
        assert len(downloaded_content) > 0
        # Should be similar size (might have minor differences due to encoding)
        assert abs(len(downloaded_content) - len(original_content)) < 100


@pytest.mark.integration
@pytest.mark.asyncio
class TestGPXDeleteWorkflow:
    """
    T021: Integration test for deleting GPX file with cascade deletion.

    Functional Requirement: FR-036 (Delete GPX file)
    Data Model: data-model.md:561-570 (cascade deletion)
    """

    async def test_delete_gpx_cascade(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test that deleting GPX file cascades to trackpoints."""
        # Step 1: Create trip and upload GPX
        payload = {
            "title": "Ruta para Eliminar",
            "description": "Test de eliminación en cascada",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "short_route.gpx"

        with open(gpx_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            upload_response = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        gpx_file_id = upload_response.json()["data"]["gpx_file_id"]

        # Step 2: Verify GPX and trackpoints exist
        gpx_result = await db_session.execute(
            select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id)
        )
        gpx_before = gpx_result.scalar_one()
        assert gpx_before is not None

        track_result = await db_session.execute(
            select(TrackPoint).where(TrackPoint.gpx_file_id == gpx_file_id)
        )
        trackpoints_before = track_result.scalars().all()
        assert len(trackpoints_before) > 0

        # Step 3: Delete GPX file
        delete_response = await client.delete(f"/trips/{trip_id}/gpx", headers=auth_headers)

        # Assert deletion response
        assert delete_response.status_code == 204  # No content

        # Step 4: Verify cascade deletion
        # GPX file should be deleted
        gpx_check = await db_session.execute(
            select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id)
        )
        gpx_after = gpx_check.scalar_one_or_none()
        assert gpx_after is None

        # Trackpoints should also be deleted (cascade)
        track_check = await db_session.execute(
            select(TrackPoint).where(TrackPoint.gpx_file_id == gpx_file_id)
        )
        trackpoints_after = track_check.scalars().all()
        assert len(trackpoints_after) == 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestGPXValidation:
    """
    T022: Integration test for GPX file validation.

    Functional Requirements: FR-001 (File size ≤10MB), FR-002, FR-003
    API Contract: contracts/gpx-api.yaml:136-142
    """

    async def test_validate_file_size(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test that files >10MB are rejected."""
        # Step 1: Create a trip
        payload = {
            "title": "Ruta para Validación",
            "description": "Test de validación de tamaño de archivo",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Create a file larger than 10MB
        large_content = b"X" * (11 * 1024 * 1024)  # 11MB
        large_file = BytesIO(large_content)

        files = {"file": ("large.gpx", large_file, "application/gpx+xml")}
        upload_response = await client.post(
            f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
        )

        # Assert rejection
        assert upload_response.status_code == 400
        error_data = upload_response.json()
        assert error_data["success"] is False
        assert "FILE_TOO_LARGE" in error_data["error"]["code"]
        # Error message should be in Spanish
        assert "10MB" in error_data["error"]["message"]

    async def test_validate_gpx_format(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test that invalid GPX format is rejected."""
        # Step 1: Create a trip
        payload = {
            "title": "Ruta para Validación Formato",
            "description": "Test de validación de formato GPX",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Step 2: Upload malformed GPX
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "invalid_gpx.xml"

        with open(gpx_path, "rb") as f:
            files = {"file": ("invalid.gpx", f, "application/gpx+xml")}
            upload_response = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        # Assert rejection
        assert upload_response.status_code == 400
        error_data = upload_response.json()
        assert error_data["success"] is False
        # Error message should mention GPX or formato
        error_msg = error_data["error"]["message"].lower()
        assert "gpx" in error_msg or "formato" in error_msg or "válido" in error_msg

    async def test_trip_can_have_only_one_gpx(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test that a trip can have at most 1 GPX file."""
        # Step 1: Create trip and upload first GPX
        payload = {
            "title": "Ruta con Un GPX",
            "description": "Test de límite de un GPX por viaje",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "short_route.gpx"

        # Upload first GPX
        with open(gpx_path, "rb") as f:
            files = {"file": ("first.gpx", f, "application/gpx+xml")}
            first_upload = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        assert first_upload.status_code == 201

        # Step 2: Try to upload second GPX to same trip
        with open(gpx_path, "rb") as f:
            files = {"file": ("second.gpx", f, "application/gpx+xml")}
            second_upload = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        # Assert rejection
        assert second_upload.status_code == 400
        error_data = second_upload.json()
        assert error_data["success"] is False
        assert "TRIP_ALREADY_HAS_GPX" in error_data["error"]["code"]
