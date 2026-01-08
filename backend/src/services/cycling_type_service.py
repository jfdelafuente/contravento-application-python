"""
CyclingType service layer.

Business logic for managing cycling types.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cycling_type import CyclingType
from src.schemas.cycling_type import (
    CyclingTypeCreateRequest,
    CyclingTypePublicResponse,
    CyclingTypeResponse,
    CyclingTypeUpdateRequest,
)

logger = logging.getLogger(__name__)


class CyclingTypeService:
    """
    Service for managing cycling types.

    Handles CRUD operations for cycling types stored in database.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session.

        Args:
            db: Database session
        """
        self.db = db

    async def get_all(self, active_only: bool = False) -> list[CyclingTypeResponse]:
        """
        Get all cycling types.

        Args:
            active_only: If True, only return active types

        Returns:
            List of cycling types
        """
        query = select(CyclingType).order_by(CyclingType.display_name)

        if active_only:
            query = query.where(CyclingType.is_active == True)  # noqa: E712

        result = await self.db.execute(query)
        cycling_types = result.scalars().all()

        return [CyclingTypeResponse.model_validate(ct) for ct in cycling_types]

    async def get_all_public(self) -> list[CyclingTypePublicResponse]:
        """
        Get all active cycling types (public endpoint).

        Returns only active types with simplified response.

        Returns:
            List of active cycling types (public format)
        """
        query = (
            select(CyclingType)
            .where(CyclingType.is_active == True)  # noqa: E712
            .order_by(CyclingType.display_name)
        )

        result = await self.db.execute(query)
        cycling_types = result.scalars().all()

        return [CyclingTypePublicResponse.model_validate(ct) for ct in cycling_types]

    async def get_by_code(self, code: str) -> Optional[CyclingTypeResponse]:
        """
        Get cycling type by code.

        Args:
            code: Cycling type code

        Returns:
            CyclingTypeResponse if found, None otherwise
        """
        query = select(CyclingType).where(CyclingType.code == code.lower())
        result = await self.db.execute(query)
        cycling_type = result.scalar_one_or_none()

        if not cycling_type:
            return None

        return CyclingTypeResponse.model_validate(cycling_type)

    async def create(self, data: CyclingTypeCreateRequest) -> CyclingTypeResponse:
        """
        Create a new cycling type.

        Args:
            data: Cycling type creation data

        Returns:
            Created cycling type

        Raises:
            ValueError: If code already exists
        """
        # Check if code already exists
        existing = await self.get_by_code(data.code)
        if existing:
            raise ValueError(f"Ya existe un tipo de ciclismo con el código '{data.code}'")

        # Create new cycling type
        cycling_type = CyclingType(
            code=data.code.lower(),
            display_name=data.display_name,
            description=data.description,
            is_active=data.is_active,
        )

        self.db.add(cycling_type)
        await self.db.commit()
        await self.db.refresh(cycling_type)

        logger.info(f"Created cycling type: {cycling_type.code}")

        return CyclingTypeResponse.model_validate(cycling_type)

    async def update(self, code: str, data: CyclingTypeUpdateRequest) -> CyclingTypeResponse:
        """
        Update an existing cycling type.

        Args:
            code: Cycling type code to update
            data: Update data

        Returns:
            Updated cycling type

        Raises:
            ValueError: If cycling type not found
        """
        # Get existing cycling type
        query = select(CyclingType).where(CyclingType.code == code.lower())
        result = await self.db.execute(query)
        cycling_type = result.scalar_one_or_none()

        if not cycling_type:
            raise ValueError(f"No se encontró el tipo de ciclismo '{code}'")

        # Update fields if provided
        if data.display_name is not None:
            cycling_type.display_name = data.display_name

        if data.description is not None:
            cycling_type.description = data.description

        if data.is_active is not None:
            cycling_type.is_active = data.is_active

        await self.db.commit()
        await self.db.refresh(cycling_type)

        logger.info(f"Updated cycling type: {cycling_type.code}")

        return CyclingTypeResponse.model_validate(cycling_type)

    async def delete(self, code: str, soft: bool = True) -> None:
        """
        Delete a cycling type.

        Args:
            code: Cycling type code to delete
            soft: If True, soft delete (set is_active=False), otherwise hard delete

        Raises:
            ValueError: If cycling type not found
        """
        # Get existing cycling type
        query = select(CyclingType).where(CyclingType.code == code.lower())
        result = await self.db.execute(query)
        cycling_type = result.scalar_one_or_none()

        if not cycling_type:
            raise ValueError(f"No se encontró el tipo de ciclismo '{code}'")

        if soft:
            # Soft delete - set is_active to False
            cycling_type.is_active = False
            await self.db.commit()
            logger.info(f"Soft deleted cycling type: {cycling_type.code}")
        else:
            # Hard delete - remove from database
            await self.db.delete(cycling_type)
            await self.db.commit()
            logger.info(f"Hard deleted cycling type: {code}")

    async def get_active_codes(self) -> set[str]:
        """
        Get set of all active cycling type codes.

        Used by validators to check if a cycling type is valid.

        Returns:
            Set of active cycling type codes (lowercase)
        """
        query = select(CyclingType.code).where(CyclingType.is_active == True)  # noqa: E712
        result = await self.db.execute(query)
        codes = result.scalars().all()

        return set(codes)
