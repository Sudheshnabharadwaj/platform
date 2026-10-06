"""Dashboard metrics service — calculates dynamic KPI counts directly from PostgreSQL."""

from datetime import datetime, time, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.department import Department
from app.db.models.ticket import Ticket
from app.db.models.user import User
from app.schemas.dashboard import (
    AdminDashboardResponse,
    EmployeeDashboardResponse,
    TeamLeadDashboardResponse,
)
from app.services.sla_service import evaluate_sla
from app.services.ticket_service import serialize_ticket


async def get_admin_dashboard(db: AsyncSession) -> AdminDashboardResponse:
    """Calculate live dashboard KPIs across all departments for Admin."""
    # Fetch all tickets
    query = (
        select(Ticket)
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.department),
            selectinload(Ticket.comments),
            selectinload(Ticket.attachments),
        )
        .order_by(Ticket.created_at.desc())
    )
    tickets_res = await db.execute(query)
    all_tickets = list(tickets_res.scalars().all())

    # User count
    users_count_res = await db.execute(select(func.count(User.id)).where(User.is_active == True))  # noqa: E712
    total_users = users_count_res.scalar() or 0

    # Categorize counts
    now = datetime.now(timezone.utc)
    today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)

    open_count = 0
    escalated_count = 0
    sla_risk_count = 0
    sla_breached_count = 0
    resolved_today_count = 0

    status_counts: dict[str, int] = {
        "Open": 0,
        "In Progress": 0,
        "Pending": 0,
        "Resolved": 0,
        "Closed": 0,
    }

    dept_counts_map: dict[str, int] = {}

    for t in all_tickets:
        st_norm = t.status.upper()
        if st_norm == "OPEN":
            status_counts["Open"] += 1
            open_count += 1
        elif st_norm == "IN_PROGRESS":
            status_counts["In Progress"] += 1
        elif st_norm == "PENDING":
            status_counts["Pending"] += 1
            open_count += 1
        elif st_norm == "RESOLVED":
            status_counts["Resolved"] += 1
            if t.resolved_at and t.resolved_at >= today_start:
                resolved_today_count += 1
        elif st_norm == "CLOSED":
            status_counts["Closed"] += 1

        if t.escalated or st_norm == "ESCALATED":
            escalated_count += 1

        # SLA calculation
        sla_st, _ = evaluate_sla(t.priority, t.created_at, t.due_at, t.status)
        if sla_st == "SLA Risk":
            sla_risk_count += 1
        elif sla_st == "SLA Breached":
            sla_breached_count += 1

        # Department aggregation
        dept_name = t.department.name if t.department else "General"
        dept_counts_map[dept_name] = dept_counts_map.get(dept_name, 0) + 1

    department_wise = [
        {"department": dept, "count": count}
        for dept, count in dept_counts_map.items()
    ]

    # Team workload
    team_members_res = await db.execute(
        select(User).options(selectinload(User.department)).where(User.is_active == True)  # noqa: E712
    )
    all_users = team_members_res.scalars().all()

    workload = []
    for u in all_users:
        user_tickets = [t for t in all_tickets if t.assigned_to == u.id and t.status.upper() not in ("RESOLVED", "CLOSED")]
        workload.append({
            "id": str(u.id),
            "name": u.name,
            "role": u.role,
            "department": u.department.name if u.department else "General",
            "activeTickets": len(user_tickets),
        })

    recent_serialized = [serialize_ticket(t) for t in all_tickets[:10]]

    return AdminDashboardResponse(
        totalTickets=len(all_tickets),
        openTickets=open_count,
        escalatedTickets=escalated_count,
        slaRiskCount=sla_risk_count,
        slaBreachedCount=sla_breached_count,
        resolvedTodayCount=resolved_today_count,
        totalUsers=total_users,
        ticketOverview=status_counts,
        departmentWiseTickets=department_wise,
        teamWorkload=workload,
        recentTickets=recent_serialized,
    )


