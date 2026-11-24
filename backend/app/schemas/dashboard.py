from decimal import Decimal
from pydantic import BaseModel, Field


class DashboardSummaryResponse(BaseModel):
    total_products: int = Field(
        ...,
        description="Total number of distinct products in the organization"
    )
    total_stock_quantity: int = Field(
        ...,
        description="Total quantity of all items in stock"
    )
    low_stock_products: int = Field(
        ...,
        description="Count of products at or below their low-stock threshold"
    )
    out_of_stock_products: int = Field(
        ...,
        description="Count of products with zero available stock"
    )
    total_inventory_value: Decimal = Field(
        ...,
        description="Total financial value of inventory (SUM of price * quantity)"
    )


class InventoryValueResponse(BaseModel):
    total_inventory_value: Decimal = Field(
        ...,
        description="Total monetary value of the inventory"
    )
    total_stock_quantity: int = Field(
        ...,
        description="Total quantity of stock across all products"
    )
    total_products: int = Field(
        ...,
        description="Total number of products in the organization"
    )
