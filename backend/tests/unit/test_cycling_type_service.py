"""
Unit tests for CyclingTypeService business logic.

Tests cycling type management service methods.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cycling_type import CyclingType
from src.schemas.cycling_type import (
    CyclingTypeCreateRequest,
    CyclingTypeUpdateRequest,
)
from src.services.cycling_type_service import CyclingTypeService


@pytest.mark.unit
@pytest.mark.asyncio
class TestCyclingTypeServiceGetAll:
    """Unit tests for CyclingTypeService.get_all()."""

    async def test_get_all_returns_all_types(self, db_session: AsyncSession):
        """Verify that get_all returns all cycling types when active_only=False."""
        # Arrange
        service = CyclingTypeService(db_session)

        # Create test types
        type1 = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        type2 = CyclingType(code="road", display_name="Road", is_active=True)
        type3 = CyclingType(code="gravel", display_name="Gravel", is_active=False)

        db_session.add_all([type1, type2, type3])
        await db_session.commit()

        # Act
        result = await service.get_all(active_only=False)

        # Assert
        assert len(result) == 3
        codes = {t.code for t in result}
        assert codes == {"mountain", "road", "gravel"}

    async def test_get_all_returns_only_active_types(self, db_session: AsyncSession):
        """Verify that get_all with active_only=True returns only active types."""
        # Arrange
        service = CyclingTypeService(db_session)

        type1 = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        type2 = CyclingType(code="road", display_name="Road", is_active=True)
        type3 = CyclingType(code="gravel", display_name="Gravel", is_active=False)

        db_session.add_all([type1, type2, type3])
        await db_session.commit()

        # Act
        result = await service.get_all(active_only=True)

        # Assert
        assert len(result) == 2
        codes = {t.code for t in result}
        assert codes == {"mountain", "road"}
        assert all(t.is_active for t in result)

    async def test_get_all_returns_empty_list_when_no_types(self, db_session: AsyncSession):
        """Verify that get_all returns empty list when no types exist."""
        # Arrange
        service = CyclingTypeService(db_session)

        # Act
        result = await service.get_all()

        # Assert
        assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
class TestCyclingTypeServiceGetAllPublic:
    """Unit tests for CyclingTypeService.get_all_public()."""

    async def test_get_all_public_returns_only_active_types(self, db_session: AsyncSession):
        """Verify that get_all_public returns only active types."""
        # Arrange
        service = CyclingTypeService(db_session)

        type1 = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        type2 = CyclingType(code="road", display_name="Road", is_active=False)

        db_session.add_all([type1, type2])
        await db_session.commit()

        # Act
        result = await service.get_all_public()

        # Assert
        assert len(result) == 1
        assert result[0].code == "mountain"
        assert result[0].display_name == "Mountain"


@pytest.mark.unit
@pytest.mark.asyncio
class TestCyclingTypeServiceGetByCode:
    """Unit tests for CyclingTypeService.get_by_code()."""

    async def test_get_by_code_returns_existing_type(self, db_session: AsyncSession):
        """Verify that get_by_code returns the correct cycling type."""
        # Arrange
        service = CyclingTypeService(db_session)

        cycling_type = CyclingType(
            code="mountain",
            display_name="Mountain Biking",
            description="Off-road cycling",
            is_active=True,
        )
        db_session.add(cycling_type)
        await db_session.commit()

        # Act
        result = await service.get_by_code("mountain")

        # Assert
        assert result is not None
        assert result.code == "mountain"
        assert result.display_name == "Mountain Biking"
        assert result.description == "Off-road cycling"
        assert result.is_active is True

    async def test_get_by_code_case_insensitive(self, db_session: AsyncSession):
        """Verify that get_by_code is case-insensitive."""
        # Arrange
        service = CyclingTypeService(db_session)

        cycling_type = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        db_session.add(cycling_type)
        await db_session.commit()

        # Act
        result = await service.get_by_code("MOUNTAIN")

        # Assert
        assert result is not None
        assert result.code == "mountain"

    async def test_get_by_code_returns_none_when_not_found(self, db_session: AsyncSession):
        """Verify that get_by_code returns None for non-existent code."""
        # Arrange
        service = CyclingTypeService(db_session)

        # Act
        result = await service.get_by_code("nonexistent")

        # Assert
        assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
class TestCyclingTypeServiceCreate:
    """Unit tests for CyclingTypeService.create()."""

    async def test_create_adds_new_cycling_type(self, db_session: AsyncSession):
        """Verify that create adds a new cycling type to database."""
        # Arrange
        service = CyclingTypeService(db_session)
        data = CyclingTypeCreateRequest(
            code="cyclocross",
            display_name="Cyclocross",
            description="Mixed terrain racing",
            is_active=True,
        )

        # Act
        result = await service.create(data)

        # Assert
        assert result.code == "cyclocross"
        assert result.display_name == "Cyclocross"
        assert result.description == "Mixed terrain racing"
        assert result.is_active is True
        assert result.id is not None
        assert result.created_at is not None

    async def test_create_converts_code_to_lowercase(self, db_session: AsyncSession):
        """Verify that create converts code to lowercase."""
        # Arrange
        service = CyclingTypeService(db_session)
        data = CyclingTypeCreateRequest(
            code="CycloCross", display_name="Cyclocross", is_active=True
        )

        # Act
        result = await service.create(data)

        # Assert
        assert result.code == "cyclocross"

    async def test_create_raises_error_for_duplicate_code(self, db_session: AsyncSession):
        """Verify that create raises ValueError for duplicate code."""
        # Arrange
        service = CyclingTypeService(db_session)

        # Create first type
        existing = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        db_session.add(existing)
        await db_session.commit()

        # Try to create duplicate
        data = CyclingTypeCreateRequest(code="mountain", display_name="Mountain 2", is_active=True)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.create(data)

        assert "ya existe" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestCyclingTypeServiceUpdate:
    """Unit tests for CyclingTypeService.update()."""

    async def test_update_changes_display_name(self, db_session: AsyncSession):
        """Verify that update changes the display name."""
        # Arrange
        service = CyclingTypeService(db_session)

        cycling_type = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        db_session.add(cycling_type)
        await db_session.commit()

        update_data = CyclingTypeUpdateRequest(display_name="Mountain Biking Pro")

        # Act
        result = await service.update("mountain", update_data)

        # Assert
        assert result.code == "mountain"
        assert result.display_name == "Mountain Biking Pro"

    async def test_update_changes_description(self, db_session: AsyncSession):
        """Verify that update changes the description."""
        # Arrange
        service = CyclingTypeService(db_session)

        cycling_type = CyclingType(
            code="mountain", display_name="Mountain", description="Old desc", is_active=True
        )
        db_session.add(cycling_type)
        await db_session.commit()

        update_data = CyclingTypeUpdateRequest(description="New description")

        # Act
        result = await service.update("mountain", update_data)

        # Assert
        assert result.description == "New description"
        assert result.display_name == "Mountain"  # Unchanged

    async def test_update_changes_active_status(self, db_session: AsyncSession):
        """Verify that update changes the active status."""
        # Arrange
        service = CyclingTypeService(db_session)

        cycling_type = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        db_session.add(cycling_type)
        await db_session.commit()

        update_data = CyclingTypeUpdateRequest(is_active=False)

        # Act
        result = await service.update("mountain", update_data)

        # Assert
        assert result.is_active is False

    async def test_update_raises_error_when_not_found(self, db_session: AsyncSession):
        """Verify that update raises ValueError when cycling type doesn't exist."""
        # Arrange
        service = CyclingTypeService(db_session)
        update_data = CyclingTypeUpdateRequest(display_name="New Name")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.update("nonexistent", update_data)

        assert "no se encontró" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestCyclingTypeServiceDelete:
    """Unit tests for CyclingTypeService.delete()."""

    async def test_delete_soft_sets_inactive(self, db_session: AsyncSession):
        """Verify that soft delete sets is_active to False."""
        # Arrange
        service = CyclingTypeService(db_session)

        cycling_type = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        db_session.add(cycling_type)
        await db_session.commit()

        # Act
        await service.delete("mountain", soft=True)

        # Assert
        result = await service.get_by_code("mountain")
        assert result is not None
        assert result.is_active is False

    async def test_delete_hard_removes_from_database(self, db_session: AsyncSession):
        """Verify that hard delete removes the cycling type from database."""
        # Arrange
        service = CyclingTypeService(db_session)

        cycling_type = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        db_session.add(cycling_type)
        await db_session.commit()

        # Act
        await service.delete("mountain", soft=False)

        # Assert
        result = await service.get_by_code("mountain")
        assert result is None

    async def test_delete_raises_error_when_not_found(self, db_session: AsyncSession):
        """Verify that delete raises ValueError when cycling type doesn't exist."""
        # Arrange
        service = CyclingTypeService(db_session)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.delete("nonexistent")

        assert "no se encontró" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestCyclingTypeServiceGetActiveCodes:
    """Unit tests for CyclingTypeService.get_active_codes()."""

    async def test_get_active_codes_returns_only_active_codes(self, db_session: AsyncSession):
        """Verify that get_active_codes returns only active type codes."""
        # Arrange
        service = CyclingTypeService(db_session)

        type1 = CyclingType(code="mountain", display_name="Mountain", is_active=True)
        type2 = CyclingType(code="road", display_name="Road", is_active=True)
        type3 = CyclingType(code="gravel", display_name="Gravel", is_active=False)

        db_session.add_all([type1, type2, type3])
        await db_session.commit()

        # Act
        result = await service.get_active_codes()

        # Assert
        assert isinstance(result, set)
        assert result == {"mountain", "road"}

    async def test_get_active_codes_returns_empty_set_when_no_active(
        self, db_session: AsyncSession
    ):
        """Verify that get_active_codes returns empty set when no active types."""
        # Arrange
        service = CyclingTypeService(db_session)

        inactive = CyclingType(code="mountain", display_name="Mountain", is_active=False)
        db_session.add(inactive)
        await db_session.commit()

        # Act
        result = await service.get_active_codes()

        # Assert
        assert result == set()
