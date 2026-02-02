"""
Integration tests for GPS Trip Creation Wizard API endpoints.

Feature: 017-gps-trip-wizard
Phase: 4 (US2 - GPX Upload & Processing)
Tasks: T031 (integration tests)

Test Coverage:
- POST /gpx/analyze (temporary GPX analysis for wizard)
- POST /trips/gpx-wizard (atomic trip creation - Phase 6)

Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml
"""

import io
from pathlib import Path

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestGPXAnalyzeEndpoint:
    """
    Integration tests for POST /gpx/analyze endpoint.

    This endpoint extracts telemetry data from GPX files without storing to database.
    Used for wizard Step 1 preview display.

    Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml (lines 32-193)
    """

    @pytest.fixture
    def gpx_fixtures_dir(self) -> Path:
        """Path to GPX test fixtures directory."""
        return Path(__file__).parent.parent / "fixtures" / "gpx"

    async def test_analyze_gpx_with_elevation_success(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test successful GPX analysis with elevation data.

        Contract: lines 70-89 (200 response withElevation example)

        Given: Valid GPX file with elevation data
        When: POST /gpx/analyze with file
        Then: Returns 200 with telemetry data (distance, elevation, difficulty)
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"
        assert gpx_file_path.exists(), f"Fixture not found: {gpx_file_path}"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}

            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        # Assert response structure
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["error"] is None
        assert "data" in data

        # Assert telemetry data structure
        telemetry = data["data"]
        assert "distance_km" in telemetry
        assert "elevation_gain" in telemetry
        assert "elevation_loss" in telemetry
        assert "max_elevation" in telemetry
        assert "min_elevation" in telemetry
        assert "has_elevation" in telemetry
        assert "difficulty" in telemetry

        # Assert data types and constraints
        assert isinstance(telemetry["distance_km"], int | float)
        assert telemetry["distance_km"] >= 0

        assert isinstance(telemetry["has_elevation"], bool)

        if telemetry["has_elevation"]:
            assert telemetry["elevation_gain"] is not None
            assert telemetry["elevation_loss"] is not None
            assert isinstance(telemetry["elevation_gain"], int | float)
            assert isinstance(telemetry["elevation_loss"], int | float)
            assert telemetry["elevation_gain"] >= 0
            assert telemetry["elevation_loss"] >= 0

        # Assert difficulty is valid TripDifficulty enum value
        assert telemetry["difficulty"] in [
            "easy",
            "moderate",
            "difficult",
            "very_difficult",
            "extreme",
        ]

    async def test_analyze_gpx_without_elevation_success(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test successful GPX analysis without elevation data.

        Contract: lines 91-103 (200 response withoutElevation example)

        Given: Valid GPX file without elevation data
        When: POST /gpx/analyze with file
        Then: Returns 200 with distance, has_elevation=false, elevation fields null
        """
        gpx_file_path = gpx_fixtures_dir / "no_elevation.gpx"
        assert gpx_file_path.exists(), f"Fixture not found: {gpx_file_path}"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("no_elevation.gpx", f, "application/gpx+xml")}

            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        telemetry = data["data"]

        # Assert has_elevation is false
        assert telemetry["has_elevation"] is False

        # Assert elevation fields are null
        assert telemetry["elevation_gain"] is None
        assert telemetry["elevation_loss"] is None
        assert telemetry["max_elevation"] is None
        assert telemetry["min_elevation"] is None

        # Assert distance is still calculated
        assert telemetry["distance_km"] > 0

        # Assert difficulty is calculated from distance only
        assert telemetry["difficulty"] in [
            "easy",
            "moderate",
            "difficult",
            "very_difficult",
            "extreme",
        ]

    async def test_analyze_gpx_invalid_file_type(self, client: AsyncClient, auth_headers: dict):
        """
        Test error handling for non-GPX file upload.

        Contract: lines 112-120 (400 response invalidFormat example)

        Given: Non-GPX file (e.g., image, text)
        When: POST /gpx/analyze with file
        Then: Returns 400 with INVALID_FILE_TYPE error
        """
        # Create a fake JPEG file
        fake_jpeg = io.BytesIO(b"\xff\xd8\xff\xe0JFIF")
        files = {"file": ("photo.jpg", fake_jpeg, "image/jpeg")}

        response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["data"] is None
        assert "error" in data

        error = data["error"]
        assert error["code"] == "INVALID_FILE_TYPE"
        assert "formato no válido" in error["message"].lower()
        assert error["field"] == "file"

    async def test_analyze_gpx_corrupted_file(self, client: AsyncClient, auth_headers: dict):
        """
        Test error handling for corrupted GPX file.

        Contract: lines 122-130 (400 response corruptedGpx example)

        Given: Corrupted GPX file (invalid XML)
        When: POST /gpx/analyze with file
        Then: Returns 400 with INVALID_GPX_FILE error
        """
        # Create corrupted GPX file (invalid XML)
        corrupted_gpx = io.BytesIO(
            b"""<?xml version="1.0"?>
        <gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
            <trk>
                <trkseg>
                    <!-- Missing closing tags - corrupted -->
        """
        )
        files = {"file": ("corrupted.gpx", corrupted_gpx, "application/gpx+xml")}

        response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["data"] is None
        assert "error" in data

        error = data["error"]
        assert error["code"] == "INVALID_GPX_FILE"
        assert "no se pudo procesar" in error["message"].lower()
        assert error["field"] == "file"

    async def test_analyze_gpx_file_too_large(self, client: AsyncClient, auth_headers: dict):
        """
        Test error handling for file size exceeding 10MB limit.

        Contract: lines 163-177 (413 response tooLarge example)

        Given: GPX file >10MB
        When: POST /gpx/analyze with file
        Then: Returns 413 with FILE_TOO_LARGE error
        """
        # Create a large fake GPX file (>10MB)
        large_content = b"<trkpt lat='0' lon='0'></trkpt>" * 500000  # ~15MB
        large_gpx = io.BytesIO(
            b"""<?xml version="1.0"?>
        <gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
            <trk>
                <trkseg>
                    """
            + large_content
            + b"""
                </trkseg>
            </trk>
        </gpx>"""
        )
        files = {"file": ("large_route.gpx", large_gpx, "application/gpx+xml")}

        response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 413
        data = response.json()

        assert data["success"] is False
        assert data["data"] is None
        assert "error" in data

        error = data["error"]
        assert error["code"] == "FILE_TOO_LARGE"
        assert "demasiado grande" in error["message"].lower()
        assert "10mb" in error["message"].lower()
        assert error["field"] == "file"

    async def test_analyze_gpx_no_file_uploaded(self, client: AsyncClient, auth_headers: dict):
        """
        Test error handling when no file is uploaded.

        Given: Empty request body (no file field)
        When: POST /gpx/analyze
        Then: Returns 400 with validation error
        """
        response = await client.post("/gpx/analyze", headers=auth_headers)

        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["data"] is None
        assert "error" in data

    async def test_analyze_gpx_unauthorized(self, client: AsyncClient):
        """
        Test authentication requirement for endpoint.

        Contract: lines 132-145 (401 response noToken example)

        Given: No authentication token
        When: POST /gpx/analyze
        Then: Returns 401 with UNAUTHORIZED error
        """
        # Create minimal valid GPX
        gpx_content = io.BytesIO(
            b"""<?xml version="1.0"?>
        <gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">
            <trk>
                <trkseg>
                    <trkpt lat="40.416775" lon="-3.703790"></trkpt>
                </trkseg>
            </trk>
        </gpx>"""
        )
        files = {"file": ("test.gpx", gpx_content, "application/gpx+xml")}

        response = await client.post("/gpx/analyze", files=files)

        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["data"] is None
        assert "error" in data

        error = data["error"]
        assert error["code"] == "UNAUTHORIZED"

    async def test_analyze_gpx_performance(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test performance requirement: <2s for files up to 10MB.

        Contract: lines 43 (Performance note)

        Given: Large GPX file (~5MB)
        When: POST /gpx/analyze with file
        Then: Response time <2 seconds
        """
        import time

        gpx_file_path = gpx_fixtures_dir / "long_route_5mb.gpx"

        # Skip test if fixture doesn't exist
        if not gpx_file_path.exists():
            pytest.skip(f"Large GPX fixture not found: {gpx_file_path}")

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("long_route.gpx", f, "application/gpx+xml")}

            start_time = time.perf_counter()
            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)
            elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Performance assertion: <2 seconds
        assert elapsed_time < 2.0, f"Performance requirement failed: {elapsed_time:.2f}s (max 2s)"
