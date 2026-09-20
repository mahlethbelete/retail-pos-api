from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_manager_or_admin
from models.user import User
from repositories.user import user_repository
from schemas.user import LoginResponse, UserCreate, UserRead
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate(db, form_data.username, form_data.password)
    return auth_service.make_login_response(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_first_user(data: UserCreate, db: Session = Depends(get_db)):
    if user_repository.count(db) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled. A manager or admin must create users.",
        )

    payload = data.model_dump()
    payload["role"] = "admin"
    return auth_service.create_user(db, payload)


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_staff_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    if current_user.role.lower() == "manager" and data.role.lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers cannot create admin accounts",
        )
    return auth_service.create_user(db, data.model_dump())
