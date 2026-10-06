"""Pydantic v2 schemas for User."""

from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "EMPLOYEE"
    department_id: uuid.UUID | None = None
    phone: str | None = None
    avatar_url: str | None = None


class UserCreate(UserBase):
    password: str
    is_active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    department_id: uuid.UUID | None = None
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    role: str
    department_id: uuid.UUID | None = None
    department_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_user(cls, user: object) -> "UserResponse":
        dept_name = None
        dept = getattr(user, "department", None)
        if dept:
            dept_name = dept.name

        return cls(
            id=getattr(user, "id"),
            email=getattr(user, "email"),
            name=getattr(user, "name", ""),
            role=getattr(user, "role", "EMPLOYEE"),
            department_id=getattr(user, "department_id", None),
            department_name=dept_name,
            phone=getattr(user, "phone", None),
            avatar_url=getattr(user, "avatar_url", None),
            is_active=getattr(user, "is_active", True),
            is_superuser=getattr(user, "is_superuser", False),
            created_at=getattr(user, "created_at"),
            updated_at=getattr(user, "updated_at"),
        )


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    size: int
