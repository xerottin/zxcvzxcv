from api.v1 import authorization, basket, branch, company, menu, menu_item, order, user
from fastapi import APIRouter

router_v1 = APIRouter(prefix="/v1")

router_v1.include_router(
    authorization.router, prefix="/authorization", tags=["Authorization"]
)
router_v1.include_router(user.router, prefix="/users", tags=["Users"])
router_v1.include_router(company.router, prefix="/companies", tags=["Companies"])
router_v1.include_router(branch.router, prefix="/branches", tags=["Branches"])
router_v1.include_router(menu.router, prefix="/menus", tags=["Menus"])
router_v1.include_router(menu_item.router, prefix="/menu-items", tags=["Menu Items"])
router_v1.include_router(basket.router, prefix="/baskets", tags=["Baskets"])
router_v1.include_router(order.router, prefix="/orders", tags=["Orders"])
# router_v1.include_router(payment.router,       prefix="/payments",      tags=["Payments"])
