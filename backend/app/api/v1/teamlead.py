"""Team Lead API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import CurrentUser, require_role
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.dashboard import TeamLeadDashboardResponse
from app.schemas.ticket import TicketAssignRequest, TicketResponse, TicketStatusRequest
from app.schemas.user import UserResponse
from app.services import dashboard_service, ticket_service
from app.services.ticket_service import serialize_ticket

router = APIRouter(
    prefix="/teamlead",
    tags=["Team Lead"],
    dependencies=[Depends(require_role("TEAM_LEAD", "ADMIN"))],
)


@router.get("/dashboard", response_model=TeamLeadDashboardResponse, summary="Team Lead Dashboard Metrics")
async def get_dashboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TeamLeadDashboardResponse:
    """Return live metrics calculated from PostgreSQL for the Team Lead's department."""
    return await dashboard_service.get_team_lead_dashboard(db, current_user)


@router.get("/tickets", response_model=list[TicketResponse], summary="Get department tickets for Team Lead")
async def get_team_tickets(
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    sla_status: str | None = Query(default=None),
    current_user: CurrentUser = None,  # type: ignore[assignment]
    db: AsyncSession = Depends(get_db),
) -> list[TicketResponse]:
    """Retrieve tickets scoped to the Team Lead's department."""
    tickets = await ticket_service.list_tickets(
        db,
        department_id=current_user.department_id,
        status=status,
        priority=priority,
        sla_filter=sla_status,
    )
    return [serialize_ticket(t) for t in tickets]


@router.get("/employees", response_model=list[UserResponse], summary="List active department employees")
async def get_department_employees(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    """Return active employees belonging to the same department as the Team Lead."""
    query = (
        select(User)
        .options(selectinload(User.department))
        .where(
            User.is_active == True,  # noqa: E712
        )
    )
    if current_user.role.upper() != "ADMIN" and current_user.department_id:
        query = query.where(User.department_id == current_user.department_id)

    res = await db.execute(query)
    users = res.scalars().all()
    return [UserResponse.from_orm_user(u) for u in users]


@router.post("/tickets/{ticket_id}/assign", response_model=TicketResponse, summary="Assign ticket to department employee")
async def assign_ticket(
    ticket_id: uuid.UUID,
    data: TicketAssignRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Assign ticket to an active department employee."""
    ticket = await ticket_service.assign_ticket(
        db,
        ticket_id=ticket_id,
        team_lead=current_user,
        employee_id=data.employee_id,
    )
    return serialize_ticket(ticket)


@router.put("/tickets/{ticket_id}/status", response_model=TicketResponse, summary="Update ticket status")
async def update_ticket_status(
    ticket_id: uuid.UUID,
    data: TicketStatusRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Update status of a ticket."""
    ticket = await ticket_service.update_ticket_status(
        db,
        ticket_id=ticket_id,
        user=current_user,
        new_status=data.status,
        note=data.note,
    )
    return serialize_ticket(ticket)
