"""
Database configuration and session management.

Provides async SQLAlchemy engine and session factory for both SQLite and PostgreSQL.
Includes SQLite foreign key pragma handler per data-model.md.
"""

from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, StaticPool

from src.config import settings


# Base class for all ORM models
Base = declarative_base()


# Configure engine based on database type
def _get_engine_kwargs() -> dict:
    """Get engine configuration based on database type."""
    if settings.database_is_sqlite:
        # SQLite configuration
        if ":memory:" in settings.database_url:
            # In-memory database (testing)
            return {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,  # Single connection, no pooling
                "echo": settings.debug,
            }
        else:
            # File-based database (development)
            return {
                "connect_args": {"check_same_thread": False},
                "poolclass": NullPool,  # No pooling for SQLite
                "echo": settings.debug,
            }
    else:
        # PostgreSQL configuration (production)
        return {
            "pool_size": 20,  # Base connections
            "max_overflow": 10,  # Additional under load
            "pool_pre_ping": True,  # Verify connections
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "echo": settings.debug,
        }


# Create async engine
engine = create_async_engine(
    settings.database_url,
    **_get_engine_kwargs()
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# SQLite foreign key pragma handler (per data-model.md)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record) -> None:
    """
    Enable foreign key constraints for SQLite.

    SQLite has foreign keys disabled by default. This handler enables them
    for every new connection to ensure referential integrity.

    Reference: specs/001-user-profiles/data-model.md
    """
    # Check if this is a SQLite connection
    if "sqlite" in str(type(dbapi_conn)).lower():
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide database session.

    Yields an async database session and ensures proper cleanup.
    Use with FastAPI Depends() for automatic session management.

    Example:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in Base metadata.
    Only used for testing - production uses Alembic migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all database tables.

    Only used for testing cleanup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
