from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import relationship

from database import Base


class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    sale_date = Column(DateTime, server_default=func.now(), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total = Column(Numeric(10, 2), nullable=False, default=0)

    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    sale_items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="sale", cascade="all, delete-orphan"
    )
    receipt = relationship(
        "Receipt", back_populates="sale", uselist=False, cascade="all, delete-orphan"
    )