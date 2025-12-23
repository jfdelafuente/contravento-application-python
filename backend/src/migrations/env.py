"""
Alembic environment configuration.

Configures async migrations with dialect detection for SQLite vs PostgreSQL.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import the Base and settings
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import Base
from src.config import settings

# Import all models to ensure they're registered with Base
# This ensures all tables are included in autogenerate
from src.models.user import User, UserProfile
from src.models.auth import PasswordReset
# TODO: Uncomment as models are created
# from src.models.stats import UserStats, Achievement, UserAchievement
# from src.models.social import Follow
# from src.models.auth import PasswordReset

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = Base.metadata

# Override sqlalchemy.url with value from settings
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        # Detect dialect for SQLite vs PostgreSQL migrations
        render_as_batch="sqlite" in str(connection.engine.url),
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async engine.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    configuration = config.get_section(config.config_ini_section, {})

    # Override with settings
    configuration["sqlalchemy.url"] = settings.database_url

    # Configure connection pooling based on database type
    if settings.database_is_sqlite:
        # SQLite: No pooling
        configuration["poolclass"] = pool.NullPool
    else:
        # PostgreSQL: Connection pooling
        configuration["pool_pre_ping"] = True
        configuration["pool_size"] = 5
        configuration["max_overflow"] = 10

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Use NullPool for migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (async)."""
    asyncio.run(run_async_migrations())


# Determine if we're in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
