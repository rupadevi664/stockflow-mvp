import pytest
from decimal import Decimal
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.models.organization import Organization
from app.models.user import User
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)


# In-memory SQLite test database for isolated testing
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


# 1. Test Product Schema Validation
def test_product_schema_validation():
    # Valid schema
    valid_data = ProductCreate(
        name="Laptop Stand",
        sku="STN-001",
        description="Ergonomic aluminum stand",
        price=Decimal("49.99"),
        quantity=25,
        low_stock_threshold=5
    )
    assert valid_data.name == "Laptop Stand"
    assert valid_data.price == Decimal("49.99")
    assert valid_data.quantity == 25

    # Negative price rejected
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Invalid Price Item",
            sku="INV-001",
            price=Decimal("-10.00"),
            quantity=5
        )

    # Negative quantity rejected
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Invalid Quantity Item",
            sku="INV-002",
            price=Decimal("10.00"),
            quantity=-1
        )

    # Negative threshold rejected
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Invalid Threshold Item",
            sku="INV-003",
            price=Decimal("10.00"),
            low_stock_threshold=-2
        )


# 2. Test Product Database Model & Unique Constraint Per Organization
def test_product_model_constraints(db):
    org1 = Organization(name="Company A")
    org2 = Organization(name="Company B")
    db.add_all([org1, org2])
    db.commit()

    # Create product in Org 1
    p1 = Product(
        name="Keyboard",
        sku="KB-100",
        price=Decimal("79.99"),
        quantity=15,
        organization_id=org1.id
    )
    db.add(p1)
    db.commit()
    db.refresh(p1)

    assert p1.id is not None
    assert p1.organization.name == "Company A"
    assert org1.products[0].name == "Keyboard"

    # Same SKU in Org 2 must succeed (uniqueness is scoped per organization)
    p2 = Product(
        name="Keyboard Pro",
        sku="KB-100",
        price=Decimal("99.99"),
        quantity=5,
        organization_id=org2.id
    )
    db.add(p2)
    db.commit()
    db.refresh(p2)
    assert p2.id is not None
    assert p2.organization_id == org2.id

    # Duplicate SKU within same organization must fail
    p3 = Product(
        name="Keyboard Duplicate",
        sku="KB-100",
        price=Decimal("69.99"),
        quantity=2,
        organization_id=org1.id
    )
    db.add(p3)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


# Helper to create test user and organization
def create_test_user_and_org(db, org_name="TechCorp", user_email="user@techcorp.com"):
    org = Organization(name=org_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    user = User(
        name="Test User",
        email=user_email,
        password_hash="hash",
        organization_id=org.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, org


# 3. Test Product Creation API
def test_create_product_api(db):
    from app.routes.products import create_product
    user, org = create_test_user_and_org(db, "Org One", "user1@orgone.com")

    product_data = ProductCreate(
        name="Wireless Mouse",
        sku="MOU-101",
        description="Bluetooth optical mouse",
        price=Decimal("29.99"),
        quantity=50,
        low_stock_threshold=10
    )

    created = create_product(data=product_data, db=db, current_user=user)

    assert created.id is not None
    assert created.name == "Wireless Mouse"
    assert created.sku == "MOU-101"
    assert created.price == Decimal("29.99")
    assert created.organization_id == org.id  # Automatically assigned

    # Duplicate SKU in same org must be rejected with 409 Conflict
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create_product(data=product_data, db=db, current_user=user)
    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail.lower()



# 4. Test Cross-Organization SKU Allowance on Creation
def test_cross_org_sku_creation(db):
    from app.routes.products import create_product
    user1, org1 = create_test_user_and_org(db, "Org 1", "u1@org1.com")
    user2, org2 = create_test_user_and_org(db, "Org 2", "u2@org2.com")

    data = ProductCreate(
        name="Shared SKU Item",
        sku="SHARED-001",
        price=Decimal("15.00"),
        quantity=10
    )

    # Org 1 creates product with SHARED-001
    p1 = create_product(data=data, db=db, current_user=user1)
    assert p1.organization_id == org1.id

    # Org 2 creates product with same SHARED-001 -> MUST succeed
    p2 = create_product(data=data, db=db, current_user=user2)
    assert p2.organization_id == org2.id
    assert p2.sku == p1.sku


# 5. Test Product Retrieval (GET /products/ and GET /products/{id})
def test_get_products_api(db):
    from app.routes.products import create_product, get_products, get_product
    from fastapi import HTTPException
    user1, org1 = create_test_user_and_org(db, "Alpha Org", "alpha@test.com")
    user2, org2 = create_test_user_and_org(db, "Beta Org", "beta@test.com")

    # Create 2 products for user1 (Alpha Org)
    create_product(
        data=ProductCreate(name="Item A1", sku="A1-SKU", price=Decimal("10.00"), quantity=5),
        db=db,
        current_user=user1
    )
    p_a2 = create_product(
        data=ProductCreate(name="Item A2", sku="A2-SKU", price=Decimal("20.00"), quantity=8),
        db=db,
        current_user=user1
    )

    # Create 1 product for user2 (Beta Org)
    p_b1 = create_product(
        data=ProductCreate(name="Item B1", sku="B1-SKU", price=Decimal("30.00"), quantity=12),
        db=db,
        current_user=user2
    )

    # GET /products/ for user1 -> Should only return 2 items from Alpha Org
    list_user1 = get_products(skip=0, limit=100, db=db, current_user=user1)
    assert len(list_user1) == 2
    skus = [p.sku for p in list_user1]
    assert "A1-SKU" in skus
    assert "A2-SKU" in skus
    assert "B1-SKU" not in skus

    # GET /products/ for user2 -> Should only return 1 item from Beta Org
    list_user2 = get_products(skip=0, limit=100, db=db, current_user=user2)
    assert len(list_user2) == 1
    assert list_user2[0].sku == "B1-SKU"

    # GET /products/{id} for user1 accessing their own product
    retrieved = get_product(product_id=p_a2.id, db=db, current_user=user1)
    assert retrieved.id == p_a2.id
    assert retrieved.name == "Item A2"

    # GET /products/{id} for user1 accessing user2's product -> 404 Not Found
    with pytest.raises(HTTPException) as exc_info:
        get_product(product_id=p_b1.id, db=db, current_user=user1)
    assert exc_info.value.status_code == 404

    # GET /products/{id} for non-existent product -> 404 Not Found
    with pytest.raises(HTTPException) as exc_info:
        get_product(product_id=99999, db=db, current_user=user1)
    assert exc_info.value.status_code == 404

