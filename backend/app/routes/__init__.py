from app.routes.auth import router as auth_router
from app.routes.organization import router as organization_router
from app.routes.products import router as products_router
from app.routes.stock import router as stock_router
from app.routes.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "organization_router",
    "products_router",
    "stock_router",
    "dashboard_router"
]
