import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import (
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate
)
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/organization",
    tags=["Organization Settings"]
)


# 1. GET ORGANIZATION SETTINGS
@router.get(
    "/settings",
    response_model=OrganizationSettingsResponse,
    summary="Get organization settings and details",
    description="Retrieve the organization profile, contact information, and default inventory thresholds for the authenticated user's organization."
)
def get_organization_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return organization


# 2. UPDATE ORGANIZATION SETTINGS
@router.put(
    "/settings",
    response_model=OrganizationSettingsResponse,
    summary="Update organization settings and details",
    description="Update the company name, contact email, contact phone, and default low-stock threshold for the authenticated user's organization."
)
def update_organization_settings(
    data: OrganizationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    update_fields = data.model_dump(exclude_unset=True)

    for field, value in update_fields.items():
        setattr(organization, field, value)

    try:
        db.commit()
        db.refresh(organization)
        return organization

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating organization settings for org {current_user.organization_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating organization settings"
        )
