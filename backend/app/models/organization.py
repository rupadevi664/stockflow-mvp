from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False
    )

    contact_email = Column(
        String(150),
        nullable=True
    )

    contact_phone = Column(
        String(50),
        nullable=True
    )

    default_low_stock_threshold = Column(
        Integer,
        nullable=False,
        default=5,
        server_default="5"
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

    users = relationship(
        "User",
        back_populates="organization"
    )

    products = relationship(
        "Product",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