async def get_team_lead_dashboard(
    db: AsyncSession,
    team_lead: User,
) -> TeamLeadDashboardResponse:
    """Calculate dashboard KPIs strictly scoped to the Team Lead's department."""
    dept_id = team_lead.department_id

    query = (
        select(Ticket)
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.department),
            selectinload(Ticket.comments),
            selectinload(Ticket.attachments),
        )
        .order_by(Ticket.created_at.desc())
    )

    if dept_id:
        query = query.where(Ticket.department_id == dept_id)

    tickets_res = await db.execute(query)
    dept_tickets = list(tickets_res.scalars().all())

    # Team members in this department
    users_query = (
        select(User)
        .options(selectinload(User.department))
        .where(User.is_active == True)  # noqa: E712
    )
    if dept_id:
        users_query = users_query.where(User.department_id == dept_id)

    users_res = await db.execute(users_query)
    dept_members = list(users_res.scalars().all())

    open_c = 0
    in_progress_c = 0
    pending_c = 0
    resolved_c = 0
    closed_c = 0
    escalated_c = 0
    sla_risk_c = 0
    sla_breached_c = 0

    for t in dept_tickets:
        st_norm = t.status.upper()
        if st_norm == "OPEN":
            open_c += 1
        elif st_norm == "IN_PROGRESS":
            in_progress_c += 1
        elif st_norm == "PENDING":
            pending_c += 1
        elif st_norm == "RESOLVED":
            resolved_c += 1
        elif st_norm == "CLOSED":
            closed_c += 1

        if t.escalated or st_norm == "ESCALATED":
            escalated_c += 1

        sla_st, _ = evaluate_sla(t.priority, t.created_at, t.due_at, t.status)
        if sla_st == "SLA Risk":
            sla_risk_c += 1
        elif sla_st == "SLA Breached":
            sla_breached_c += 1

    workload = []
    for m in dept_members:
        member_active = [t for t in dept_tickets if t.assigned_to == m.id and t.status.upper() not in ("RESOLVED", "CLOSED")]
        workload.append({
            "id": str(m.id),
            "name": m.name,
            "role": m.role,
            "email": m.email,
            "activeTickets": len(member_active),
        })

    dept_name = team_lead.department.name if team_lead.department else "General Department"
    recent_serialized = [serialize_ticket(t) for t in dept_tickets[:10]]

    return TeamLeadDashboardResponse(
        totalDepartmentTickets=len(dept_tickets),
        openTickets=open_c,
        inProgressTickets=in_progress_c,
        pendingTickets=pending_c,
        resolvedTickets=resolved_c,
        closedTickets=closed_c,
        escalatedTickets=escalated_c,
        slaRiskCount=sla_risk_c,
        slaBreachedCount=sla_breached_c,
        departmentName=dept_name,
        teamMembersCount=len(dept_members),
        teamWorkload=workload,
        recentTickets=recent_serialized,
    )


async def get_employee_dashboard(
    db: AsyncSession,
    employee: User,
) -> EmployeeDashboardResponse:
    """Calculate dashboard metrics for a specific employee."""
    # Created tickets
    created_res = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.department),
            selectinload(Ticket.comments),
            selectinload(Ticket.attachments),
        )
        .where(Ticket.requester_id == employee.id)
        .order_by(Ticket.created_at.desc())
    )
    my_created = list(created_res.scalars().all())

    # Assigned tickets
    assigned_res = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.requester),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.department),
            selectinload(Ticket.comments),
            selectinload(Ticket.attachments),
        )
        .where(Ticket.assigned_to == employee.id)
        .order_by(Ticket.created_at.desc())
    )
    my_assigned = list(assigned_res.scalars().all())

    open_assigned = 0
    in_progress_assigned = 0
    resolved_assigned = 0
    sla_risk_c = 0
    sla_breached_c = 0

    for t in my_assigned:
        st_norm = t.status.upper()
        if st_norm == "OPEN":
            open_assigned += 1
        elif st_norm == "IN_PROGRESS":
            in_progress_assigned += 1
        elif st_norm == "RESOLVED":
            resolved_assigned += 1

        sla_st, _ = evaluate_sla(t.priority, t.created_at, t.due_at, t.status)
        if sla_st == "SLA Risk":
            sla_risk_c += 1
        elif sla_st == "SLA Breached":
            sla_breached_c += 1

    return EmployeeDashboardResponse(
        myCreatedTicketsCount=len(my_created),
        myAssignedTicketsCount=len(my_assigned),
        openAssignedCount=open_assigned,
        inProgressAssignedCount=in_progress_assigned,
        resolvedAssignedCount=resolved_assigned,
        slaRiskCount=sla_risk_c,
        slaBreachedCount=sla_breached_c,
        recentAssignedTickets=[serialize_ticket(t) for t in my_assigned[:5]],
        recentCreatedTickets=[serialize_ticket(t) for t in my_created[:5]],
    )
