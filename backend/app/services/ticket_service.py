"""Ticket service — core domain business logic, assignment, status workflow, and queries."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.db.models.department import Department
from app.db.models.ticket import Ticket
from app.db.models.ticket_attachment import TicketAttachment
from app.db.models.ticket_comment import TicketComment
from app.db.models.user import User
from app.schemas.ticket import (
    TicketAttachmentResponse,
    TicketCommentResponse,
    TicketCreate,
    TicketResponse,
    TicketUpdate,
)
from app.services.notification_service import create_notification, notify_team_leads_of_department
from app.services.sla_service import calculate_due_date, evaluate_sla


def serialize_ticket(ticket: Ticket) -> TicketResponse:
    """Serialize a Ticket ORM entity into a rich TicketResponse with live SLA values."""
    sla_status, sla_remaining = evaluate_sla(
        priority=ticket.priority,
        created_at=ticket.created_at,
        due_at=ticket.due_at,
        status=ticket.status,
    )

    comments_resp = [
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
        for c in (ticket.comments or [])
    ]

    attachments_resp = [
        TicketAttachmentResponse(
            id=a.id,
            ticket_id=a.ticket_id,
            file_name=a.file_name,
            file_url=a.file_url,
            file_size=a.file_size,
            created_at=a.created_at,
        )
        for a in (ticket.attachments or [])
    ]

    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        title=ticket.title,
        description=ticket.description,
        requester_id=ticket.requester_id,
        requester_name=ticket.requester.name if ticket.requester else "Unknown",
        requester_email=ticket.requester.email if ticket.requester else "",
        assigned_to=ticket.assigned_to,
        assigned_name=ticket.assigned_user.name if ticket.assigned_user else None,
        assigned_email=ticket.assigned_user.email if ticket.assigned_user else None,
        department_id=ticket.department_id,
        department_name=ticket.department.name if ticket.department else "General",
        category=ticket.category,
        sub_category=ticket.sub_category,
        priority=ticket.priority,
        status=ticket.status,
        sla_status=sla_status,
        sla_remaining=sla_remaining,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        due_at=ticket.due_at,
        resolved_at=ticket.resolved_at,
        resolution_notes=ticket.resolution_notes,
        escalated=ticket.escalated,
        escalation_reason=ticket.escalation_reason,
        comments=comments_resp,
        attachments=attachments_resp,
    )


async def generate_ticket_number(db: AsyncSession) -> str:
    """Generate next sequential ticket number like TICK-1001."""
    count_res = await db.execute(select(func.count()).select_from(Ticket))
    count = count_res.scalar() or 0
    return f"TICK-{1001 + count}"


async def create_ticket(
    db: AsyncSession,
    creator: User,
    data: TicketCreate,
) -> Ticket:
    """Create a new ticket in PostgreSQL with auto-assigned SLA and department resolution."""
    # Resolve department
    target_dept_id: uuid.UUID | None = data.department_id

    if not target_dept_id and data.department_name:
        dept_res = await db.execute(
            select(Department).where(func.lower(Department.name) == data.department_name.strip().lower())
        )
        dept = dept_res.scalar_one_or_none()
        if dept:
            target_dept_id = dept.id

    if not target_dept_id:
        if creator.department_id:
            target_dept_id = creator.department_id
        else:
            default_dept_res = await db.execute(select(Department).order_by(Department.name.asc()).limit(1))
            default_dept = default_dept_res.scalar_one_or_none()
            if not default_dept:
                # Create default department if none exists
                default_dept = Department(name="IT Support", description="Technical support & IT operations")
                db.add(default_dept)
                await db.flush()
            target_dept_id = default_dept.id

    priority_norm = (data.priority or "MEDIUM").strip().upper()
    if priority_norm not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        priority_norm = "MEDIUM"

    now = datetime.now(timezone.utc)
    due_at = calculate_due_date(priority_norm, now)
    ticket_num = await generate_ticket_number(db)

    ticket = Ticket(
        ticket_number=ticket_num,
        title=data.title.strip(),
        description=data.description.strip(),
        requester_id=creator.id,
        department_id=target_dept_id,
        category=data.category or "General Support",
        sub_category=data.sub_category,
        priority=priority_norm,
        status="OPEN",
        due_at=due_at,
        created_at=now,
        updated_at=now,
        escalated=False,
    )
    db.add(ticket)
    await db.flush()

    # Initial creation comment
    initial_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=creator.id,
        comment="Ticket created.",
        is_internal=False,
        created_at=now,
    )
    db.add(initial_comment)

    # Attachments
    if data.attachments:
        for att in data.attachments:
            att_entry = TicketAttachment(
                ticket_id=ticket.id,
                user_id=creator.id,
                file_name=att,
                file_url=None,
                file_size=None,
                created_at=now,
            )
            db.add(att_entry)

    await db.flush()

    # Notify team leads of this department
    await notify_team_leads_of_department(
        db,
        department_id=target_dept_id,
        title=f"New Ticket #{ticket.ticket_number}",
        message=f"New ticket '{ticket.title}' submitted by {creator.name} ({ticket.priority} Priority).",
        ticket_id=ticket.id,
    )

    # Re-fetch with full relationships loaded
    return await get_ticket_by_id(db, ticket.id)  # type: ignore[return-value]


async def get_ticket_by_id(
    db: AsyncSession,
    ticket_id: uuid.UUID,
) -> Ticket | None:
    """Fetch ticket with eager loaded relationships."""
    query = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.department),
            selectinload(Ticket.comments).selectinload(TicketComment.user),
            selectinload(Ticket.attachments),
        )
    )
    res = await db.execute(query)
    return res.scalar_one_or_none()


async def get_ticket_by_number(
    db: AsyncSession,
    ticket_number: str,
) -> Ticket | None:
    """Fetch ticket by number string (e.g. 'TICK-1001')."""
    query = (
        select(Ticket)
        .where(func.lower(Ticket.ticket_number) == ticket_number.strip().lower())
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.department),
            selectinload(Ticket.comments).selectinload(TicketComment.user),
            selectinload(Ticket.attachments),
        )
    )
    res = await db.execute(query)
    return res.scalar_one_or_none()


async def list_tickets(
    db: AsyncSession,
    *,
    department_id: uuid.UUID | None = None,
    requester_id: uuid.UUID | None = None,
    assigned_to: uuid.UUID | None = None,
    status: str | None = None,
    priority: str | None = None,
    sla_filter: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Ticket]:
    """Query tickets with optional filtering."""
    query = (
        select(Ticket)
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.department),
            selectinload(Ticket.comments).selectinload(TicketComment.user),
            selectinload(Ticket.attachments),
        )
        .order_by(Ticket.created_at.desc())
    )

    if department_id:
        query = query.where(Ticket.department_id == department_id)
    if requester_id:
        query = query.where(Ticket.requester_id == requester_id)
    if assigned_to:
        query = query.where(Ticket.assigned_to == assigned_to)
    if status and status.lower() != "all":
        query = query.where(func.lower(Ticket.status) == status.strip().lower())
    if priority and priority.lower() != "all":
        query = query.where(func.lower(Ticket.priority) == priority.strip().lower())

    res = await db.execute(query)
    tickets = list(res.scalars().all())

    # SLA filter applied dynamically if requested
    if sla_filter:
        norm_sla = sla_filter.strip().lower()
        filtered = []
        for t in tickets:
            sla_st, _ = evaluate_sla(t.priority, t.created_at, t.due_at, t.status)
            if norm_sla in ("sla risk", "risk") and sla_st == "SLA Risk":
                filtered.append(t)
            elif norm_sla in ("sla breached", "breached") and sla_st == "SLA Breached":
                filtered.append(t)
            elif norm_sla in ("normal", "within sla") and sla_st == "Normal":
                filtered.append(t)
        tickets = filtered

    return tickets[skip : skip + limit]


async def assign_ticket(
    db: AsyncSession,
    ticket_id: uuid.UUID,
    team_lead: User,
    employee_id: uuid.UUID,
) -> Ticket:
    """Team lead assigns ticket to an active employee belonging to the same department."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    # Validate team lead's department (Admins can assign anywhere)
    if team_lead.role.upper() != "ADMIN":
        if team_lead.department_id != ticket.department_id:
            raise ForbiddenError("You can only assign tickets belonging to your own department")

    # Fetch employee
    emp_res = await db.execute(select(User).where(User.id == employee_id))
    employee = emp_res.scalar_one_or_none()
    if not employee:
        raise NotFoundError("Employee", employee_id)

    if not employee.is_active:
        raise BadRequestError("Cannot assign ticket to an inactive employee")

    if team_lead.role.upper() != "ADMIN" and employee.department_id != ticket.department_id:
        raise BadRequestError("Employee must belong to the ticket's department")

    # Update assignment
    ticket.assigned_to = employee.id
    if ticket.status.upper() == "OPEN":
        ticket.status = "IN_PROGRESS"
    ticket.updated_at = datetime.now(timezone.utc)

    # Audit comment
    comment = TicketComment(
        ticket_id=ticket.id,
        user_id=team_lead.id,
        comment=f"Ticket assigned to {employee.name} by {team_lead.name} ({team_lead.role}).",
        is_internal=False,
    )
    db.add(comment)

    # Notification to assigned employee
    await create_notification(
        db,
        user_id=employee.id,
        title=f"New Ticket Assigned: #{ticket.ticket_number}",
        message=f"You have been assigned ticket '{ticket.title}' ({ticket.priority} Priority).",
        ticket_id=ticket.id,
    )

    await db.flush()
    return (await get_ticket_by_id(db, ticket.id))!  # type: ignore[return-value]


async def update_ticket_status(
    db: AsyncSession,
    ticket_id: uuid.UUID,
    user: User,
    new_status: str,
    note: str | None = None,
) -> Ticket:
    """Update ticket status, record timestamps, and notify requester."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    norm_status = new_status.strip().upper()
    old_status = ticket.status

    ticket.status = norm_status
    ticket.updated_at = datetime.now(timezone.utc)

    if norm_status in ("RESOLVED", "CLOSED"):
        ticket.resolved_at = datetime.now(timezone.utc)
    else:
        ticket.resolved_at = None

    comment_msg = f"Status updated from {old_status} to {norm_status}."
    if note:
        comment_msg += f" Note: {note.strip()}"

    comment = TicketComment(
        ticket_id=ticket.id,
        user_id=user.id,
        comment=comment_msg,
        is_internal=False,
    )
    db.add(comment)

    # Notify requester if status changed by agent/lead
    if ticket.requester_id != user.id:
        await create_notification(
            db,
            user_id=ticket.requester_id,
            title=f"Ticket #{ticket.ticket_number} Status Update",
            message=f"Your ticket '{ticket.title}' was marked as {norm_status}.",
            ticket_id=ticket.id,
        )

    await db.flush()
    return (await get_ticket_by_id(db, ticket.id))!  # type: ignore[return-value]


async def resolve_ticket(
    db: AsyncSession,
    ticket_id: uuid.UUID,
    user: User,
    resolution_notes: str,
) -> Ticket:
    """Mark ticket resolved with resolution notes."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    now = datetime.now(timezone.utc)
    ticket.status = "RESOLVED"
    ticket.resolved_at = now
    ticket.resolution_notes = resolution_notes.strip()
    ticket.updated_at = now

    comment = TicketComment(
        ticket_id=ticket.id,
        user_id=user.id,
        comment=f"Ticket marked as Resolved. Resolution summary: {resolution_notes.strip()}",
        is_internal=False,
    )
    db.add(comment)

    # Notify requester
    if ticket.requester_id != user.id:
        await create_notification(
            db,
            user_id=ticket.requester_id,
            title=f"Ticket #{ticket.ticket_number} Resolved",
            message=f"Your ticket '{ticket.title}' has been resolved: {resolution_notes.strip()}",
            ticket_id=ticket.id,
        )

    await db.flush()
    return (await get_ticket_by_id(db, ticket.id))!  # type: ignore[return-value]


