"""Redis client factory."""

from __future__ import annotations

from functools import lru_cache

from redis import Redis

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    """Return a Redis client based on application settings."""

    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


__all__ = ["get_redis_client"]
