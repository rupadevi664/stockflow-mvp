from fastapi import FastAPI

from app.core.config import settings
from app.database import Base, engine
from app import models
from app.routes.auth import router as auth_router
from app.routes.organization import router as organization_router
from app.routes.dashboard import router as dashboard_router
from app.routes.stock import router as stock_router
from app.routes.products import router as products_router






app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SaaS Inventory Management System"
)


# Create database tables for the MVP
Base.metadata.create_all(bind=engine)


# Register routes
app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(dashboard_router)
app.include_router(stock_router)
app.include_router(products_router)






@app.get("/")
def home():
    return {
        "message": "Welcome to StockFlow MVP API",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }