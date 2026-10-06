"""Tickets API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.schemas.ticket import (
    TicketCommentCreate,
    TicketCommentResponse,
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketUpdate,
)
from app.services import ticket_service
from app.services.ticket_service import serialize_ticket

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, summary="Create a new support ticket")
async def create_ticket(
    data: TicketCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Create a ticket in PostgreSQL. Requester ID is always obtained from JWT user."""
    ticket = await ticket_service.create_ticket(db, creator=current_user, data=data)
    return serialize_ticket(ticket)


@router.get("", response_model=TicketListResponse, summary="List tickets with filtering")
async def list_tickets(
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    sla_status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    current_user: CurrentUser = None,  # type: ignore[assignment]
    db: AsyncSession = Depends(get_db),
) -> TicketListResponse:
    """Retrieve tickets scoped to user role or filters."""
    # Scope based on role:
    # ADMIN -> all
    # TEAM_LEAD -> department tickets
    # EMPLOYEE -> tickets created or assigned to them
    dept_id = None
    req_id = None
    assigned_id = None

    role = current_user.role.upper()
    if role == "TEAM_LEAD":
        dept_id = current_user.department_id
    elif role == "EMPLOYEE":
        # In general list, employee sees their created tickets unless explicitly filtering
        req_id = current_user.id

    tickets = await ticket_service.list_tickets(
        db,
        department_id=dept_id,
        requester_id=req_id,
        assigned_to=assigned_id,
        status=status,
        priority=priority,
        sla_filter=sla_status,
        skip=skip,
        limit=limit,
    )

    items = [serialize_ticket(t) for t in tickets]
    return TicketListResponse(items=items, total=len(items))


@router.get("/{ticket_id}", response_model=TicketResponse, summary="Get ticket by UUID or Ticket Number")
async def get_ticket(
    ticket_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Retrieve ticket details."""
    ticket = None
    try:
        t_uuid = uuid.UUID(ticket_id)
        ticket = await ticket_service.get_ticket_by_id(db, t_uuid)
    except (ValueError, TypeError):
        ticket = await ticket_service.get_ticket_by_number(db, ticket_id)

    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    # Permission check for employee
    role = current_user.role.upper()
    if role == "EMPLOYEE":
        if ticket.requester_id != current_user.id and ticket.assigned_to != current_user.id:
            raise ForbiddenError("You do not have access to view this ticket")
    elif role == "TEAM_LEAD":
        if current_user.department_id and ticket.department_id != current_user.department_id:
            raise ForbiddenError("This ticket belongs to another department")

    return serialize_ticket(ticket)


@router.put("/{ticket_id}", response_model=TicketResponse, summary="Update ticket details")
async def update_ticket(
    ticket_id: uuid.UUID,
    data: TicketUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Update ticket fields."""
    ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    if data.status:
        ticket = await ticket_service.update_ticket_status(db, ticket.id, current_user, data.status)
    if data.resolution_notes:
        ticket = await ticket_service.resolve_ticket(db, ticket.id, current_user, data.resolution_notes)

    return serialize_ticket(ticket)


@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse, summary="Add comment to ticket")
async def add_comment(
    ticket_id: uuid.UUID,
    data: TicketCommentCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TicketCommentResponse:
    """Add a comment or internal note."""
    comment = await ticket_service.add_comment(
        db,
        ticket_id=ticket_id,
        user=current_user,
        comment_text=data.comment,
        is_internal=data.is_internal,
    )
    return TicketCommentResponse(
        id=comment.id,
        ticket_id=comment.ticket_id,
        user_id=comment.user_id,
        author_name=current_user.name,
        author_role=current_user.role,
        comment=comment.comment,
        is_internal=comment.is_internal,
        created_at=comment.created_at,
    )


@router.get("/{ticket_id}/comments", response_model=list[TicketCommentResponse], summary="Get ticket comments")
async def get_comments(
    ticket_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[TicketCommentResponse]:
    """List comments for a ticket."""
    ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    role = current_user.role.upper()
    comments = []
    for c in ticket.comments:
        # Hide internal notes from normal employee requester
        if c.is_internal and role == "EMPLOYEE" and ticket.assigned_to != current_user.id:
            continue
        comments.append(
            TicketCommentResponse(
                id=c.id,
                ticket_id=c.ticket_id,
                user_id=c.user_id,
                author_name=c.user.name if c.user else "System",
                author_role=c.user.role if c.user else "SYSTEM",
                comment=c.comment,
                is_internal=c.is_internal,
                created_at=c.created_at,
            )
        )
    return comments
