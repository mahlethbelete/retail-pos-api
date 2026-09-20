from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_staff
from models.user import User
from schemas.receipt import ReceiptCreate, ReceiptRead, ReceiptUpdate
from services import receipt as receipt_service

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("/", response_model=ReceiptRead, status_code=status.HTTP_201_CREATED)
def create_receipt(
    data: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return receipt_service.create_receipt(db, data)


@router.get("/", response_model=list[ReceiptRead])
def list_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return receipt_service.list_receipts(db)


@router.get("/{receipt_id}", response_model=ReceiptRead)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return receipt_service.get_receipt(db, receipt_id)


@router.put("/{receipt_id}", response_model=ReceiptRead)
def update_receipt(
    receipt_id: int,
    data: ReceiptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    return receipt_service.update_receipt(db, receipt_id, data)


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    receipt_service.delete_receipt(db, receipt_id)