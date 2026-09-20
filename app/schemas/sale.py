from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleBase(BaseModel):
    customer_id: int | None = Field(None, gt=0)
    user_id: int = Field(..., gt=0)
    sale_date: datetime | None = None
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total: Decimal = Field(default=Decimal("0.00"), ge=0)


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    customer_id: int | None = Field(None, gt=0)
    user_id: int | None = Field(None, gt=0)
    sale_date: datetime | None = None
    subtotal: Decimal | None = Field(None, ge=0)
    tax_amount: Decimal | None = Field(None, ge=0)
    total: Decimal | None = Field(None, ge=0)


class SaleRead(SaleBase):
    model_config = ConfigDict(from_attributes=True)

    sale_id: int
    sale_date: datetime
