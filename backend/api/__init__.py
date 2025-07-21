from fastapi import APIRouter

from api import auth
from api.v1 import user, profile, company

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["auth"])

router.include_router(user.router, prefix="/user", tags=["Users"])
router.include_router(company.router, prefix="/company", tags=["Companies"])
