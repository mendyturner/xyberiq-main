"""API route registrations for the XyberIQ backend."""

from fastapi import APIRouter

from . import auth, root


api_router = APIRouter()

api_router.include_router(root.router)
api_router.include_router(auth.router)


__all__ = ["api_router"]
