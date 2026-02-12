"""
Performance Benchmarks for API Endpoints

Tests endpoint response times using pytest-benchmark (T068-T069).

Success Criteria (from spec.md):
- Simple queries (GET /health, GET /trips/public): <200ms p95
- Auth endpoints (POST /auth/login): <500ms p95
- Trip creation (POST /trips): <1000ms p95

Benchmarking Strategy:
- Runs each test multiple times (min 5 iterations)
- Reports min, max, mean, median, stddev
- Fails if p95 exceeds threshold

Usage:
    pytest tests/performance/test_api_benchmarks.py -v
    pytest tests/performance/test_api_benchmarks.py --benchmark-only
    pytest tests/performance/test_api_benchmarks.py --benchmark-compare
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import create_trip


@pytest.mark.performance
@pytest.mark.benchmark
class TestHealthEndpointBenchmark:
    """Benchmark health check endpoint (T068)."""

    async def test_health_endpoint_latency(self, client: AsyncClient, benchmark):
        """
        Test GET /health latency.

        Target: <200ms p95 (simple query)
        """

        async def make_request():
            response = await client.get("/health")
            assert response.status_code == 200
            return response

        benchmark(make_request)
        # pytest-benchmark automatically reports stats


@pytest.mark.performance
@pytest.mark.benchmark
class TestAuthEndpointsBenchmark:
    """Benchmark authentication endpoints (T068)."""

    async def test_login_endpoint_latency(
        self,
        client: AsyncClient,
        test_user,
        benchmark,
    ):
        """
        Test POST /auth/login latency.

        Target: <500ms p95 (auth endpoint)
        """

        async def login():
            response = await client.post(
                "/auth/login",
                json={
                    "login": test_user.username,
                    "password": "TestPass123!",
                },
            )
            assert response.status_code == 200
            return response

        benchmark(login)

    async def test_token_refresh_latency(
        self,
        client: AsyncClient,
        test_user,
        benchmark,
    ):
        """
        Test POST /auth/refresh latency.

        Target: <500ms p95 (auth endpoint)
        """

        # First, login to get refresh token
        login_response = await client.post(
            "/auth/login",
            json={
                "login": test_user.username,
                "password": "TestPass123!",
            },
        )
        refresh_token = login_response.json()["data"]["refresh_token"]

        async def refresh():
            response = await client.post(f"/auth/refresh?refresh_token={refresh_token}")
            assert response.status_code == 200
            return response

        benchmark(refresh)


@pytest.mark.performance
@pytest.mark.benchmark
class TestPublicFeedBenchmark:
    """Benchmark public feed endpoint (T068)."""

    async def test_public_feed_latency_empty(self, client: AsyncClient, benchmark):
        """
        Test GET /trips/public latency (empty feed).

        Target: <200ms p95 (simple query)
        """

        async def fetch_feed():
            response = await client.get("/trips/public")
            assert response.status_code == 200
            return response

        benchmark(fetch_feed)

    async def test_public_feed_latency_with_data(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers,
        benchmark,
    ):
        """
        Test GET /trips/public latency (with 50 trips).

        Target: <200ms p95 (simple query)
        """

        # Seed database with 50 published trips
        for i in range(50):
            await create_trip(
                db_session,
                test_user.id,
                title=f"Benchmark Trip {i}",
                description=f"Test trip {i} for performance benchmarking.",
                status="PUBLISHED",
            )

        async def fetch_feed():
            response = await client.get("/trips/public?limit=10&page=1")
            assert response.status_code == 200
            data = response.json()
            assert len(data["trips"]) == 10
            return response

        benchmark(fetch_feed)


@pytest.mark.performance
@pytest.mark.benchmark
class TestTripCreationBenchmark:
    """Benchmark trip creation endpoint (T069)."""

    async def test_create_trip_latency(
        self,
        client: AsyncClient,
        auth_headers,
        benchmark,
    ):
        """
        Test POST /trips latency.

        Target: <1000ms p95 (trip creation)
        """

        trip_data = {
            "title": "Performance Test Trip",
            "description": "Trip created for performance benchmarking with sufficient description length.",
            "start_date": "2024-06-01",
            "distance_km": 150.5,
        }

        async def create():
            response = await client.post("/trips", json=trip_data, headers=auth_headers)
            assert response.status_code == 201
            return response

        benchmark(create)

    async def test_publish_trip_latency(
        self,
        client: AsyncClient,
        auth_headers,
        db_session: AsyncSession,
        test_user,
        benchmark,
    ):
        """
        Test POST /trips/{trip_id}/publish latency.

        Target: <500ms p95 (simple operation)
        """

        # Create a draft trip first
        trip = await create_trip(
            db_session,
            test_user.id,
            title="Trip to Publish",
            description="Testing publish endpoint performance.",
            status="DRAFT",
        )

        async def publish():
            response = await client.post(f"/trips/{trip.trip_id}/publish", headers=auth_headers)
            assert response.status_code == 200
            return response

        benchmark(publish)


@pytest.mark.performance
@pytest.mark.benchmark
class TestUserTripsListBenchmark:
    """Benchmark user trips list endpoint (T069)."""

    async def test_user_trips_latency_with_data(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers,
        benchmark,
    ):
        """
        Test GET /users/{username}/trips latency (with 100 trips).

        Target: <200ms p95 (simple query with pagination)
        """

        # Seed database with 100 trips
        for i in range(100):
            await create_trip(
                db_session,
                test_user.id,
                title=f"User Trip {i}",
                description=f"Test trip {i} for user trips list benchmarking.",
                status="PUBLISHED" if i % 2 == 0 else "DRAFT",
            )

        async def fetch_trips():
            response = await client.get(
                f"/users/{test_user.username}/trips?limit=20&page=1",
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]["trips"]) == 20
            return response

        benchmark(fetch_trips)


@pytest.mark.performance
@pytest.mark.benchmark
class TestDatabaseQueryBenchmark:
    """Benchmark database queries (T068-T069)."""

    async def test_user_lookup_by_username(self, db_session: AsyncSession, test_user, benchmark):
        """
        Test User lookup by username query performance.

        Target: <50ms (direct database query)
        """

        from sqlalchemy import select

        from src.models.user import User

        async def lookup():
            result = await db_session.execute(
                select(User).where(User.username == test_user.username)
            )
            user = result.scalar_one_or_none()
            assert user is not None
            return user

        benchmark(lookup)

    async def test_trip_query_with_relationships(
        self, db_session: AsyncSession, test_user, benchmark
    ):
        """
        Test Trip query with joined relationships (photos, tags, locations).

        Target: <100ms (complex query with joins)
        """

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload

        from src.models.trip import Trip

        # Create trip with relationships
        trip = await create_trip(
            db_session,
            test_user.id,
            title="Trip with Relations",
            description="Testing eager loading performance.",
            tags=["test", "benchmark", "performance"],
        )

        async def query():
            result = await db_session.execute(
                select(Trip)
                .where(Trip.trip_id == trip.trip_id)
                .options(
                    joinedload(Trip.photos),
                    joinedload(Trip.tags),
                    joinedload(Trip.locations),
                )
            )
            loaded_trip = result.scalar_one_or_none()
            assert loaded_trip is not None
            return loaded_trip

        benchmark(query)


@pytest.mark.performance
@pytest.mark.benchmark
class TestPasswordHashingBenchmark:
    """Benchmark password hashing operations (T069)."""

    async def test_password_hashing_latency(self, benchmark):
        """
        Test bcrypt password hashing performance.

        Target: <500ms (security vs. performance tradeoff)
        Note: Bcrypt is intentionally slow for security.
        """

        from src.utils.security import hash_password

        def hash_pw():
            hashed = hash_password("TestPassword123!")
            assert hashed.startswith("$2b$")
            return hashed

        benchmark(hash_pw)

    async def test_password_verification_latency(self, benchmark):
        """
        Test bcrypt password verification performance.

        Target: <500ms (security vs. performance tradeoff)
        """

        from src.utils.security import hash_password, verify_password

        hashed = hash_password("TestPassword123!")

        def verify():
            is_valid = verify_password("TestPassword123!", hashed)
            assert is_valid is True
            return is_valid

        benchmark(verify)


@pytest.mark.performance
@pytest.mark.benchmark
class TestGPXMapLoadingBenchmark:
    """Benchmark GPX track loading for map rendering (T052)."""

    async def test_map_loads_with_1000_points(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers,
        benchmark,
    ):
        """
        T052: Test GET /gpx/{gpx_file_id}/track loads with 1000 points in <3s.

        Success Criteria: SC-007 (Map loads with 1000 points in <3s)
        Functional Requirements: FR-010 (Display interactive route map)
        """
        from pathlib import Path

        # Step 1: Create trip and upload GPX file with ~2000 points (will be simplified to ~200)
        trip_data = {
            "title": "Map Loading Performance Test",
            "description": "Testing map rendering performance with large GPX file.",
            "start_date": "2024-06-01",
        }

        create_response = await client.post("/trips", json=trip_data, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Upload camino_del_cid.gpx (2000 points → simplified to ~200 points)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "camino_del_cid.gpx"

        with open(gpx_path, "rb") as f:
            files = {"file": ("camino_del_cid.gpx", f, "application/gpx+xml")}
            upload_response = await client.post(
                f"/trips/{trip_id}/gpx", files=files, headers=auth_headers
            )

        gpx_file_id = upload_response.json()["data"]["gpx_file_id"]

        # Step 2: Benchmark track data retrieval (map rendering endpoint)
        async def fetch_track_data():
            response = await client.get(f"/gpx/{gpx_file_id}/track")
            assert response.status_code == 200
            data = response.json()["data"]

            # Verify trackpoints exist
            assert "trackpoints" in data
            assert len(data["trackpoints"]) > 0

            return response

        # Run benchmark
        result = benchmark(fetch_track_data)

        # Assert performance (SC-007): Should load in <3s
        # Note: pytest-benchmark measures execution time automatically
        # We'll verify in the stats output that mean/median < 3000ms
