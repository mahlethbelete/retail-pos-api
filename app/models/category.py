from sqlalchemy import (
    Column,
    Integer,
    String,
)

from sqlalchemy.orm import relationship
from database import Base


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    

    products = relationship("Product", back_populates="category")
