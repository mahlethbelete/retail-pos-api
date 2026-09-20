from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_staff
from models.user import User
from schemas.sale import SaleCreate, SaleRead, SaleUpdate
from services import sale as sale_service

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("/", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return sale_service.create_sale(db, data)


@router.get("/", response_model=list[SaleRead])
def list_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.list_sales(db)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.get_sale(db, sale_id)


@router.put("/{sale_id}", response_model=SaleRead)
def update_sale(
    sale_id: int,
    data: SaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return sale_service.update_sale(db, sale_id, data)


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    sale_service.delete_sale(db, sale_id)