from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_staff
from models.user import User
from schemas.sale_item import SaleItemCreate, SaleItemRead, SaleItemUpdate
from services import sale_item as sale_item_service

router = APIRouter(prefix="/sale-items", tags=["sale-items"])


@router.post("/", response_model=SaleItemRead, status_code=status.HTTP_201_CREATED)
def create_sale_item(
    data: SaleItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return sale_item_service.create_sale_item(db, data)


@router.get("/", response_model=list[SaleItemRead])
def list_sale_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_item_service.list_sale_items(db)


@router.get("/{sale_item_id}", response_model=SaleItemRead)
def get_sale_item(
    sale_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_item_service.get_sale_item(db, sale_item_id)


@router.put("/{sale_item_id}", response_model=SaleItemRead)
def update_sale_item(
    sale_item_id: int,
    data: SaleItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return sale_item_service.update_sale_item(db, sale_item_id, data)


@router.delete("/{sale_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale_item(
    sale_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    sale_item_service.delete_sale_item(db, sale_item_id)