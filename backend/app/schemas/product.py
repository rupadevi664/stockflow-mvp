from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Name of the product"
    )
    sku: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Stock Keeping Unit (SKU), unique per organization"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional detailed product description"
    )
    price: Decimal = Field(
        ...,
        ge=0,
        description="Product unit price (cannot be negative)"
    )
    quantity: int = Field(
        default=0,
        ge=0,
        description="Available stock quantity (cannot be negative)"
    )
    low_stock_threshold: int = Field(
        default=5,
        ge=0,
        description="Threshold for low-stock warning (cannot be negative)"
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150
    )
    sku: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    description: Optional[str] = None
    price: Optional[Decimal] = Field(
        default=None,
        ge=0
    )
    quantity: Optional[int] = Field(
        default=None,
        ge=0
    )
    low_stock_threshold: Optional[int] = Field(
        default=None,
        ge=0
    )


class ProductResponse(ProductBase):
    id: int
    organization_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
