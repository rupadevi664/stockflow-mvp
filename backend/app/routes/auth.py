from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.schemas.auth import SignupRequest, SignupResponse
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(data: SignupRequest, db: Session = Depends(get_db)):

    # Check existing email
    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    try:
        # Create organization
        organization = Organization(
            name=data.organization_name
        )

        db.add(organization)
        db.flush()

        # Create user
        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            organization_id=organization.id
        )
 
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "Registration successful",
            "user_id": user.id,
            "organization_id": organization.id,
            "email": user.email
        }

    except Exception:
        db.rollback()
        raise