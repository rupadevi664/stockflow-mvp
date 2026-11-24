import pytest
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.organization import Organization
from app.models.user import User
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDeleteResponse
)
from app.routes.products import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product
)
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


# Helper to create test organizations and users
def setup_test_users(db):
    org_a = Organization(name="Organization Alpha")
    org_b = Organization(name="Organization Beta")
    db.add_all([org_a, org_b])
    db.commit()
    db.refresh(org_a)
    db.refresh(org_b)

    user_a = User(
        name="Alice Alpha",
        email="alice@alpha.com",
        password_hash="mock_hash_a",
        organization_id=org_a.id
    )
    user_b = User(
        name="Bob Beta",
        email="bob@beta.com",
        password_hash="mock_hash_b",
        organization_id=org_b.id
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    return user_a, user_b, org_a, org_b


# 1. Product creation success
def test_product_creation_success(db):
    user_a, _, org_a, _ = setup_test_users(db)

    product_in = ProductCreate(
        name="Wireless Keyboard",
        sku="KB-001",
        description="Compact wireless mechanical keyboard",
        price=Decimal("89.99"),
        quantity=30,
        low_stock_threshold=5
    )

    created = create_product(data=product_in, db=db, current_user=user_a)

    assert created.id is not None
    assert created.name == "Wireless Keyboard"
    assert created.sku == "KB-001"
    assert created.price == Decimal("89.99")
    assert created.quantity == 30
    assert created.low_stock_threshold == 5
    assert created.organization_id == org_a.id


# 2. Product creation with duplicate SKU in the same organization
def test_product_creation_duplicate_sku_same_org(db):
    user_a, _, _, _ = setup_test_users(db)

    product_in = ProductCreate(
        name="Product 1",
        sku="DUPLICATE-SKU",
        price=Decimal("19.99"),
        quantity=10
    )
    create_product(data=product_in, db=db, current_user=user_a)

    # Attempt to create another product with the same SKU in Org A
    duplicate_in = ProductCreate(
        name="Product 2",
        sku="DUPLICATE-SKU",
        price=Decimal("29.99"),
        quantity=5
    )
    with pytest.raises(HTTPException) as exc_info:
        create_product(data=duplicate_in, db=db, current_user=user_a)

    assert exc_info.value.status_code == 409
    assert "already exists in your organization" in exc_info.value.detail


# 3. Same SKU allowed in different organizations
def test_same_sku_allowed_in_different_organizations(db):
    user_a, user_b, org_a, org_b = setup_test_users(db)

    shared_sku = "GLOBAL-STYLE-SKU"
    p_a = create_product(
        data=ProductCreate(name="Item in A", sku=shared_sku, price=Decimal("10.00"), quantity=5),
        db=db,
        current_user=user_a
    )

    # Org B can use the same SKU without conflict
    p_b = create_product(
        data=ProductCreate(name="Item in B", sku=shared_sku, price=Decimal("15.00"), quantity=8),
        db=db,
        current_user=user_b
    )

    assert p_a.sku == p_b.sku
    assert p_a.organization_id == org_a.id
    assert p_b.organization_id == org_b.id
    assert p_a.id != p_b.id


# 4. Retrieve all products (isolated to user's organization)
def test_retrieve_all_products(db):
    user_a, user_b, org_a, org_b = setup_test_users(db)

    # Create 3 products for Org A
    for i in range(3):
        create_product(
            data=ProductCreate(name=f"Alpha Product {i}", sku=f"SKU-A-{i}", price=Decimal("10.00"), quantity=5),
            db=db,
            current_user=user_a
        )

    # Create 2 products for Org B
    for i in range(2):
        create_product(
            data=ProductCreate(name=f"Beta Product {i}", sku=f"SKU-B-{i}", price=Decimal("20.00"), quantity=10),
            db=db,
            current_user=user_b
        )

    # User A retrieves only Org A's products
    products_a = get_products(skip=0, limit=100, db=db, current_user=user_a)
    assert len(products_a) == 3
    assert all(p.organization_id == org_a.id for p in products_a)

    # User B retrieves only Org B's products
    products_b = get_products(skip=0, limit=100, db=db, current_user=user_b)
    assert len(products_b) == 2
    assert all(p.organization_id == org_b.id for p in products_b)


# 5. Pagination
def test_pagination(db):
    user_a, _, _, _ = setup_test_users(db)

    for i in range(10):
        create_product(
            data=ProductCreate(name=f"Paginated Item {i}", sku=f"PG-SKU-{i:02d}", price=Decimal("5.00"), quantity=i),
            db=db,
            current_user=user_a
        )

    # Page 1: 3 items
    page_1 = get_products(skip=0, limit=3, db=db, current_user=user_a)
    assert len(page_1) == 3

    # Page 2: 3 items
    page_2 = get_products(skip=3, limit=3, db=db, current_user=user_a)
    assert len(page_2) == 3
    assert page_1[0].id != page_2[0].id

    # Page 4: Remaining 1 item
    page_4 = get_products(skip=9, limit=3, db=db, current_user=user_a)
    assert len(page_4) == 1


# 6. Search by name
def test_search_by_name(db):
    user_a, _, _, _ = setup_test_users(db)

    create_product(data=ProductCreate(name="Gaming Monitor", sku="MON-01", price=Decimal("299.99")), db=db, current_user=user_a)
    create_product(data=ProductCreate(name="Office Desk", sku="DSK-01", price=Decimal("149.99")), db=db, current_user=user_a)
    create_product(data=ProductCreate(name="Gaming Chair", sku="CHR-01", price=Decimal("199.99")), db=db, current_user=user_a)

    results = get_products(search="Gaming", db=db, current_user=user_a)
    assert len(results) == 2
    names = [p.name for p in results]
    assert "Gaming Monitor" in names
    assert "Gaming Chair" in names
    assert "Office Desk" not in names


# 7. Search by SKU
def test_search_by_sku(db):
    user_a, _, _, _ = setup_test_users(db)

    create_product(data=ProductCreate(name="Item 1", sku="SEARCH-SKU-99", price=Decimal("10.00")), db=db, current_user=user_a)
    create_product(data=ProductCreate(name="Item 2", sku="OTHER-SKU-01", price=Decimal("20.00")), db=db, current_user=user_a)

    results = get_products(search="99", db=db, current_user=user_a)
    assert len(results) == 1
    assert results[0].sku == "SEARCH-SKU-99"


# 8. Retrieve a single product
def test_retrieve_single_product(db):
    user_a, _, _, _ = setup_test_users(db)

    created = create_product(
        data=ProductCreate(name="Desk Lamp", sku="LMP-01", price=Decimal("34.50"), quantity=15),
        db=db,
        current_user=user_a
    )

    retrieved = get_product(product_id=created.id, db=db, current_user=user_a)
    assert retrieved.id == created.id
    assert retrieved.name == "Desk Lamp"
    assert retrieved.price == Decimal("34.50")


# 9. Update product successfully
def test_update_product_success(db):
    user_a, _, _, _ = setup_test_users(db)

    created = create_product(
        data=ProductCreate(name="Old Name", sku="UPD-001", price=Decimal("50.00"), quantity=20),
        db=db,
        current_user=user_a
    )

    update_in = ProductUpdate(
        name="Updated Name",
        price=Decimal("75.00"),
        quantity=35
    )
    updated = update_product(product_id=created.id, data=update_in, db=db, current_user=user_a)

    assert updated.id == created.id
    assert updated.name == "Updated Name"
    assert updated.price == Decimal("75.00")
    assert updated.quantity == 35
    assert updated.sku == "UPD-001"  # Unchanged field remains intact


# 10. Update with duplicate SKU
def test_update_with_duplicate_sku(db):
    user_a, _, _, _ = setup_test_users(db)

    p1 = create_product(data=ProductCreate(name="Item 1", sku="SKU-AAA", price=Decimal("10.00")), db=db, current_user=user_a)
    p2 = create_product(data=ProductCreate(name="Item 2", sku="SKU-BBB", price=Decimal("20.00")), db=db, current_user=user_a)

    # Attempt to update p2 with p1's SKU
    update_in = ProductUpdate(sku="SKU-AAA")
    with pytest.raises(HTTPException) as exc_info:
        update_product(product_id=p2.id, data=update_in, db=db, current_user=user_a)

    assert exc_info.value.status_code == 409
    assert "already exists in your organization" in exc_info.value.detail


# 11. Delete product successfully
def test_delete_product_success(db):
    user_a, _, _, _ = setup_test_users(db)

    created = create_product(
        data=ProductCreate(name="To Delete", sku="DEL-01", price=Decimal("10.00")),
        db=db,
        current_user=user_a
    )

    response = delete_product(product_id=created.id, db=db, current_user=user_a)
    assert isinstance(response, ProductDeleteResponse)
    assert response.id == created.id
    assert response.message == "Product deleted successfully"

    # Verify product no longer exists
    with pytest.raises(HTTPException) as exc_info:
        get_product(product_id=created.id, db=db, current_user=user_a)
    assert exc_info.value.status_code == 404


# 12. Access product belonging to another organization (404 Not Found)
def test_access_product_belonging_to_another_organization(db):
    user_a, user_b, _, _ = setup_test_users(db)

    # Org B creates a product
    p_b = create_product(data=ProductCreate(name="Secret B", sku="SEC-B", price=Decimal("100.00")), db=db, current_user=user_b)

    # User A attempts to view Org B's product
    with pytest.raises(HTTPException) as exc_info:
        get_product(product_id=p_b.id, db=db, current_user=user_a)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product not found"


# 13. Update product belonging to another organization (404 Not Found)
def test_update_product_belonging_to_another_organization(db):
    user_a, user_b, _, _ = setup_test_users(db)

    p_b = create_product(data=ProductCreate(name="Item B", sku="ITM-B", price=Decimal("100.00")), db=db, current_user=user_b)

    # User A attempts to update Org B's product
    with pytest.raises(HTTPException) as exc_info:
        update_product(product_id=p_b.id, data=ProductUpdate(name="Hijacked"), db=db, current_user=user_a)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product not found"


# 14. Delete product belonging to another organization (404 Not Found)
def test_delete_product_belonging_to_another_organization(db):
    user_a, user_b, _, _ = setup_test_users(db)

    p_b = create_product(data=ProductCreate(name="Item B", sku="ITM-B", price=Decimal("100.00")), db=db, current_user=user_b)

    # User A attempts to delete Org B's product
    with pytest.raises(HTTPException) as exc_info:
        delete_product(product_id=p_b.id, db=db, current_user=user_a)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product not found"


# 15. Reject unauthenticated requests
def test_reject_unauthenticated_requests(db):
    # Calling get_current_user with invalid token must raise 401
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid_or_missing_token", db=db)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail
