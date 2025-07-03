from fastapi import APIRouter
from api.v1 import user

router = APIRouter(prefix="/api/v1")
router.include_router(user.router, prefix="/user", tags=["Users"])
