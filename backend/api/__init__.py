from fastapi import APIRouter

from api import auth
from api.v1 import user, company, branch, menu, menu_item, basket

"""
Main router that includes all versioned API routes (v1).
"""


router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["auth"])

router.include_router(user.router, prefix="/user", tags=["Users"])
router.include_router(company.router, prefix="/company", tags=["Companies"])
router.include_router(branch.router, prefix="/branch", tags=["Branches"])
router.include_router(menu.router, prefix="/menu", tags=["Menus"])
router.include_router(menu_item.router, prefix="/menu_item", tags=["Menu-Item"])
router.include_router(basket.router, prefix="/basket", tags=["Basket"])