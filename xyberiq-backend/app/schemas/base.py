"""Shared Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


__all__ = ["APIModel"]
