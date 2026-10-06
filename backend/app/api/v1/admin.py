"""Admin API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import CurrentUser, require_role
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.department import Department
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.dashboard import AdminDashboardResponse
from app.schemas.department import DepartmentResponse
from app.schemas.ticket import TicketResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import dashboard_service, ticket_service
from app.services.auth_service import hash_password
from app.services.ticket_service import serialize_ticket

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role("ADMIN"))],
)


@router.get("/dashboard", response_model=AdminDashboardResponse, summary="Admin Dashboard Live Metrics")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
) -> AdminDashboardResponse:
    """Return live dashboard statistics computed from PostgreSQL."""
    return await dashboard_service.get_admin_dashboard(db)


@router.get("/users", response_model=list[UserResponse], summary="List all users with department data")
async def list_users(
    role: str | None = Query(default=None),
    department_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    """Retrieve all users with role and department filters."""
    query = select(User).options(selectinload(User.department)).order_by(User.created_at.desc())
    if role and role.lower() != "all":
        query = query.where(func.lower(User.role) == role.strip().lower())
    if department_id:
        query = query.where(User.department_id == department_id)

    res = await db.execute(query)
    users = res.scalars().all()
    return [UserResponse.from_orm_user(u) for u in users]


@router.post("/users", response_model=UserResponse, summary="Create a new user")
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Admin creates a new user with hashed password in PostgreSQL."""
    existing_res = await db.execute(select(User).where(User.email == data.email.strip().lower()))
    if existing_res.scalar_one_or_none():
        raise ConflictError(f"User with email '{data.email}' already exists")

    hashed = hash_password(data.password) if data.password else None
    role_norm = (data.role or "EMPLOYEE").strip().upper()

    user = User(
        email=data.email.strip().lower(),
        name=data.name.strip(),
        password_hash=hashed,
        role=role_norm,
        department_id=data.department_id,
        phone=data.phone,
        avatar_url=data.avatar_url,
        is_active=data.is_active,
    )
    db.add(user)
    await db.flush()

    # Re-fetch with department
    query = select(User).options(selectinload(User.department)).where(User.id == user.id)
    res = await db.execute(query)
    user_loaded = res.scalar_one()

    return UserResponse.from_orm_user(user_loaded)


@router.put("/users/{user_id}", response_model=UserResponse, summary="Update an existing user")
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Admin updates user profile, role, or department."""
    query = select(User).options(selectinload(User.department)).where(User.id == user_id)
    res = await db.execute(query)
    user = res.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", user_id)

    if data.name is not None:
        user.name = data.name.strip()
    if data.email is not None:
        user.email = data.email.strip().lower()
    if data.role is not None:
        user.role = data.role.strip().upper()
    if data.department_id is not None:
        user.department_id = data.department_id
    if data.phone is not None:
        user.phone = data.phone
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password is not None and data.password.strip():
        user.password_hash = hash_password(data.password.strip())

    await db.flush()

    res = await db.execute(select(User).options(selectinload(User.department)).where(User.id == user.id))
    user_loaded = res.scalar_one()
    return UserResponse.from_orm_user(user_loaded)


@router.delete("/users/{user_id}", summary="Delete or deactivate user")
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Deactivate or remove a user."""
    query = select(User).where(User.id == user_id)
    res = await db.execute(query)
    user = res.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", user_id)

    # Soft delete / deactivate
    user.is_active = False
    await db.flush()
    return {"status": "success", "message": f"User {user.email} deactivated successfully."}


@router.get("/tickets", response_model=list[TicketResponse], summary="List all tickets across organization")
async def list_all_tickets(
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    department_id: uuid.UUID | None = Query(default=None),
    sla_status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[TicketResponse]:
    """Admin query for all tickets across departments."""
    tickets = await ticket_service.list_tickets(
        db,
        department_id=department_id,
        status=status,
        priority=priority,
        sla_filter=sla_status,
        skip=skip,
        limit=limit,
    )
    return [serialize_ticket(t) for t in tickets]


@router.get("/departments", response_model=list[DepartmentResponse], summary="List all departments")
async def list_departments(
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentResponse]:
    """Retrieve all registered departments."""
    res = await db.execute(select(Department).order_by(Department.name.asc()))
    depts = res.scalars().all()
    return [DepartmentResponse.model_validate(d) for d in depts]
