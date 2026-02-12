"""
Contract tests for GPX Wizard API (Feature 017 - US2).

Validates that GPX wizard endpoint responses match the OpenAPI specification
defined in specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml.

Test Coverage:
- POST /gpx/analyze response schemas
- Error response schemas (400, 401, 413)
- Field validation and types
"""

import io
from pathlib import Path

import pytest
from httpx import AsyncClient


@pytest.mark.contract
@pytest.mark.asyncio
class TestGPXAnalyzeContract:
    """Contract tests for POST /gpx/analyze endpoint."""

    @pytest.fixture
    def gpx_fixtures_dir(self) -> Path:
        """Path to GPX test fixtures directory."""
        return Path(__file__).parent.parent / "fixtures" / "gpx"

    async def test_analyze_gpx_success_response_schema(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test POST /gpx/analyze success response matches GPXAnalysisResponse schema.

        Contract: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml lines 71-116

        Schema validation:
        - success: boolean (true)
        - data: GPXTelemetry object
        - error: null
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        # Validate status code
        assert response.status_code == 200

        data = response.json()

        # Validate top-level response structure
        assert "success" in data
        assert "data" in data
        assert "error" in data

        # Validate field types
        assert isinstance(data["success"], bool)
        assert isinstance(data["data"], dict)
        assert data["error"] is None

        # Validate success value
        assert data["success"] is True

    async def test_analyze_gpx_telemetry_schema_with_elevation(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test GPXTelemetry schema fields with elevation data.

        Contract: GPXTelemetry schema (components/schemas/GPXTelemetry)

        Required fields:
        - distance_km: number (≥0)
        - elevation_gain: number (≥0) or null
        - elevation_loss: number (≥0) or null
        - max_elevation: number or null
        - min_elevation: number or null
        - has_elevation: boolean
        - difficulty: string (enum: easy, moderate, difficult, very_difficult)
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 200
        data = response.json()
        telemetry = data["data"]

        # Validate required fields exist
        assert "distance_km" in telemetry
        assert "elevation_gain" in telemetry
        assert "elevation_loss" in telemetry
        assert "max_elevation" in telemetry
        assert "min_elevation" in telemetry
        assert "has_elevation" in telemetry
        assert "difficulty" in telemetry

        # Validate field types
        assert isinstance(telemetry["distance_km"], int | float)
        assert telemetry["elevation_gain"] is None or isinstance(
            telemetry["elevation_gain"], int | float
        )
        assert telemetry["elevation_loss"] is None or isinstance(
            telemetry["elevation_loss"], int | float
        )
        assert telemetry["max_elevation"] is None or isinstance(
            telemetry["max_elevation"], int | float
        )
        assert telemetry["min_elevation"] is None or isinstance(
            telemetry["min_elevation"], int | float
        )
        assert isinstance(telemetry["has_elevation"], bool)
        assert isinstance(telemetry["difficulty"], str)

        # Validate field constraints
        assert telemetry["distance_km"] >= 0
        if telemetry["elevation_gain"] is not None:
            assert telemetry["elevation_gain"] >= 0
        if telemetry["elevation_loss"] is not None:
            assert telemetry["elevation_loss"] >= 0

        # Validate difficulty enum
        assert telemetry["difficulty"] in ["easy", "moderate", "difficult", "very_difficult"]

    async def test_analyze_gpx_telemetry_schema_without_elevation(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test GPXTelemetry schema for GPX files without elevation data.

        Elevation fields should be null when has_elevation is false.
        """
        gpx_file_path = gpx_fixtures_dir / "no_elevation.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("no_elevation.gpx", f, "application/gpx+xml")}
            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 200
        data = response.json()
        telemetry = data["data"]

        # Validate has_elevation is false
        assert telemetry["has_elevation"] is False

        # Elevation fields should be null
        assert telemetry["elevation_gain"] is None
        assert telemetry["elevation_loss"] is None
        assert telemetry["max_elevation"] is None
        assert telemetry["min_elevation"] is None

        # Distance and difficulty should still be present
        assert telemetry["distance_km"] >= 0
        assert telemetry["difficulty"] in ["easy", "moderate", "difficult", "very_difficult"]

    async def test_analyze_gpx_error_response_invalid_file_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test 400 error response schema for invalid file type.

        Contract: lines 122-130 (invalidFileType example)

        Error schema:
        - success: false
        - data: null
        - error: {code, message, field}
        """
        # Upload non-GPX file (fake JPEG)
        fake_jpeg = io.BytesIO(b"\xff\xd8\xff\xe0JFIF")
        files = {"file": ("photo.jpg", fake_jpeg, "image/jpeg")}

        response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        # Validate status code
        assert response.status_code == 400

        data = response.json()

        # Validate error response structure
        assert "success" in data
        assert "data" in data
        assert "error" in data

        # Validate field types
        assert isinstance(data["success"], bool)
        assert data["data"] is None
        assert isinstance(data["error"], dict)

        # Validate error object fields
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "field" in error

        # Validate error field types
        assert isinstance(error["code"], str)
        assert isinstance(error["message"], str)
        assert isinstance(error["field"], str)

        # Validate error values
        assert data["success"] is False
        assert error["code"] == "INVALID_FILE_TYPE"
        assert error["field"] == "file"

    async def test_analyze_gpx_error_response_corrupted_file(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test 400 error response schema for corrupted GPX file.

        Contract: lines 132-140 (corruptedGpx example)

        Error code should be INVALID_GPX_FILE.
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

        # Validate status code
        assert response.status_code == 400

        data = response.json()

        # Validate error response structure
        assert data["success"] is False
        assert data["data"] is None
        assert isinstance(data["error"], dict)

        # Validate error code
        error = data["error"]
        assert error["code"] == "INVALID_GPX_FILE"
        assert isinstance(error["message"], str)

    async def test_analyze_gpx_error_response_file_too_large(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test 413 error response schema for file exceeding size limit.

        Contract: lines 142-150 (fileTooLarge example)

        Status: 413 Request Entity Too Large
        Error code: FILE_TOO_LARGE
        """
        # Create file larger than 10MB (10 * 1024 * 1024 bytes)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("huge.gpx", io.BytesIO(large_content), "application/gpx+xml")}

        response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        # Validate status code
        assert response.status_code == 413

        data = response.json()

        # Validate error response structure
        assert data["success"] is False
        assert data["data"] is None
        assert isinstance(data["error"], dict)

        # Validate error code
        error = data["error"]
        assert error["code"] == "FILE_TOO_LARGE"
        assert error["field"] == "file"

    async def test_analyze_gpx_requires_authentication(
        self, client: AsyncClient, gpx_fixtures_dir: Path
    ):
        """
        Test 401 error response for unauthenticated request.

        Contract: lines 152-159 (unauthorized example)

        Status: 401 Unauthorized
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            # No auth headers
            response = await client.post("/gpx/analyze", files=files)

        # Validate status code
        assert response.status_code == 401

        data = response.json()

        # Should have error information
        assert "error" in data or "detail" in data

    async def test_analyze_gpx_missing_file_parameter(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test 400 error response when file parameter is missing.

        Contract: implied by required file parameter

        Error code: MISSING_FILE
        """
        # No files parameter
        response = await client.post("/gpx/analyze", headers=auth_headers)

        # Validate status code (422 for missing required field)
        assert response.status_code in [400, 422]

    async def test_analyze_gpx_response_content_type(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test response Content-Type header is application/json.

        Contract: lines 73-74 (content type)
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 200

        # Validate Content-Type header
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type.lower()

    async def test_analyze_gpx_distance_precision(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test distance_km field has appropriate precision (≤2 decimal places).

        Contract: distance_km should be rounded to 2 decimal places
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 200
        data = response.json()
        distance_km = data["data"]["distance_km"]

        # Check precision (≤2 decimal places)
        # Convert to string and count decimals
        distance_str = str(distance_km)
        if "." in distance_str:
            decimals = len(distance_str.split(".")[-1])
            assert decimals <= 2, f"Distance has {decimals} decimals, expected ≤2"

    async def test_analyze_gpx_elevation_precision(
        self, client: AsyncClient, auth_headers: dict, gpx_fixtures_dir: Path
    ):
        """
        Test elevation fields have appropriate precision (≤1 decimal place).

        Contract: elevation fields should be rounded to 1 decimal place
        """
        gpx_file_path = gpx_fixtures_dir / "short_route.gpx"

        with open(gpx_file_path, "rb") as f:
            files = {"file": ("short_route.gpx", f, "application/gpx+xml")}
            response = await client.post("/gpx/analyze", headers=auth_headers, files=files)

        assert response.status_code == 200
        data = response.json()
        telemetry = data["data"]

        # Check precision for non-null elevation fields
        elevation_fields = [
            "elevation_gain",
            "elevation_loss",
            "max_elevation",
            "min_elevation",
        ]

        for field in elevation_fields:
            value = telemetry[field]
            if value is not None:
                value_str = str(value)
                if "." in value_str:
                    decimals = len(value_str.split(".")[-1])
                    assert decimals <= 1, f"{field} has {decimals} decimals, expected ≤1"
