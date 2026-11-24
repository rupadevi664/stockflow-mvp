
from fastapi import FastAPI

app = FastAPI(
    title="StockFlow MVP",
    description="SaaS Inventory Management System",
    version="1.0.0"
)


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
