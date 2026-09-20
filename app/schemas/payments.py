from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    sale_id: int
    payment_method: str
    amount: Decimal
    payment_date: datetime | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    sale_id: int | None = None
    payment_method: str | None = None
    amount: Decimal | None = None
    payment_date: datetime | None = None


class PaymentRead(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int