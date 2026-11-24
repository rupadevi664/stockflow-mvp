import pytest
from decimal import Decimal
from pydantic import ValidationError
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.organization import Organization
from app.models.user import User
from app.models.product import Product
from app.schemas.stock import StockAdjustmentRequest, StockAdjustmentResponse
from app.routes.stock import increase_stock, decrease_stock, get_low_stock_products
from app.routes.auth import get_current_user


# Isolated SQLite in-memory test database
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


def setup_orgs_and_users(db):
    org_a = Organization(name="Organization Alpha")
    org_b = Organization(name="Organization Beta")
    db.add_all([org_a, org_b])
    db.commit()
    db.refresh(org_a)
    db.refresh(org_b)

    user_a = User(
        name="Alice Alpha",
        email="alice@alpha.com",
        password_hash="hashed_pw_a",
        organization_id=org_a.id
    )
    user_b = User(
        name="Bob Beta",
        email="bob@beta.com",
        password_hash="hashed_pw_b",
        organization_id=org_b.id
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    return user_a, user_b, org_a, org_b


# 1. Successful stock increase
def test_successful_stock_increase(db):
    user_a, _, org_a, _ = setup_orgs_and_users(db)

    product = Product(
        name="Mousepad",
        sku="MP-001",
        price=Decimal("15.00"),
        quantity=10,
        low_stock_threshold=5,
        organization_id=org_a.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    req = StockAdjustmentRequest(quantity=15)
    res = increase_stock(product_id=product.id, data=req, db=db, current_user=user_a)

    assert isinstance(res, StockAdjustmentResponse)
    assert res.product_id == product.id
    assert res.product_name == "Mousepad"
    assert res.previous_quantity == 10
    assert res.updated_quantity == 25
    assert res.changed_quantity == 15
    assert res.message == "Stock increased successfully"

    # Verify persisted in database
    db.refresh(product)
    assert product.quantity == 25


# 2. Successful stock decrease
def test_successful_stock_decrease(db):
    user_a, _, org_a, _ = setup_orgs_and_users(db)

    product = Product(
        name="Keyboard",
        sku="KB-002",
        price=Decimal("45.00"),
        quantity=20,
        low_stock_threshold=5,
        organization_id=org_a.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    req = StockAdjustmentRequest(quantity=7)
    res = decrease_stock(product_id=product.id, data=req, db=db, current_user=user_a)

    assert isinstance(res, StockAdjustmentResponse)
    assert res.product_id == product.id
    assert res.previous_quantity == 20
    assert res.updated_quantity == 13
    assert res.changed_quantity == 7
    assert res.message == "Stock decreased successfully"

    db.refresh(product)
    assert product.quantity == 13


# 3. Stock increase with zero quantity
def test_stock_increase_with_zero_quantity():
    with pytest.raises(ValidationError) as exc_info:
        StockAdjustmentRequest(quantity=0)
    assert "greater than 0" in str(exc_info.value)


# 4. Stock increase with negative quantity
def test_stock_increase_with_negative_quantity():
    with pytest.raises(ValidationError) as exc_info:
        StockAdjustmentRequest(quantity=-5)
    assert "greater than 0" in str(exc_info.value)


# 5. Stock decrease with zero quantity
def test_stock_decrease_with_zero_quantity():
    with pytest.raises(ValidationError) as exc_info:
        StockAdjustmentRequest(quantity=0)
    assert "greater than 0" in str(exc_info.value)


# 6. Stock decrease with negative quantity
def test_stock_decrease_with_negative_quantity():
    with pytest.raises(ValidationError) as exc_info:
        StockAdjustmentRequest(quantity=-10)
    assert "greater than 0" in str(exc_info.value)


# 7. Decrease quantity greater than available stock (Insufficient stock -> 400)
def test_decrease_quantity_greater_than_available_stock(db):
    user_a, _, org_a, _ = setup_orgs_and_users(db)

    product = Product(
        name="Headphones",
        sku="HP-001",
        price=Decimal("99.00"),
        quantity=5,
        low_stock_threshold=2,
        organization_id=org_a.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    req = StockAdjustmentRequest(quantity=10)
    with pytest.raises(HTTPException) as exc_info:
        decrease_stock(product_id=product.id, data=req, db=db, current_user=user_a)

    assert exc_info.value.status_code == 400
    assert "Insufficient stock available" in exc_info.value.detail
    # Quantity must remain untouched
    db.refresh(product)
    assert product.quantity == 5


# 8. Product not found (404)
def test_product_not_found(db):
    user_a, _, _, _ = setup_orgs_and_users(db)

    req = StockAdjustmentRequest(quantity=5)
    with pytest.raises(HTTPException) as exc_info_inc:
        increase_stock(product_id=99999, data=req, db=db, current_user=user_a)
    assert exc_info_inc.value.status_code == 404
    assert exc_info_inc.value.detail == "Product not found"

    with pytest.raises(HTTPException) as exc_info_dec:
        decrease_stock(product_id=99999, data=req, db=db, current_user=user_a)
    assert exc_info_dec.value.status_code == 404
    assert exc_info_dec.value.detail == "Product not found"


# 9. Cross-organization stock access (404)
def test_cross_organization_stock_access(db):
    user_a, user_b, _, org_b = setup_orgs_and_users(db)

    # Product belongs to Org B
    product_b = Product(
        name="Org B Secret Item",
        sku="SEC-B-01",
        price=Decimal("150.00"),
        quantity=20,
        organization_id=org_b.id
    )
    db.add(product_b)
    db.commit()
    db.refresh(product_b)

    # User A tries to increase stock of Org B's product
    req = StockAdjustmentRequest(quantity=5)
    with pytest.raises(HTTPException) as exc_info:
        increase_stock(product_id=product_b.id, data=req, db=db, current_user=user_a)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product not found"


# 10. Cross-organization stock modification (404)
def test_cross_organization_stock_modification(db):
    user_a, user_b, _, org_b = setup_orgs_and_users(db)

    # Product belongs to Org B
    product_b = Product(
        name="Org B Private Item",
        sku="SEC-B-02",
        price=Decimal("200.00"),
        quantity=30,
        organization_id=org_b.id
    )
    db.add(product_b)
    db.commit()
    db.refresh(product_b)

    # User A tries to decrease stock of Org B's product
    req = StockAdjustmentRequest(quantity=10)
    with pytest.raises(HTTPException) as exc_info:
        decrease_stock(product_id=product_b.id, data=req, db=db, current_user=user_a)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product not found"

    # Verify Org B's stock was NOT altered
    db.refresh(product_b)
    assert product_b.quantity == 30


# 11. Low-stock product detection (quantity <= low_stock_threshold)
def test_low_stock_product_detection(db):
    user_a, user_b, org_a, org_b = setup_orgs_and_users(db)

    # Org A: 1 low stock (qty 3, threshold 5), 1 normal stock (qty 20, threshold 5), 1 at threshold (qty 5, threshold 5)
    p_low = Product(name="Low Item", sku="LOW-1", price=Decimal("10.00"), quantity=3, low_stock_threshold=5, organization_id=org_a.id)
    p_exact = Product(name="Exact Item", sku="EXACT-1", price=Decimal("10.00"), quantity=5, low_stock_threshold=5, organization_id=org_a.id)
    p_normal = Product(name="Normal Item", sku="NORM-1", price=Decimal("10.00"), quantity=20, low_stock_threshold=5, organization_id=org_a.id)

    # Org B: 1 low stock item (must NOT leak to User A)
    p_b_low = Product(name="Org B Low Item", sku="B-LOW", price=Decimal("10.00"), quantity=1, low_stock_threshold=5, organization_id=org_b.id)

    db.add_all([p_low, p_exact, p_normal, p_b_low])
    db.commit()

    low_stock_list = get_low_stock_products(db=db, current_user=user_a)
    assert len(low_stock_list) == 2
    low_skus = [p.sku for p in low_stock_list]
    assert "LOW-1" in low_skus
    assert "EXACT-1" in low_skus
    assert "NORM-1" not in low_skus
    assert "B-LOW" not in low_skus  # Data isolation


# 12. No low-stock products returns empty list
def test_no_low_stock_products(db):
    user_a, _, org_a, _ = setup_orgs_and_users(db)

    p1 = Product(name="Plentiful Item", sku="PLEN-1", price=Decimal("10.00"), quantity=50, low_stock_threshold=5, organization_id=org_a.id)
    db.add(p1)
    db.commit()

    low_stock_list = get_low_stock_products(db=db, current_user=user_a)
    assert low_stock_list == []


# 13. Unauthenticated stock requests rejected (401)
def test_unauthenticated_stock_requests(db):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid_or_missing_token", db=db)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


# 14. Verify stock never becomes negative
def test_verify_stock_never_becomes_negative(db):
    user_a, _, org_a, _ = setup_orgs_and_users(db)

    product = Product(
        name="Zero Target",
        sku="ZERO-01",
        price=Decimal("12.00"),
        quantity=3,
        low_stock_threshold=1,
        organization_id=org_a.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Deduction of exact quantity reaches 0 safely
    res = decrease_stock(product_id=product.id, data=StockAdjustmentRequest(quantity=3), db=db, current_user=user_a)
    assert res.updated_quantity == 0
    db.refresh(product)
    assert product.quantity == 0

    # Further deduction of 1 must fail and not allow negative stock
    with pytest.raises(HTTPException) as exc_info:
        decrease_stock(product_id=product.id, data=StockAdjustmentRequest(quantity=1), db=db, current_user=user_a)
    assert exc_info.value.status_code == 400
    db.refresh(product)
    assert product.quantity == 0  # Still 0, never negative
