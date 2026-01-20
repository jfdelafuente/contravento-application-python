"""
Statistics and Achievements request/response schemas.

Pydantic models for validating stats and achievements API requests and responses.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class CountryInfo(BaseModel):
    """
    Country information with code and name.

    Attributes:
        code: ISO country code (e.g., 'ES')
        name: Country name in Spanish (e.g., 'España')
    """

    code: str = Field(..., description="Código ISO del país (e.g., 'ES')")
    name: str = Field(..., description="Nombre del país en español (e.g., 'España')")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"code": "ES", "name": "España"}}


class StatsResponse(BaseModel):
    """
    T155: Schema for user statistics in API responses.

    Returns aggregated user cycling statistics.

    Attributes:
        total_trips: Number of published trips
        total_kilometers: Total kilometers accumulated
        countries_visited: List of countries with codes and names
        total_photos: Total photos uploaded
        achievements_count: Number of achievements earned
        last_trip_date: Date of most recent trip (nullable)
        updated_at: Last stats update timestamp
    """

    total_trips: int = Field(..., description="Número total de viajes publicados")
    total_kilometers: float = Field(..., description="Kilómetros totales recorridos")
    countries_visited: list[CountryInfo] = Field(..., description="Lista de países visitados")
    total_photos: int = Field(..., description="Número total de fotos subidas")
    achievements_count: int = Field(..., description="Número de logros desbloqueados")
    last_trip_date: date | None = Field(None, description="Fecha del último viaje")
    updated_at: datetime = Field(..., description="Última actualización de estadísticas")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_trips": 12,
                "total_kilometers": 1547.85,
                "countries_visited": [
                    {"code": "ES", "name": "España"},
                    {"code": "FR", "name": "Francia"},
                    {"code": "IT", "name": "Italia"},
                ],
                "total_photos": 48,
                "achievements_count": 5,
                "last_trip_date": "2025-12-15",
                "updated_at": "2025-12-20T14:30:00Z",
            }
        }


class AchievementResponse(BaseModel):
    """
    T156: Schema for user-earned achievement in API responses.

    Returns achievement details with the date it was earned.

    Attributes:
        code: Unique achievement code
        name: Achievement display name
        description: Achievement description
        badge_icon: Emoji or icon for the badge
        requirement_type: Type of requirement (distance, trips, countries, photos, followers)
        requirement_value: Value required to unlock
        awarded_at: Timestamp when achievement was earned
    """

    code: str = Field(..., description="Código único del logro")
    name: str = Field(..., description="Nombre del logro")
    description: str = Field(..., description="Descripción del logro")
    badge_icon: str = Field(..., description="Icono o emoji del badge")
    requirement_type: str = Field(
        ..., description="Tipo de requisito: distance, trips, countries, photos, followers"
    )
    requirement_value: float = Field(..., description="Valor requerido para desbloquear")
    awarded_at: datetime = Field(..., description="Fecha y hora de obtención")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "VOYAGER",
                "name": "Viajero",
                "description": "Acumulaste 1000 km",
                "badge_icon": "🌍",
                "requirement_type": "distance",
                "requirement_value": 1000,
                "awarded_at": "2025-12-15T18:20:00Z",
            }
        }


class AchievementDefinition(BaseModel):
    """
    T157: Schema for achievement definition (without awarded_at).

    Returns achievement details for all available achievements.
    Used in GET /achievements endpoint.

    Attributes:
        code: Unique achievement code
        name: Achievement display name
        description: Achievement description
        badge_icon: Emoji or icon for the badge
        requirement_type: Type of requirement (distance, trips, countries, photos, followers)
        requirement_value: Value required to unlock
    """

    code: str = Field(..., description="Código único del logro")
    name: str = Field(..., description="Nombre del logro")
    description: str = Field(..., description="Descripción del logro")
    badge_icon: str = Field(..., description="Icono o emoji del badge")
    requirement_type: str = Field(
        ..., description="Tipo de requisito: distance, trips, countries, photos, followers"
    )
    requirement_value: float = Field(..., description="Valor requerido para desbloquear")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "CENTURY",
                "name": "Centurión",
                "description": "Recorriste 100 km en total",
                "badge_icon": "💯",
                "requirement_type": "distance",
                "requirement_value": 100,
            }
        }


class UserAchievementResponse(BaseModel):
    """
    T158: Schema for listing user achievements with metadata.

    Wrapper for user achievements list with total count.

    Attributes:
        achievements: List of user-earned achievements
        total_count: Total number of achievements earned
    """

    achievements: list[AchievementResponse] = Field(..., description="Lista de logros obtenidos")
    total_count: int = Field(..., description="Número total de logros obtenidos")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "achievements": [
                    {
                        "code": "VOYAGER",
                        "name": "Viajero",
                        "description": "Acumulaste 1000 km",
                        "badge_icon": "🌍",
                        "requirement_type": "distance",
                        "requirement_value": 1000,
                        "awarded_at": "2025-12-15T18:20:00Z",
                    }
                ],
                "total_count": 1,
            }
        }


class AchievementDefinitionList(BaseModel):
    """
    Schema for listing all available achievements.

    Wrapper for achievement definitions list with total count.

    Attributes:
        achievements: List of all achievement definitions
        total_count: Total number of available achievements
    """

    achievements: list[AchievementDefinition] = Field(
        ..., description="Lista de todos los logros disponibles"
    )
    total_count: int = Field(..., description="Número total de logros disponibles")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "achievements": [
                    {
                        "code": "FIRST_TRIP",
                        "name": "Primer Viaje",
                        "description": "Publicaste tu primer viaje",
                        "badge_icon": "🚴",
                        "requirement_type": "trips",
                        "requirement_value": 1,
                    },
                    {
                        "code": "CENTURY",
                        "name": "Centurión",
                        "description": "Recorriste 100 km en total",
                        "badge_icon": "💯",
                        "requirement_type": "distance",
                        "requirement_value": 100,
                    },
                ],
                "total_count": 9,
            }
        }
