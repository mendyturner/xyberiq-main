"""Database seeding script placeholder."""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


def main() -> None:
    """Entry point for database seed operations."""

    logger.info("seed.start", message="Seeding not yet implemented")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
