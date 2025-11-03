"""Application configuration settings using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic.networks import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the XyberIQ backend."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        env_prefix="XYBERIQ_",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = "XyberIQ Backend"
    environment: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = False
    support_email: EmailStr = "support@xyberiq.example"

    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/xyberiq"
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20

    redis_url: str = "redis://redis:6379/0"
    rq_default_queue: str = "default"

    s3_endpoint_url: str | None = None
    s3_region: str = "us-east-1"
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_bucket: str = "xyberiq"
    s3_use_ssl: bool = True

    jwt_secret_key: str = "change-me"
    jwt_refresh_secret_key: str = "change-me-refresh"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 15
    jwt_refresh_token_expires_minutes: int = 60 * 24 * 30

    password_reset_token_expires_minutes: int = 30

    cors_allow_origins: list[str] = Field(default_factory=list)

    rate_limit_auth_per_minute: int = 20

    request_id_header: str = "X-Request-ID"

    oidc_enabled: bool = False
    oidc_providers: list[str] = Field(default_factory=lambda: ["google", "microsoft"])

    openapi_tags: list[dict[str, Any]] = Field(default_factory=lambda: [
        {"name": "Auth", "description": "Authentication and authorization APIs."},
        {"name": "HR", "description": "Human resources management APIs."},
        {"name": "IT", "description": "IT and security operations APIs."},
        {"name": "Compliance", "description": "Compliance frameworks and controls."},
        {"name": "Content", "description": "Training content management."},
        {"name": "Exports", "description": "Data exports and evidence packages."},
        {"name": "Dash", "description": "Dashboard endpoints."},
        {"name": "Health", "description": "Operational monitoring endpoints."},
    ])

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def split_origins(cls, value: Any) -> list[str]:  # noqa: D401 - short doc inherited
        """Allow comma-separated strings to represent origin lists."""

        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, (list, tuple)):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        return []


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()  # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]
