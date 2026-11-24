from pydantic import BaseModel, Field


class StockAdjustmentRequest(BaseModel):
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity must be an integer greater than zero"
    )


# Alias for backward/forward compatibility
StockUpdateRequest = StockAdjustmentRequest


class StockAdjustmentResponse(BaseModel):
    message: str
    product_id: int
    product_name: str
    previous_quantity: int
    updated_quantity: int
    changed_quantity: int


# Alias for backward/forward compatibility
StockUpdateResponse = StockAdjustmentResponse
