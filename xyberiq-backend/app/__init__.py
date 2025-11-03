"""XyberIQ Backend application package."""

from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    """Return the installed package version or "0.0.0" when unavailable."""

    try:
        return version("xyberiq-backend")
    except PackageNotFoundError:
        return "0.0.0"


__all__ = ["get_version"]
