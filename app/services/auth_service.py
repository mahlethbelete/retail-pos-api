from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from models.user import User
from repositories.user import user_repository

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired authentication token",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate(db: Session, username: str, password: str) -> User:
    user = user_repository.get_by_username(db, username)

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user account is inactive",
        )

    return user


def create_user(db: Session, data: dict) -> User:
    if user_repository.get_by_username(db, data["username"]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already registered",
        )

    payload = dict(data)
    password = payload.pop("password", None)
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    payload["password_hash"] = hash_password(password)
    payload["role"] = payload.get("role", "cashier").lower()
    payload["is_active"] = True

    return user_repository.create(db, payload)


def get_user_from_token(db: Session, token: str) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise CREDENTIALS_EXCEPTION

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise CREDENTIALS_EXCEPTION

    user = user_repository.get(db, user_id)
    if not user or not user.is_active:
        raise CREDENTIALS_EXCEPTION

    return user


def make_login_response(user: User) -> dict:
    return {
        "access_token": create_access_token(user.user_id, user.role),
        "token_type": "bearer",
        "user": user,
    }