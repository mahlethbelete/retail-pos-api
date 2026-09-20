from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_admin, require_manager_or_admin
from models.user import User
from schemas.user import UserCreate, UserRead, UserUpdate
from services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    if current_user.role.lower() == "manager" and data.role.lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers cannot create admin accounts",
        )
    return user_service.create_user(db, data)


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    return user_service.get_user(db, user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    target = user_service.get_user(db, user_id)

    if current_user.role.lower() == "manager":
        if target.role.lower() == "admin":
            raise HTTPException(403, "Managers cannot modify admin accounts")
        if data.role and data.role.lower() == "admin":
            raise HTTPException(403, "Managers cannot promote users to admin")

    return user_service.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if user_id == current_user.user_id:
        raise HTTPException(400, "You cannot delete your own account")
    user_service.delete_user(db, user_id)