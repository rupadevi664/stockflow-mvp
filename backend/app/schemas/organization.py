import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class OrganizationSettingsResponse(BaseModel):
    id: int
    name: str
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    default_low_stock_threshold: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationSettingsUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
        description="Organization company name"
    )
    contact_email: Optional[EmailStr] = Field(
        default=None,
        description="Official contact email"
    )
    contact_phone: Optional[str] = Field(
        default=None,
        description="Official contact phone number"
    )
    default_low_stock_threshold: Optional[int] = Field(
        default=None,
        ge=0,
        description="Default inventory threshold for low stock alerts"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Organization name must not be empty.")
            return stripped
        return v

    @field_validator("contact_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                return None
            # Must only contain valid phone characters: digits, spaces, +, -, (, ), .
            if not re.match(r"^[\+0-9\s\-\(\)\.]+$", stripped):
                raise ValueError("Invalid phone number format. Contains invalid characters.")
            # Extract digits only to check length: between 7 and 15 digits
            digits = re.sub(r"[^\d]", "", stripped)
            if len(digits) < 7 or len(digits) > 15:
                raise ValueError("Invalid phone number format. Must contain 7 to 15 digits.")
            return stripped
        return v



# Alias for backward/forward compatibility
OrganizationSettingsRequest = OrganizationSettingsUpdate
