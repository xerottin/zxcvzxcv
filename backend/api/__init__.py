from fastapi import APIRouter

from api import auth
from api.v1 import user, profile

router = APIRouter(prefix="/api/v1")
router.include_router(user.router, prefix="/user", tags=["Users"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
