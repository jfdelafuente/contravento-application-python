#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Connectivity Checker for ContraVento Smoke Tests

Tests database connectivity for different deployment modes.

Usage:
    python scripts/check_db.py <mode>

Modes:
    local-dev      - SQLite local development
    local-minimal  - PostgreSQL minimal Docker
    local-full     - PostgreSQL full Docker
    staging        - PostgreSQL staging

Exit codes:
    0 - Database connection successful
    1 - Database connection failed
    2 - Invalid arguments or configuration
"""

import asyncio
import sys
import io
from pathlib import Path

# Force UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


async def check_sqlite(db_path: str) -> bool:
    """
    Check SQLite database connectivity.

    Args:
        db_path: Path to SQLite database file

    Returns:
        bool: True if connection successful
    """
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        # Create engine
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            echo=False,
        )

        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ SQLite connection successful")
                print(f"   Database: {db_path}")
                await engine.dispose()
                return True

        await engine.dispose()
        return False

    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
        return False


async def check_postgresql(connection_string: str) -> bool:
    """
    Check PostgreSQL database connectivity.

    Args:
        connection_string: PostgreSQL connection string

    Returns:
        bool: True if connection successful
    """
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        # Create engine
        engine = create_async_engine(
            connection_string,
            echo=False,
        )

        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()
            if version:
                print("✅ PostgreSQL connection successful")
                print(f"   Version: {version[0][:50]}...")
                await engine.dispose()
                return True

        await engine.dispose()
        return False

    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Error: Missing deployment mode", file=sys.stderr)
        print("", file=sys.stderr)
        print("Usage: python scripts/check_db.py <mode>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Modes:", file=sys.stderr)
        print("  local-dev      - SQLite local development", file=sys.stderr)
        print("  local-minimal  - PostgreSQL minimal Docker", file=sys.stderr)
        print("  local-full     - PostgreSQL full Docker", file=sys.stderr)
        print("  staging        - PostgreSQL staging", file=sys.stderr)
        sys.exit(2)

    mode = sys.argv[1]

    print(f"Checking database connectivity for mode: {mode}")
    print("")

    # Determine database connection based on mode
    if mode == "local-dev":
        # SQLite local development
        db_path = Path(__file__).parent.parent / "backend" / "contravento_dev.db"

        if not db_path.exists():
            print(f"❌ Database file not found: {db_path}")
            print("   Run './run-local-dev.sh --setup' to initialize the database")
            sys.exit(1)

        success = await check_sqlite(str(db_path))

    elif mode == "local-minimal":
        # PostgreSQL minimal Docker (port 5432)
        connection_string = "postgresql+asyncpg://contravento:contraventopass@localhost:5432/contravento_db"
        success = await check_postgresql(connection_string)

    elif mode == "local-full":
        # PostgreSQL full Docker (port 5432)
        connection_string = "postgresql+asyncpg://contravento:contraventopass@localhost:5432/contravento_db"
        success = await check_postgresql(connection_string)

    elif mode == "staging":
        # PostgreSQL staging (use environment variables or hardcoded staging URL)
        # TODO: Update with actual staging connection string
        connection_string = "postgresql+asyncpg://staging_user:staging_pass@staging.contravento.com:5432/contravento_staging"
        print("⚠️  Staging database check not fully configured")
        print("   Update connection string in check_db.py for staging environment")
        success = await check_postgresql(connection_string)

    else:
        print(f"Error: Invalid mode '{mode}'", file=sys.stderr)
        print("", file=sys.stderr)
        print("Valid modes: local-dev, local-minimal, local-full, staging", file=sys.stderr)
        sys.exit(2)

    # Exit with appropriate code
    if success:
        print("")
        print("Database connection successful")
        sys.exit(0)
    else:
        print("")
        print("Database connection failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
