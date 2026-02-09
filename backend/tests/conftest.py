"""
Pytest configuration and fixtures.

Provides test fixtures for database, async client, authentication, and test data.

IMPORTANT: This module loads .env.test BEFORE any src.* imports to ensure
Settings() has environment variables available at instantiation time.
"""

import os
from pathlib import Path

# ========================================================================
# CRITICAL: Load test environment FIRST, before any src.* imports!
# ========================================================================
# This prevents "Field required" validation errors when Settings() is
# instantiated during module imports (src.main.app, src.database, etc.)
# ========================================================================
from dotenv import load_dotenv

# Get path to .env.test (backend/.env.test)
_env_file = Path(__file__).parent.parent / ".env.test"

if _env_file.exists():
    load_dotenv(_env_file, override=True)
    os.environ["APP_ENV"] = "testing"
else:
    # Fallback: set minimal test environment variables
    os.environ.setdefault("APP_ENV", "testing")
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
    os.environ.setdefault("BCRYPT_ROUNDS", "4")

# ========================================================================
# Now safe to import src.* modules (Settings() will have environment vars)
# ========================================================================

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import TYPE_CHECKING

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.main import app

if TYPE_CHECKING:
    from src.models.user import User

# Configure pytest-asyncio and load Feature 013 fixtures
pytest_plugins = ("pytest_asyncio", "tests.fixtures.feature_013_fixtures")


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """
    Verify test environment is configured correctly.

    Environment variables are now loaded at module level (before any src.* imports)
    to prevent Settings() validation errors. This fixture just validates the setup.
    """
    # Verify critical environment variables are set
    assert os.environ.get("APP_ENV") == "testing", "APP_ENV must be 'testing'"
    assert os.environ.get("SECRET_KEY"), "SECRET_KEY must be set"
    assert os.environ.get("DATABASE_URL"), "DATABASE_URL must be set"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for the test session.

    Yields:
        Event loop for async tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """
    Create a fresh in-memory SQLite database engine for each test.

    Returns:
        Async engine for testing
    """
    # Import Base here (after load_test_env has run)
    from src.database import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for testing.

    Each test gets a fresh in-memory database with automatic rollback.

    Args:
        db_engine: Test database engine

    Yields:
        Database session for the test

    Example:
        async def test_something(db_session):
            # Use db_session for database operations
            result = await db_session.execute(select(User))
            users = result.scalars().all()
    """
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for testing API endpoints.

    Overrides the get_db dependency to use the test database.

    Args:
        db_session: Test database session

    Yields:
        Async HTTP client

    Example:
        async def test_api_endpoint(client):
            response = await client.get("/health")
            assert response.status_code == 200
    """
    from src.api.deps import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def faker_instance() -> Faker:
    """
    Provide a Faker instance for generating test data.

    Returns:
        Faker instance

    Example:
        def test_something(faker_instance):
            email = faker_instance.email()
            username = faker_instance.user_name()
    """
    Faker.seed(42)  # Fixed seed for reproducible tests
    return Faker("es_ES")  # Spanish locale


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    """
    Provide authentication headers with a valid JWT token for an ADMIN user.

    Creates an admin test user, generates token, and returns headers for authenticated requests.
    Use this for testing admin-protected endpoints.

    Args:
        client: Async HTTP client
        db_session: Database session

    Returns:
        Dictionary with Authorization header

    Example:
        async def test_admin_endpoint(client, auth_headers):
            response = await client.post("/admin/cycling-types", headers=auth_headers, json={...})
            assert response.status_code == 201
    """
    from src.models.user import User, UserProfile, UserRole
    from src.utils.security import create_access_token, hash_password

    # Create an admin test user in the database
    user = User(
        username="admin_user",
        email="admin@example.com",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create profile for user
    profile = UserProfile(user_id=user.id)
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate token with actual user ID
    token = create_access_token({"sub": user.id, "username": user.username})

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def regular_user_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    """
    Provide authentication headers with a valid JWT token for a regular USER.

    Creates a regular test user, generates token, and returns headers for authenticated requests.
    Use this for testing that regular users cannot access admin endpoints.

    Args:
        client: Async HTTP client
        db_session: Database session

    Returns:
        Dictionary with Authorization header

    Example:
        async def test_regular_user_cannot_access_admin(client, regular_user_headers):
            response = await client.post("/admin/cycling-types", headers=regular_user_headers, json={...})
            assert response.status_code == 403
    """
    from src.models.user import User, UserProfile, UserRole
    from src.utils.security import create_access_token, hash_password

    # Create a regular test user in the database
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password=hash_password("TestPass123!"),
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create profile for user
    profile = UserProfile(user_id=user.id)
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate token with actual user ID
    token = create_access_token({"sub": user.id, "username": user.username})

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> "User":
    """
    Provide a test user instance for integration tests.

    Returns the same test user as auth_headers fixture but as a User object.
    Use this when tests need to access user properties (username, user_id, etc.).

    Args:
        db_session: Database session

    Returns:
        User instance

    Example:
        async def test_user_trips(client, auth_headers, test_user):
            response = await client.get(f"/users/{test_user.username}/trips", headers=auth_headers)
            assert response.status_code == 200
    """
    from sqlalchemy import select

    from src.models.user import User

    # Query the existing test user created by auth_headers fixture
    # If auth_headers fixture hasn't run yet, this will return None and we create the user
    result = await db_session.execute(select(User).where(User.username == "test_user"))
    user = result.scalar_one_or_none()

    if not user:
        # Create user if it doesn't exist (when test_user is used without auth_headers)
        from src.models.user import UserProfile, UserRole
        from src.utils.security import hash_password

        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password=hash_password("TestPass123!"),
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        # Create profile for user
        profile = UserProfile(user_id=user.id)
        db_session.add(profile)
        await db_session.commit()
        await db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def sample_user_data(faker_instance: Faker) -> dict:
    """
    Generate sample user data for testing.

    Args:
        faker_instance: Faker instance

    Returns:
        Dictionary with user data

    Example:
        def test_user_creation(sample_user_data):
            user = User(**sample_user_data)
            assert user.email == sample_user_data["email"]
    """
    return {
        "username": faker_instance.user_name().lower().replace(".", "_"),
        "email": faker_instance.email(),
        "password": "SecurePass123!",
        "full_name": faker_instance.name(),
    }


@pytest.fixture(scope="function")
def sample_profile_data(faker_instance: Faker) -> dict:
    """
    Generate sample profile data for testing.

    Args:
        faker_instance: Faker instance

    Returns:
        Dictionary with profile data

    Example:
        def test_profile_update(sample_profile_data):
            profile = UserProfile(**sample_profile_data)
            assert profile.bio == sample_profile_data["bio"]
    """
    return {
        "full_name": faker_instance.name(),
        "bio": faker_instance.text(max_nb_chars=200),
        "location": faker_instance.city() + ", " + faker_instance.country(),
        "cycling_type": faker_instance.random_element(
            ["road", "mountain", "gravel", "touring", "commuting"]
        ),
    }


@pytest.fixture(scope="function")
def fixtures_dir() -> Path:
    """
    Get path to test fixtures directory.

    Returns:
        Path: Absolute path to backend/tests/fixtures/

    Example:
        def test_load_fixture(fixtures_dir):
            users_file = fixtures_dir / "users.json"
            with open(users_file) as f:
                users = json.load(f)
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
def load_json_fixture(fixtures_dir):
    """
    Load JSON fixture file.

    Returns a function that loads JSON fixtures by filename.

    Args:
        fixtures_dir: Fixtures directory path fixture

    Returns:
        callable: Function that takes filename and returns parsed JSON

    Example:
        def test_users_fixture(load_json_fixture):
            users = load_json_fixture("users.json")
            assert len(users) > 0
    """
    import json

    def _load(filename: str):
        filepath = fixtures_dir / filename
        if not filepath.exists():
            return None
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)

    return _load


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for business logic")
    config.addinivalue_line("markers", "integration: Integration tests for API endpoints")
    config.addinivalue_line("markers", "contract: Contract tests for OpenAPI validation")
    config.addinivalue_line("markers", "e2e: End-to-end tests for full application")
    config.addinivalue_line("markers", "performance: Performance and load tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
