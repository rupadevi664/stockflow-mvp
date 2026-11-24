import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.stock import StockAdjustmentRequest, StockAdjustmentResponse
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["Stock Management"]
)


# INCREASE STOCK
@router.post(
    "/{product_id}/stock/increase",
    response_model=StockAdjustmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Increase product stock quantity",
    description="Increase inventory quantity for a specified product belonging to the authenticated organization."
)
def increase_stock(
    product_id: int,
    data: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id
        ).with_for_update().first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        previous_quantity = product.quantity
        updated_quantity = previous_quantity + data.quantity
        product.quantity = updated_quantity

        db.commit()
        db.refresh(product)

        return StockAdjustmentResponse(
            message="Stock increased successfully",
            product_id=product.id,
            product_name=product.name,
            previous_quantity=previous_quantity,
            updated_quantity=updated_quantity,
            changed_quantity=data.quantity
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error increasing stock for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating stock"
        )


# DECREASE STOCK
@router.post(
    "/{product_id}/stock/decrease",
    response_model=StockAdjustmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Decrease product stock quantity",
    description="Decrease inventory quantity safely with concurrency protection and underflow prevention."
)
def decrease_stock(
    product_id: int,
    data: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id
        ).with_for_update().first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        previous_quantity = product.quantity

        if previous_quantity < data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock available. Current stock: {previous_quantity}, requested deduction: {data.quantity}"
            )

        updated_quantity = previous_quantity - data.quantity
        product.quantity = updated_quantity

        db.commit()
        db.refresh(product)

        return StockAdjustmentResponse(
            message="Stock decreased successfully",
            product_id=product.id,
            product_name=product.name,
            previous_quantity=previous_quantity,
            updated_quantity=updated_quantity,
            changed_quantity=data.quantity
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error decreasing stock for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating stock"
        )
