#!/usr/bin/env python
"""
Test PostgreSQL connection before running migrations.
Usage: python scripts/test-postgres-connection.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


async def test_connection():
    """Test PostgreSQL connection using asyncpg directly."""

    print("🔍 Testing PostgreSQL Connection")
    print("=" * 50)
    print(f"DATABASE_URL: {settings.database_url}")
    print()

    # Parse connection string
    import re
    match = re.match(
        r'postgresql\+asyncpg://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)',
        settings.database_url
    )

    if not match:
        print("❌ Invalid DATABASE_URL format")
        print("Expected: postgresql+asyncpg://user:password@host:port/database")
        return False

    user, password, host, port, database = match.groups()

    print(f"User: {user}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print()

    # Test basic socket connection
    print("Step 1: Testing socket connection...")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, int(port)))
        sock.close()

        if result == 0:
            print(f"✅ Socket connection to {host}:{port} successful")
        else:
            print(f"❌ Socket connection failed (error code: {result})")
            print(f"   Make sure PostgreSQL container is running:")
            print(f"   docker-compose up -d postgres")
            return False
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print(f"   Try using 127.0.0.1 instead of localhost in DATABASE_URL")
        return False
    except Exception as e:
        print(f"❌ Socket connection error: {e}")
        return False

    print()

    # Test asyncpg connection
    print("Step 2: Testing asyncpg connection...")
    try:
        import asyncpg

        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=int(port),
            database=database,
            timeout=10
        )

        # Test query
        version = await conn.fetchval('SELECT version()')
        await conn.close()

        print("✅ PostgreSQL connection successful!")
        print(f"   Version: {version.split(',')[0]}")
        return True

    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ Authentication failed - wrong password")
        print(f"   Check password in .env matches docker-compose.yml")
        print(f"   Default: changeme_in_production")
        return False
    except asyncpg.exceptions.InvalidCatalogNameError:
        print(f"❌ Database '{database}' does not exist")
        print(f"   The container should create it automatically")
        print(f"   Try recreating: docker-compose down -v && docker-compose up -d postgres")
        return False
    except ConnectionRefusedError:
        print(f"❌ Connection refused on {host}:{port}")
        print(f"   PostgreSQL is not listening on this port")
        print(f"   Check: docker ps | grep contravento-db")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
        return False


async def main():
    """Run connection test."""
    print()
    success = await test_connection()
    print()
    print("=" * 50)

    if success:
        print("✅ All checks passed! You can now run:")
        print("   poetry run alembic upgrade head")
        sys.exit(0)
    else:
        print("❌ Connection test failed")
        print()
        print("🔧 Troubleshooting steps:")
        print("1. Check if PostgreSQL container is running:")
        print("   docker ps | grep contravento-db")
        print()
        print("2. If not running, start it:")
        print("   docker-compose up -d postgres")
        print()
        print("3. Check container logs:")
        print("   docker logs contravento-db")
        print()
        print("4. Verify port mapping:")
        print("   docker port contravento-db")
        print()
        print("5. Try connecting manually:")
        print(f"   docker exec -it contravento-db psql -U contravento_user -d contravento")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
