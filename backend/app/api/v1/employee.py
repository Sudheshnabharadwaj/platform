"""Employee API endpoints."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, require_role
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.schemas.dashboard import EmployeeDashboardResponse
from app.schemas.ticket import TicketResponse, TicketStatusRequest
from app.services import dashboard_service, ticket_service
from app.services.ticket_service import serialize_ticket

router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    dependencies=[Depends(require_role("EMPLOYEE", "TEAM_LEAD", "ADMIN"))],
)


@router.get("/dashboard", response_model=EmployeeDashboardResponse, summary="Employee Dashboard Metrics")
async def get_dashboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> EmployeeDashboardResponse:
    """Return live dashboard statistics for the logged-in employee."""
    return await dashboard_service.get_employee_dashboard(db, current_user)


@router.get("/tickets", response_model=list[TicketResponse], summary="Get tickets created by employee")
async def get_created_tickets(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[TicketResponse]:
    """Retrieve all tickets requested/created by the authenticated employee."""
    tickets = await ticket_service.list_tickets(
        db,
        requester_id=current_user.id,
    )
    return [serialize_ticket(t) for t in tickets]


@router.get("/assigned-tickets", response_model=list[TicketResponse], summary="Get tickets assigned to employee")
async def get_assigned_tickets(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[TicketResponse]:
    """Retrieve all tickets assigned to the authenticated employee."""
    tickets = await ticket_service.list_tickets(
        db,
        assigned_to=current_user.id,
    )
    return [serialize_ticket(t) for t in tickets]


@router.get("/tickets/{ticket_id}", response_model=TicketResponse, summary="Get single ticket details")
async def get_ticket_details(
    ticket_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Retrieve ticket details if employee is requester or assignee."""
    ticket = None
    try:
        t_uuid = uuid.UUID(ticket_id)
        ticket = await ticket_service.get_ticket_by_id(db, t_uuid)
    except (ValueError, TypeError):
        ticket = await ticket_service.get_ticket_by_number(db, ticket_id)

    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    # Validate employee access
    if (
        current_user.role.upper() == "EMPLOYEE"
        and ticket.requester_id != current_user.id
        and ticket.assigned_to != current_user.id
    ):
        raise ForbiddenError("You are not authorized to view this ticket")

    return serialize_ticket(ticket)


@router.put("/tickets/{ticket_id}/status", response_model=TicketResponse, summary="Update status of assigned ticket")
async def update_assigned_ticket_status(
    ticket_id: uuid.UUID,
    data: TicketStatusRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Employee updates status of a ticket assigned to them."""
    ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    if current_user.role.upper() == "EMPLOYEE" and ticket.assigned_to != current_user.id:
        raise ForbiddenError("You can only update the status of tickets assigned to you")

    norm_status = data.status.strip().upper()
    if norm_status == "RESOLVED":
        ticket = await ticket_service.resolve_ticket(
            db,
            ticket_id=ticket.id,
            user=current_user,
            resolution_notes=data.note or "Resolved by assignee.",
        )
    else:
        ticket = await ticket_service.update_ticket_status(
            db,
            ticket_id=ticket.id,
            user=current_user,
            new_status=norm_status,
            note=data.note,
        )

    return serialize_ticket(ticket)
