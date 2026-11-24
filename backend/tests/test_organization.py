import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import (
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate
)
from app.routes.organization import (
    get_organization_settings,
    update_organization_settings
)
from app.routes.auth import get_current_user


# Isolated in-memory SQLite database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def setup_test_orgs(db):
    org_a = Organization(
        name="Acme Corp",
        contact_email="contact@acme.com",
        contact_phone="+1-555-0199",
        default_low_stock_threshold=5
    )
    org_b = Organization(
        name="Beta Logistics",
        contact_email="info@betalog.com",
        contact_phone="+1-555-0288",
        default_low_stock_threshold=10
    )
    db.add_all([org_a, org_b])
    db.commit()
    db.refresh(org_a)
    db.refresh(org_b)

    user_a = User(
        name="Alice Admin",
        email="alice@acme.com",
        password_hash="mock_hash_a",
        organization_id=org_a.id
    )
    user_b = User(
        name="Bob Manager",
        email="bob@betalog.com",
        password_hash="mock_hash_b",
        organization_id=org_b.id
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    return user_a, user_b, org_a, org_b


# 1. Retrieve organization settings
def test_get_organization_settings(db):
    user_a, _, org_a, _ = setup_test_orgs(db)

    settings = get_organization_settings(db=db, current_user=user_a)
    assert isinstance(settings, Organization)
    assert settings.id == org_a.id
    assert settings.name == "Acme Corp"
    assert settings.contact_email == "contact@acme.com"
    assert settings.contact_phone == "+1-555-0199"
    assert settings.default_low_stock_threshold == 5


# 2. Update organization settings successfully
def test_update_organization_settings_success(db):
    user_a, _, org_a, _ = setup_test_orgs(db)

    update_in = OrganizationSettingsUpdate(
        name="Acme Global Corporation",
        contact_email="support@acmeglobal.com",
        contact_phone="+1 (800) 555-0123",
        default_low_stock_threshold=8
    )

    updated = update_organization_settings(data=update_in, db=db, current_user=user_a)

    assert updated.id == org_a.id
    assert updated.name == "Acme Global Corporation"
    assert updated.contact_email == "support@acmeglobal.com"
    assert updated.contact_phone == "+1 (800) 555-0123"
    assert updated.default_low_stock_threshold == 8

    # Verify persisted in database
    db.refresh(org_a)
    assert org_a.name == "Acme Global Corporation"
    assert org_a.default_low_stock_threshold == 8


# 3. Partial update of organization settings
def test_partial_update_organization_settings(db):
    user_a, _, org_a, _ = setup_test_orgs(db)

    # Only update the low stock threshold
    update_in = OrganizationSettingsUpdate(default_low_stock_threshold=12)
    updated = update_organization_settings(data=update_in, db=db, current_user=user_a)

    assert updated.default_low_stock_threshold == 12
    assert updated.name == "Acme Corp"  # Unchanged field remains intact
    assert updated.contact_email == "contact@acme.com"


# 4. Reject invalid empty organization name
def test_reject_empty_organization_name():
    with pytest.raises(ValidationError) as exc_info:
        OrganizationSettingsUpdate(name="")
    assert "at least 1 character" in str(exc_info.value) or "must not be empty" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info2:
        OrganizationSettingsUpdate(name="   ")
    assert "must not be empty" in str(exc_info2.value)


# 5. Reject invalid email format
def test_reject_invalid_email_format():
    with pytest.raises(ValidationError) as exc_info:
        OrganizationSettingsUpdate(contact_email="not-an-email")
    assert "value is not a valid email address" in str(exc_info.value).lower()


# 6. Reject invalid phone number format
def test_reject_invalid_phone_number_format():
    with pytest.raises(ValidationError) as exc_info:
        OrganizationSettingsUpdate(contact_phone="abcdefg123")
    assert "Invalid phone number format" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info2:
        OrganizationSettingsUpdate(contact_phone="123")  # Less than 7 digits
    assert "Must contain 7 to 15 digits" in str(exc_info2.value)


# 7. Reject negative low-stock threshold
def test_reject_negative_low_stock_threshold():
    with pytest.raises(ValidationError) as exc_info:
        OrganizationSettingsUpdate(default_low_stock_threshold=-1)
    assert "greater than or equal to 0" in str(exc_info.value)


# 8. Reject unauthenticated requests
def test_reject_unauthenticated_requests(db):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid_token_xyz", db=db)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


# 9. Verify organization data isolation
def test_organization_data_isolation(db):
    user_a, user_b, org_a, org_b = setup_test_orgs(db)

    # User A updates Org A settings
    update_in = OrganizationSettingsUpdate(
        name="Acme Modified",
        default_low_stock_threshold=20
    )
    update_organization_settings(data=update_in, db=db, current_user=user_a)

    # User B queries Org B settings -> Must remain completely unaffected
    settings_b = get_organization_settings(db=db, current_user=user_b)
    assert settings_b.id == org_b.id
    assert settings_b.name == "Beta Logistics"
    assert settings_b.default_low_stock_threshold == 10  # Untouched

    # User A's settings are isolated to Org A
    settings_a = get_organization_settings(db=db, current_user=user_a)
    assert settings_a.id == org_a.id
    assert settings_a.name == "Acme Modified"
    assert settings_a.default_low_stock_threshold == 20
