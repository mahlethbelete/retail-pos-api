from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.payments import payment_repository
from schemas.payments import PaymentCreate, PaymentUpdate


def get_payment(db: Session, id: int):
    payment = payment_repository.get(db, id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


def list_payments(db: Session):
    return payment_repository.get_all(db)


def create_payment(db: Session, data: PaymentCreate):
    return payment_repository.create(db, data.model_dump(exclude_none=True))


def update_payment(db: Session, payment_id: int, data: PaymentUpdate):
    payment = get_payment(db, payment_id)
    return payment_repository.update(
        db, payment, data.model_dump(exclude_unset=True)
    )


def delete_payment(db: Session, payment_id: int):
    payment = get_payment(db, payment_id)
    payment_repository.delete(db, payment)