async def add_comment(
    db: AsyncSession,
    ticket_id: uuid.UUID,
    user: User,
    comment_text: str,
    is_internal: bool = False,
) -> TicketComment:
    """Add a comment or internal note to a ticket."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    comment = TicketComment(
        ticket_id=ticket.id,
        user_id=user.id,
        comment=comment_text.strip(),
        is_internal=is_internal,
    )
    db.add(comment)
    ticket.updated_at = datetime.now(timezone.utc)
    await db.flush()

    # Send notification if not internal
    if not is_internal:
        notify_user_id = ticket.requester_id if user.id != ticket.requester_id else ticket.assigned_to
        if notify_user_id:
            await create_notification(
                db,
                user_id=notify_user_id,
                title=f"New Comment on Ticket #{ticket.ticket_number}",
                message=f"{user.name} commented: '{comment_text.strip()[:100]}'",
                ticket_id=ticket.id,
            )

    return comment


async def add_attachment(
    db: AsyncSession,
    ticket_id: uuid.UUID,
    user: User,
    file_name: str,
    file_url: str | None = None,
    file_size: str | None = None,
) -> TicketAttachment:
    """Add an attachment record to a ticket."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    attachment = TicketAttachment(
        ticket_id=ticket.id,
        user_id=user.id,
        file_name=file_name.strip(),
        file_url=file_url,
        file_size=file_size,
    )
    db.add(attachment)

    audit_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=user.id,
        comment=f"Attached file: {file_name.strip()}",
        is_internal=False,
    )
    db.add(audit_comment)
    ticket.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return attachment
