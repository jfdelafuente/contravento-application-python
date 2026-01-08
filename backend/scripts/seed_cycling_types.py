#!/usr/bin/env python3
"""
Seed cycling types from YAML configuration.

Loads cycling types from config/cycling_types.yaml and inserts them into the database.
Can be run multiple times safely - will skip existing types and update if needed.

Usage:
    poetry run python scripts/seed_cycling_types.py
    poetry run python scripts/seed_cycling_types.py --force  # Force update existing
"""

import asyncio
import sys
from pathlib import Path

import yaml

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.models.cycling_type import CyclingType


async def load_cycling_types_from_yaml(yaml_path: Path) -> list[dict]:
    """
    Load cycling types from YAML configuration file.

    Args:
        yaml_path: Path to YAML file

    Returns:
        List of cycling type dictionaries

    Raises:
        FileNotFoundError: If YAML file not found
        yaml.YAMLError: If YAML parsing fails
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Cycling types YAML not found: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "cycling_types" not in data:
        raise ValueError("Invalid YAML format: 'cycling_types' key not found")

    return data["cycling_types"]


async def seed_cycling_types(force: bool = False) -> None:
    """
    Seed cycling types into database from YAML configuration.

    Args:
        force: If True, update existing types with new data from YAML
    """
    # Load YAML configuration
    yaml_path = backend_dir / "config" / "cycling_types.yaml"
    print(f"Loading cycling types from: {yaml_path}")

    try:
        cycling_types_data = await load_cycling_types_from_yaml(yaml_path)
        print(f"Found {len(cycling_types_data)} cycling types in YAML")
    except Exception as e:
        print(f"Error loading YAML: {e}")
        sys.exit(1)

    # Connect to database
    async with AsyncSessionLocal() as db:
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for ct_data in cycling_types_data:
            code = ct_data["code"]
            display_name = ct_data["display_name"]
            description = ct_data.get("description")
            is_active = ct_data.get("is_active", True)

            # Check if cycling type already exists
            result = await db.execute(select(CyclingType).where(CyclingType.code == code))
            existing = result.scalar_one_or_none()

            if existing:
                if force:
                    # Update existing
                    existing.display_name = display_name
                    existing.description = description
                    existing.is_active = is_active
                    updated_count += 1
                    print(f"  ✓ Updated: {code}")
                else:
                    # Skip existing
                    skipped_count += 1
                    print(f"  - Skipped (exists): {code}")
            else:
                # Create new
                new_type = CyclingType(
                    code=code,
                    display_name=display_name,
                    description=description,
                    is_active=is_active,
                )
                db.add(new_type)
                created_count += 1
                print(f"  + Created: {code}")

        # Commit all changes
        await db.commit()

        # Summary
        print("\n" + "=" * 50)
        print("Cycling Types Seeding Complete")
        print("=" * 50)
        print(f"Created:  {created_count}")
        print(f"Updated:  {updated_count}")
        print(f"Skipped:  {skipped_count}")
        print(f"Total:    {created_count + updated_count + skipped_count}")


async def list_cycling_types() -> None:
    """
    List all cycling types in database.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CyclingType).order_by(CyclingType.is_active.desc(), CyclingType.display_name)
        )
        cycling_types = result.scalars().all()

        if not cycling_types:
            print("No cycling types found in database.")
            return

        print("\n" + "=" * 70)
        print("Current Cycling Types in Database")
        print("=" * 70)
        print(f"{'Code':<20} {'Display Name':<25} {'Active':<8} {'Description'}")
        print("-" * 70)

        for ct in cycling_types:
            status = "Yes" if ct.is_active else "No"
            desc = (ct.description or "")[:30] + "..." if ct.description else ""
            print(f"{ct.code:<20} {ct.display_name:<25} {status:<8} {desc}")

        print("-" * 70)
        print(f"Total: {len(cycling_types)} types")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed cycling types from YAML configuration")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update existing types with YAML data",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current cycling types in database",
    )

    args = parser.parse_args()

    if args.list:
        asyncio.run(list_cycling_types())
    else:
        print("=" * 50)
        print("Seeding Cycling Types")
        print("=" * 50)
        asyncio.run(seed_cycling_types(force=args.force))
        print("\nRun with --list to see current database state")


if __name__ == "__main__":
    main()
