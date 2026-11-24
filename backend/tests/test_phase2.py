import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.database import Base, get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    UserProfileResponse
)
from app.routes.auth import signup, login, get_current_user, get_my_profile


# Create isolated in-memory test database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh isolated database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


# 1. SQLAlchemy Engine, SessionLocal, Base & get_db Configuration
def test_sqlalchemy_configuration():
    from app.database import engine, SessionLocal, Base, get_db
    assert engine is not None
    assert SessionLocal is not None
    assert Base is not None
    gen = get_db()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        pass


# 2. Organization Database Model
def test_organization_model(db_session):
    org = Organization(name="Test Company")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    assert org.id is not None
    assert org.name == "Test Company"
    assert org.created_at is not None
    assert Organization.__tablename__ == "organizations"


# 3. User Database Model & Relationships
def test_user_model(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    user = User(
        name="Test User",
        email="testuser@example.com",
        password_hash=hash_password("Password123"),
        organization_id=org.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == "testuser@example.com"
    assert user.organization.name == "Test Org"
    assert org.users[0].name == "Test User"
    assert User.__tablename__ == "users"


# 4. Password Hashing (Argon2)
def test_password_hashing():
    raw_pw = "StrongPassword123"
    hashed = hash_password(raw_pw)

    assert hashed is not None
    assert hashed != raw_pw
    assert "$argon2" in hashed  # Confirms Argon2 algorithm


# 5. Correct Password Verification
def test_password_verification_success():
    raw_pw = "StrongPassword123"
    hashed = hash_password(raw_pw)

    assert verify_password(raw_pw, hashed) is True


# 6. Wrong Password Rejection
def test_password_verification_failure():
    raw_pw = "StrongPassword123"
    hashed = hash_password(raw_pw)

    assert verify_password("WrongPassword999", hashed) is False


# 7. Safe Handling of Plain-text Passwords
def test_plaintext_password_handling():
    # Plain text should NEVER verify as valid and must not crash with 500
    assert verify_password("secret", "secret") is False
    assert verify_password("secret", "invalid_corrupt_hash_value") is False


# 8. JWT Token Generation
def test_jwt_generation():
    token = create_access_token(data={"sub": "42"})
    assert isinstance(token, str)
    assert len(token) > 20


# 9. JWT Token Validation
def test_jwt_validation():
    token = create_access_token(data={"sub": "42"})
    payload = decode_access_token(token)

    assert payload.get("sub") == "42"
    assert "exp" in payload


# 10. Expired Token Rejection
def test_jwt_expired_token():
    past_time = datetime.now(timezone.utc) - timedelta(minutes=15)
    expired_token = jwt.encode(
        {"sub": "42", "exp": past_time},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    payload = decode_access_token(expired_token)
    assert payload == {}


# 11. User Signup API - Success
def test_signup_api_success(db_session):
    signup_data = SignupRequest(
        name="Rupa",
        email="rupa_test@example.com",
        password="StrongPassword123",
        organization_name="StockFlow Company"
    )
    response = signup(data=signup_data, db=db_session)

    assert isinstance(response, SignupResponse)
    assert response.email == "rupa_test@example.com"
    assert response.user_id is not None
    assert response.organization_id is not None
    assert response.message == "Registration successful"

    # Verify user saved in DB with Argon2 hash
    saved_user = db_session.query(User).filter(User.email == "rupa_test@example.com").first()
    assert saved_user is not None
    assert "$argon2" in saved_user.password_hash
    assert saved_user.password_hash != "StrongPassword123"


# 12. User Signup API - Duplicate Email Rejection
def test_signup_api_duplicate_email(db_session):
    signup_data = SignupRequest(
        name="Rupa",
        email="duplicate@example.com",
        password="StrongPassword123",
        organization_name="StockFlow Company"
    )
    signup(data=signup_data, db=db_session)

    # Attempt signup again with same email
    with pytest.raises(HTTPException) as exc_info:
        signup(data=signup_data, db=db_session)

    assert exc_info.value.status_code == 400
    assert "already registered" in exc_info.value.detail.lower()


# 13. User Login API - Success
def test_login_api_success(db_session):
    # Prepare user
    signup_data = SignupRequest(
        name="Rupa",
        email="login_test@example.com",
        password="StrongPassword123",
        organization_name="StockFlow Company"
    )
    signup(data=signup_data, db=db_session)

    # Login
    login_data = LoginRequest(
        email="login_test@example.com",
        password="StrongPassword123"
    )
    response = login(data=login_data, db=db_session)

    assert isinstance(response, LoginResponse)
    assert response.access_token is not None
    assert response.token_type == "bearer"


# 14. User Login API - Wrong Password Rejection
def test_login_api_wrong_password(db_session):
    signup_data = SignupRequest(
        name="Rupa",
        email="wrong_pw_test@example.com",
        password="StrongPassword123",
        organization_name="StockFlow Company"
    )
    signup(data=signup_data, db=db_session)

    login_data = LoginRequest(
        email="wrong_pw_test@example.com",
        password="WrongPassword123"
    )
    with pytest.raises(HTTPException) as exc_info:
        login(data=login_data, db=db_session)

    assert exc_info.value.status_code == 401
    assert "invalid email or password" in exc_info.value.detail.lower()


# 15. User Login API - Non-existent Email Rejection
def test_login_api_nonexistent_email(db_session):
    login_data = LoginRequest(
        email="nonexistent@example.com",
        password="StrongPassword123"
    )
    with pytest.raises(HTTPException) as exc_info:
        login(data=login_data, db=db_session)

    assert exc_info.value.status_code == 401
    assert "invalid email or password" in exc_info.value.detail.lower()


# 16. Protected /auth/me Endpoint - Success
def test_protected_me_endpoint_success(db_session):
    signup_data = SignupRequest(
        name="Rupa",
        email="me_test@example.com",
        password="StrongPassword123",
        organization_name="StockFlow Company"
    )
    signup_resp = signup(data=signup_data, db=db_session)

    login_data = LoginRequest(
        email="me_test@example.com",
        password="StrongPassword123"
    )
    login_resp = login(data=login_data, db=db_session)

    # Get current user using token
    current_user = get_current_user(token=login_resp.access_token, db=db_session)
    profile = get_my_profile(current_user=current_user)

    assert isinstance(profile, UserProfileResponse)
    assert profile.id == signup_resp.user_id
    assert profile.name == "Rupa"
    assert profile.email == "me_test@example.com"
    assert profile.organization_id == signup_resp.organization_id


# 17. Protected /auth/me Endpoint - Missing / Invalid Token Rejection
def test_protected_me_endpoint_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid.bearer.token", db=db_session)

    assert exc_info.value.status_code == 401


# 18. Protected /auth/me Endpoint - Expired Token Rejection
def test_protected_me_endpoint_expired_token(db_session):
    past_time = datetime.now(timezone.utc) - timedelta(minutes=15)
    expired_token = jwt.encode(
        {"sub": "1", "exp": past_time},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=expired_token, db=db_session)

    assert exc_info.value.status_code == 401
