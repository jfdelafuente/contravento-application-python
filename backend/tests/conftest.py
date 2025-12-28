"""
Pytest configuration and fixtures.

Provides test fixtures for database, async client, authentication, and test data.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.main import app


# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


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
    Provide authentication headers with a valid JWT token.

    Creates a test user, generates token, and returns headers for authenticated requests.

    Args:
        client: Async HTTP client
        db_session: Database session

    Returns:
        Dictionary with Authorization header

    Example:
        async def test_protected_endpoint(client, auth_headers):
            response = await client.get("/protected", headers=auth_headers)
            assert response.status_code == 200
    """
    from src.utils.security import create_access_token, hash_password
    from src.models.user import User, UserProfile

    # Create a test user in the database
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password=hash_password("TestPass123!"),
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


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for business logic")
    config.addinivalue_line("markers", "integration: Integration tests for API endpoints")
    config.addinivalue_line("markers", "contract: Contract tests for OpenAPI validation")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
