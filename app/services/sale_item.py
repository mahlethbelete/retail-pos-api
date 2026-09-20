from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.sale_item import sale_item_repository
from schemas.sale_item import SaleItemCreate, SaleItemUpdate


def get_sale_item(db: Session, id: int):
    sale_item = sale_item_repository.get(db, id)

    if not sale_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale item not found"
        )

    return sale_item


def list_sale_items(db: Session):
    return sale_item_repository.get_all(db)


def create_sale_item(db: Session, data: SaleItemCreate):
    payload = data.model_dump()

    if payload.get("line_total") is None:
        payload["line_total"] = payload["unit_price"] * payload["quantity"]

    return sale_item_repository.create(db, payload)


def update_sale_item(db: Session, sale_item_id: int, data: SaleItemUpdate):
    sale_item = get_sale_item(db, sale_item_id)
    payload = data.model_dump(exclude_unset=True, exclude_none=True)

    if "line_total" not in payload and ("unit_price" in payload or "quantity" in payload):
        unit_price = payload.get("unit_price", sale_item.unit_price)
        quantity = payload.get("quantity", sale_item.quantity)
        payload["line_total"] = unit_price * quantity

    return sale_item_repository.update(db, sale_item, payload)


def delete_sale_item(db: Session, sale_item_id: int):
    sale_item = get_sale_item(db, sale_item_id)
    sale_item_repository.delete(db, sale_item)
