from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id", ondelete="CASCADE"), nullable=False, unique=True)
    receipt_number = Column(String(50), nullable=False, unique=True)
    issued_at = Column(DateTime, server_default=func.now(), nullable=False)

    sale = relationship("Sale", back_populates="receipt")