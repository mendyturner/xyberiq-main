"""Base API routes."""

from __future__ import annotations

from fastapi import APIRouter


router = APIRouter()


@router.get("/", tags=["Health"], summary="API root")
async def read_root() -> dict[str, str]:
    """Simple root endpoint to confirm API availability."""

    return {"message": "Welcome to the XyberIQ API"}


__all__ = ["router"]
