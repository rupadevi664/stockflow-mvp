from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    UserProfileResponse
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDeleteResponse
)

from app.schemas.stock import (
    StockAdjustmentRequest,
    StockAdjustmentResponse,
    StockUpdateRequest,
    StockUpdateResponse
)
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    InventoryValueResponse
)
from app.schemas.organization import (
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    OrganizationSettingsRequest
)

__all__ = [
    "SignupRequest",
    "SignupResponse",
    "LoginRequest",
    "LoginResponse",
    "UserProfileResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductDeleteResponse",
    "StockAdjustmentRequest",
    "StockAdjustmentResponse",
    "StockUpdateRequest",
    "StockUpdateResponse",
    "DashboardSummaryResponse",
    "InventoryValueResponse",
    "OrganizationSettingsResponse",
    "OrganizationSettingsUpdate",
    "OrganizationSettingsRequest"
]




