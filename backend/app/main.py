import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine
from app import models
from app.routes.auth import router as auth_router
from app.routes.organization import router as organization_router
from app.routes.dashboard import router as dashboard_router
from app.routes.stock import router as stock_router
from app.routes.products import router as products_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SaaS Inventory Management System"
)

# Configure CORS for frontend integration
cors_origins = (
    [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    if settings.CORS_ORIGINS != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables for the MVP safely on startup
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.warning(f"Database table initialization deferred: {str(e)}")


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
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }