from app.routes.auth import router as auth_router
from app.routes.products import router as products_router
from app.routes.stock import router as stock_router

__all__ = ["auth_router", "products_router", "stock_router"]
