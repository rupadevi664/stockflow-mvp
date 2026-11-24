import pytest
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.organization import Organization
from app.models.user import User
from app.models.product import Product
from app.schemas.dashboard import DashboardSummaryResponse, InventoryValueResponse
from app.routes.dashboard import (
    get_dashboard_summary,
    get_dashboard_low_stock,
    get_inventory_value
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


def setup_dashboard_data(db):
    org_a = Organization(name="Dashboard Org A")
    org_b = Organization(name="Dashboard Org B")
    org_c = Organization(name="Empty Org C")
    db.add_all([org_a, org_b, org_c])
    db.commit()
    db.refresh(org_a)
    db.refresh(org_b)
    db.refresh(org_c)

    user_a = User(
        name="User A",
        email="user_a@dash.com",
        password_hash="mock_hash_a",
        organization_id=org_a.id
    )
    user_b = User(
        name="User B",
        email="user_b@dash.com",
        password_hash="mock_hash_b",
        organization_id=org_b.id
    )
    user_c = User(
        name="User C",
        email="user_c@dash.com",
        password_hash="mock_hash_c",
        organization_id=org_c.id
    )
    db.add_all([user_a, user_b, user_c])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)
    db.refresh(user_c)

    # Org A products:
    # 1. Normal stock: 10 units @ 10.00 = 100.00, threshold 5
    p1 = Product(name="Item 1", sku="SKU-A-1", price=Decimal("10.00"), quantity=10, low_stock_threshold=5, organization_id=org_a.id)
    # 2. Low stock: 4 units @ 25.50 = 102.00, threshold 5 (4 <= 5)
    p2 = Product(name="Item 2", sku="SKU-A-2", price=Decimal("25.50"), quantity=4, low_stock_threshold=5, organization_id=org_a.id)
    # 3. Out of stock: 0 units @ 50.00 = 0.00, threshold 2 (0 <= 2, 0 == 0)
    p3 = Product(name="Item 3", sku="SKU-A-3", price=Decimal("50.00"), quantity=0, low_stock_threshold=2, organization_id=org_a.id)

    # Org B products:
    # Isolated item: 2 units @ 100.00 = 200.00, threshold 1
    p4 = Product(name="Item B", sku="SKU-B-1", price=Decimal("100.00"), quantity=2, low_stock_threshold=1, organization_id=org_b.id)

    db.add_all([p1, p2, p3, p4])
    db.commit()

    return user_a, user_b, user_c, org_a, org_b, org_c


# 1. Dashboard summary with products
def test_dashboard_summary_with_products(db):
    user_a, _, _, _, _, _ = setup_dashboard_data(db)

    summary = get_dashboard_summary(db=db, current_user=user_a)
    assert isinstance(summary, DashboardSummaryResponse)
    assert summary.total_products == 3
    assert summary.total_stock_quantity == 14
    assert summary.low_stock_products == 2
    assert summary.out_of_stock_products == 1
    assert summary.total_inventory_value == Decimal("202.00")


# 2. Total product count calculation
def test_total_product_count(db):
    user_a, _, _, _, _, _ = setup_dashboard_data(db)

    summary = get_dashboard_summary(db=db, current_user=user_a)
    assert summary.total_products == 3


# 3. Total stock quantity calculation
def test_total_stock_quantity(db):
    user_a, _, _, _, _, _ = setup_dashboard_data(db)

    summary = get_dashboard_summary(db=db, current_user=user_a)
    # 10 + 4 + 0 = 14
    assert summary.total_stock_quantity == 14


# 4. Low-stock count calculation (quantity <= low_stock_threshold)
def test_low_stock_count(db):
    user_a, _, _, _, _, _ = setup_dashboard_data(db)

    summary = get_dashboard_summary(db=db, current_user=user_a)
    # Item 2 (qty 4 <= 5) and Item 3 (qty 0 <= 2)
    assert summary.low_stock_products == 2


# 5. Out-of-stock count calculation (quantity == 0)
def test_out_of_stock_count(db):
    user_a, _, _, _, _, _ = setup_dashboard_data(db)

    summary = get_dashboard_summary(db=db, current_user=user_a)
    # Item 3 (qty 0)
    assert summary.out_of_stock_products == 1


# 6. Inventory value calculation (SUM of price * quantity)
def test_inventory_value_calculation(db):
    user_a, _, _, _, _, _ = setup_dashboard_data(db)

    summary = get_dashboard_summary(db=db, current_user=user_a)
    # (10 * 10.00) + (4 * 25.50) + (0 * 50.00) = 100.00 + 102.00 + 0 = 202.00
    assert summary.total_inventory_value == Decimal("202.00")


# 7. Empty organization dashboard (safely returns zeros, no nulls)
def test_empty_organization_dashboard(db):
    _, _, user_c, _, _, _ = setup_dashboard_data(db)

    summary = get_dashboard_summary(db=db, current_user=user_c)
    assert summary.total_products == 0
    assert summary.total_stock_quantity == 0
    assert summary.low_stock_products == 0
    assert summary.out_of_stock_products == 0
    assert summary.total_inventory_value == Decimal("0.00")


# 8. Organization data isolation (Org A vs Org B)
def test_organization_data_isolation(db):
    user_a, user_b, _, _, _, _ = setup_dashboard_data(db)

    summary_a = get_dashboard_summary(db=db, current_user=user_a)
    summary_b = get_dashboard_summary(db=db, current_user=user_b)

    # Org A has 3 products, Org B has 1 product
    assert summary_a.total_products == 3
    assert summary_b.total_products == 1

    # Org A stock is 14, Org B stock is 2
    assert summary_a.total_stock_quantity == 14
    assert summary_b.total_stock_quantity == 2

    # Org A value is 202.00, Org B value is 200.00
    assert summary_a.total_inventory_value == Decimal("202.00")
    assert summary_b.total_inventory_value == Decimal("200.00")


# 9. Low-stock product listing (GET /dashboard/low-stock)
def test_low_stock_product_listing(db):
    user_a, _, _, _, _, _ = setup_dashboard_data(db)

    low_stock_items = get_dashboard_low_stock(db=db, current_user=user_a)
    assert len(low_stock_items) == 2
    skus = [p.sku for p in low_stock_items]
    assert "SKU-A-2" in skus
    assert "SKU-A-3" in skus
    assert "SKU-A-1" not in skus


# 10. Inventory value endpoint (GET /dashboard/inventory-value)
def test_inventory_value_endpoint(db):
    user_a, _, user_c, _, _, _ = setup_dashboard_data(db)

    # Populated org
    val_a = get_inventory_value(db=db, current_user=user_a)
    assert isinstance(val_a, InventoryValueResponse)
    assert val_a.total_inventory_value == Decimal("202.00")
    assert val_a.total_stock_quantity == 14
    assert val_a.total_products == 3

    # Empty org
    val_c = get_inventory_value(db=db, current_user=user_c)
    assert val_c.total_inventory_value == Decimal("0.00")
    assert val_c.total_stock_quantity == 0
    assert val_c.total_products == 0


# 11. Unauthenticated access rejection
def test_unauthenticated_access_rejection(db):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid_token_header", db=db)
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail
