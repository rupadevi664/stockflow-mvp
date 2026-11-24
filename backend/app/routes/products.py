import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDeleteResponse
)
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# 1. CREATE PRODUCT
@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_product = db.query(Product).filter(
        Product.organization_id == current_user.organization_id,
        Product.sku == data.sku
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this SKU already exists in your organization"
        )

    try:
        product = Product(
            name=data.name,
            sku=data.sku,
            description=data.description,
            price=data.price,
            quantity=data.quantity,
            low_stock_threshold=data.low_stock_threshold,
            organization_id=current_user.organization_id
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this SKU already exists in your organization"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the product"
        )


# 2. GET ALL PRODUCTS FOR USER'S ORGANIZATION
@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="List products for the authenticated organization"
)
def get_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip_val = skip.default if hasattr(skip, "default") else skip
    limit_val = limit.default if hasattr(limit, "default") else limit

    products = db.query(Product).filter(
        Product.organization_id == current_user.organization_id
    ).offset(skip_val).limit(limit_val).all()

    return products


# 3. GET SINGLE PRODUCT BY ID
@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product details by ID"
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.organization_id == current_user.organization_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# 4. UPDATE PRODUCT BY ID
@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product details"
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.organization_id == current_user.organization_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # If SKU is updated, ensure uniqueness within organization
    if data.sku and data.sku != product.sku:
        existing_sku = db.query(Product).filter(
            Product.organization_id == current_user.organization_id,
            Product.sku == data.sku,
            Product.id != product_id
        ).first()

        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with this SKU already exists in your organization"
            )

    # Apply only fields that were set in the request
    update_fields = data.model_dump(exclude_unset=True)
    for field_name, value in update_fields.items():
        setattr(product, field_name, value)

    try:
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this SKU already exists in your organization"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the product"
        )


# 5. DELETE PRODUCT BY ID
@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    summary="Delete a product by ID"
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.organization_id == current_user.organization_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    try:
        db.delete(product)
        db.commit()
        return ProductDeleteResponse(
            message="Product deleted successfully",
            id=product_id
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the product"
        )
