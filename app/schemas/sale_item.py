from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleItemBase(BaseModel):
    sale_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    line_total: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemUpdate(BaseModel):
    sale_id: int | None = Field(None, gt=0)
    product_id: int | None = Field(None, gt=0)
    quantity: int | None = Field(None, gt=0)
    unit_price: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)
    line_total: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)


class SaleItemRead(SaleItemBase):
    model_config = ConfigDict(from_attributes=True)

    sale_item_id: int
    line_total: Decimal
