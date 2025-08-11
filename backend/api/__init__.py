from api import auth
from api.v1 import router_v1
from fastapi import APIRouter

router = APIRouter(prefix="/api")
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(router_v1)
