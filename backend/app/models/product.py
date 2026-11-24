from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False,
        index=True
    )

    sku = Column(
        String(100),
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    price = Column(
        Numeric(10, 2),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    low_stock_threshold = Column(
        Integer,
        nullable=False,
        default=5
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    organization = relationship(
        "Organization",
        back_populates="products"
    )

    # Constraints: SKU is unique within an organization, not globally
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "sku",
            name="uq_organization_sku"
        ),
    )
