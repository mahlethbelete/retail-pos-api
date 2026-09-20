from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.config import PAYMENT_METHODS, normalize_payment_method


class CheckoutItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CheckoutPayment(BaseModel):
    payment_method: str = Field(..., min_length=2, max_length=80)
    amount: Decimal = Field(..., gt=0)

    @field_validator("payment_method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        value = normalize_payment_method(value)
        if value not in PAYMENT_METHODS:
            raise ValueError(
                "Payment method must be cash, telebirr, card, or bank_transfer"
            )
        return value


class SaleCheckout(BaseModel):
    customer_id: int | None = Field(None, gt=0)
    items: list[CheckoutItem] = Field(..., min_length=1)
    payments: list[CheckoutPayment] = Field(..., min_length=1)


class SaleItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_item_id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    sale_id: int
    payment_method: str
    amount: Decimal
    payment_date: datetime


class ReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    receipt_id: int
    sale_id: int
    receipt_number: str
    issued_at: datetime


class SaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_id: int
    customer_id: int | None
    user_id: int
    sale_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    sale_items: list[SaleItemRead] = []
    payments: list[PaymentRead] = []
    receipt: ReceiptRead | None = None
    change_due: Decimal = Decimal("0.00")