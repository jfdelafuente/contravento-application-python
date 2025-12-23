"""
Configuration management for ContraVento backend.

Loads and validates environment variables using Pydantic Settings.
All configuration is immutable and validated at startup.
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="ContraVento", description="Application name")
    app_env: str = Field(default="development", description="Environment (development, testing, production)")
    debug: bool = Field(default=False, description="Debug mode")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./contravento_dev.db",
        description="Database connection URL"
    )

    # Security & Authentication
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT tokens (min 32 characters)"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=15,
        ge=1,
        description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=30,
        ge=1,
        description="Refresh token expiration in days"
    )

    # Password Hashing
    bcrypt_rounds: int = Field(
        default=12,
        ge=4,
        le=31,
        description="Bcrypt rounds (4-31, recommended 12 for production)"
    )

    # Email Configuration
    smtp_host: str = Field(default="localhost", description="SMTP server host")
    smtp_port: int = Field(default=1025, ge=1, le=65535, description="SMTP server port")
    smtp_user: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")
    smtp_from: str = Field(default="noreply@contravento.com", description="From email address")
    smtp_tls: bool = Field(default=False, description="Use TLS for SMTP")

    # File Storage
    storage_path: str = Field(default="./storage", description="Local file storage path")
    upload_max_size_mb: int = Field(default=5, ge=1, description="Maximum upload size in MB")
    profile_photo_size: int = Field(default=400, ge=100, description="Profile photo dimension (square)")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )

    # Rate Limiting
    login_max_attempts: int = Field(default=5, ge=1, description="Max login attempts before lockout")
    login_lockout_minutes: int = Field(default=15, ge=1, description="Lockout duration in minutes")
    verification_email_max_per_hour: int = Field(
        default=3,
        ge=1,
        description="Max verification emails per hour"
    )

    # Session
    session_expire_days: int = Field(default=30, ge=1, description="Session expiration in days")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Validate application environment."""
        allowed_envs = {"development", "testing", "production"}
        if v.lower() not in allowed_envs:
            raise ValueError(f"app_env must be one of {allowed_envs}")
        return v.lower()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v_upper

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.app_env == "testing"

    @property
    def database_is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.database_url.lower()

    @property
    def database_is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return "postgresql" in self.database_url.lower()


# Global settings instance
settings = Settings()
