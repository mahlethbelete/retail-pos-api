from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ROLES = {"cashier", "manager", "admin"}


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    role: str = "cashier"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.lower()
        if value not in ROLES:
            raise ValueError("Role must be cashier, manager, or admin")
        return value


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8, max_length=128)
    role: str | None = None
    is_active: bool | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.lower()
        if value not in ROLES:
            raise ValueError("Role must be cashier, manager, or admin")
        return value


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    is_active: bool
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead