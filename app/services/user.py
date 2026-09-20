from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import hash_password
from repositories.user import user_repository
from schemas.user import UserCreate, UserUpdate


def get_user(db: Session, id: int):
    user = user_repository.get(db, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


def list_users(db: Session):
    return user_repository.get_all(db)


def create_user(db: Session, data: UserCreate):
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already registered",
        )

    payload = data.model_dump()
    payload["password_hash"] = hash_password(payload.pop("password"))
    payload["role"] = payload.get("role", "cashier").lower()
    return user_repository.create(db, payload)


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user(db, user_id)
    payload = data.model_dump(exclude_unset=True)

    if "password" in payload:
        payload["password_hash"] = hash_password(payload.pop("password"))

    if "username" in payload:
        existing = user_repository.get_by_username(db, payload["username"])
        if existing and existing.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already registered",
            )

    return user_repository.update(db, user, payload)


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    user_repository.delete(db, user)