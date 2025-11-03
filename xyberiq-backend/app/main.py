"""Application entrypoint for the XyberIQ backend."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import get_version
from app.api.routes import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging


def create_application(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application instance."""

    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.project_name,
        description="XyberIQ compliance training platform backend",
        version=get_version(),
        contact={
            "name": "XyberIQ Platform Team",
            "email": settings.support_email,
        },
        license_info={
            "name": "Proprietary",
        },
        openapi_tags=settings.openapi_tags,
    )

    if settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/health", tags=["Health"], response_model=dict[str, Any])
    def health_check(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
        """Return a basic health check response."""

        return {
            "status": "ok",
            "environment": settings.environment,
        }

    @app.get("/version", tags=["Health"], response_model=dict[str, str])
    def version() -> dict[str, str]:
        """Expose application version information."""

        return {"version": get_version()}

    app.include_router(api_router)

    return app


app = create_application()


__all__ = ["create_application", "app"]
