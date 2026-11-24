import logging
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from sqlalchemy.sql.functions import coalesce

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductResponse
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    InventoryValueResponse
)
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard & Analytics"]
)


# 1. DASHBOARD SUMMARY
@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get dashboard inventory summary",
    description="Calculates total products, total stock quantity, low-stock count, out-of-stock count, and total inventory value for the authenticated user's organization."
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        summary = db.query(
            func.count(Product.id).label("total_products"),
            coalesce(func.sum(Product.quantity), 0).label("total_stock_quantity"),
            coalesce(func.sum(Product.price * Product.quantity), Decimal("0.00")).label("total_inventory_value"),
            coalesce(
                func.sum(case((Product.quantity <= Product.low_stock_threshold, 1), else_=0)),
                0
            ).label("low_stock_products"),
            coalesce(
                func.sum(case((Product.quantity == 0, 1), else_=0)),
                0
            ).label("out_of_stock_products")
        ).filter(
            Product.organization_id == current_user.organization_id
        ).first()

        # Format and round total inventory value safely to 2 decimal places
        raw_value = summary.total_inventory_value if summary else Decimal("0.00")
        inventory_value = Decimal(str(round(Decimal(str(raw_value)), 2)))

        return DashboardSummaryResponse(
            total_products=int(summary.total_products) if summary else 0,
            total_stock_quantity=int(summary.total_stock_quantity) if summary else 0,
            low_stock_products=int(summary.low_stock_products) if summary else 0,
            out_of_stock_products=int(summary.out_of_stock_products) if summary else 0,
            total_inventory_value=inventory_value
        )

    except Exception as e:
        logger.error(f"Error computing dashboard summary for org {current_user.organization_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while computing the dashboard summary"
        )


# 2. LOW-STOCK PRODUCTS
@router.get(
    "/low-stock",
    response_model=List[ProductResponse],
    summary="Get low-stock products for dashboard",
    description="Retrieve all products in the authenticated organization where quantity is less than or equal to low_stock_threshold."
)
def get_dashboard_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        products = db.query(Product).filter(
            Product.organization_id == current_user.organization_id,
            Product.quantity <= Product.low_stock_threshold
        ).all()

        return products

    except Exception as e:
        logger.error(f"Error fetching dashboard low-stock for org {current_user.organization_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching low-stock products"
        )


# 3. INVENTORY VALUE
@router.get(
    "/inventory-value",
    response_model=InventoryValueResponse,
    summary="Get inventory valuation metrics",
    description="Retrieve total monetary valuation, stock quantity, and product count for the authenticated organization."
)
def get_inventory_value(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        valuation = db.query(
            func.count(Product.id).label("total_products"),
            coalesce(func.sum(Product.quantity), 0).label("total_stock_quantity"),
            coalesce(func.sum(Product.price * Product.quantity), Decimal("0.00")).label("total_inventory_value")
        ).filter(
            Product.organization_id == current_user.organization_id
        ).first()

        raw_value = valuation.total_inventory_value if valuation else Decimal("0.00")
        inventory_value = Decimal(str(round(Decimal(str(raw_value)), 2)))

        return InventoryValueResponse(
            total_inventory_value=inventory_value,
            total_stock_quantity=int(valuation.total_stock_quantity) if valuation else 0,
            total_products=int(valuation.total_products) if valuation else 0
        )

    except Exception as e:
        logger.error(f"Error computing inventory value for org {current_user.organization_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while computing inventory valuation"
        )
