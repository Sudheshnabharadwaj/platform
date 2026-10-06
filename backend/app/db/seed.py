"""Database seed script — initializes default departments, users, and realistic tickets in PostgreSQL."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.department import Department
from app.db.models.ticket import Ticket
from app.db.models.ticket_comment import TicketComment
from app.db.models.user import User
from app.db.session import AsyncSessionLocal
from app.services.auth_service import hash_password
from app.services.sla_service import calculate_due_date


DEFAULT_DEPARTMENTS = [
    {"name": "IT Support", "description": "Technical support, hardware, software, and networking."},
    {"name": "HR", "description": "Human resources, employee benefits, and onboarding."},
    {"name": "Finance", "description": "Financial accounting, payroll, expenses, and invoices."},
    {"name": "Operations", "description": "Business workflows, office facilities, and logistics."},
    {"name": "Other", "description": "General queries and miscellaneous administrative support."},
]


async def seed_departments(db: AsyncSession) -> dict[str, Department]:
    """Seed the default departments in PostgreSQL."""
    dept_map: dict[str, Department] = {}
    for d_data in DEFAULT_DEPARTMENTS:
        res = await db.execute(select(Department).where(Department.name == d_data["name"]))
        existing = res.scalar_one_or_none()
        if not existing:
            dept = Department(name=d_data["name"], description=d_data["description"])
            db.add(dept)
            await db.flush()
            dept_map[d_data["name"]] = dept
            print(f"[Seed] Created department: {dept.name}")
        else:
            dept_map[d_data["name"]] = existing
    return dept_map


async def seed_users(db: AsyncSession, depts: dict[str, Department]) -> dict[str, User]:
    """Seed default Admin, Team Lead, and Employee accounts."""
    user_definitions = [
        {
            "email": "admin@company.com",
            "name": "Hyma Admin",
            "role": "ADMIN",
            "password": "admin123",
            "department": depts["IT Support"],
            "phone": "+1 (555) 019-2834",
        },
        {
            "email": "teamlead@company.com",
            "name": "Sarah Connor",
            "role": "TEAM_LEAD",
            "password": "Password123",
            "department": depts["IT Support"],
            "phone": "+1 (555) 014-9921",
        },
        {
            "email": "adi@company.com",
            "name": "Adi TeamLead",
            "role": "TEAM_LEAD",
            "password": "Password123",
            "department": depts["HR"],
            "phone": "+1 (555) 018-3342",
        },
        {
            "email": "emily.c@company.com",
            "name": "Emily Clarke",
            "role": "EMPLOYEE",
            "password": "password",
            "department": depts["IT Support"],
            "phone": "+1 (555) 012-7744",
        },
        {
            "email": "manikanta@company.com",
            "name": "Manikanta",
            "role": "EMPLOYEE",
            "password": "password",
            "department": depts["IT Support"],
            "phone": "+1 (555) 016-5589",
        },
        {
            "email": "sudha@company.com",
            "name": "Sudha",
            "role": "EMPLOYEE",
            "password": "password",
            "department": depts["Finance"],
            "phone": "+1 (555) 017-8899",
        },
        {
            "email": "mounika@company.com",
            "name": "Mounika",
            "role": "EMPLOYEE",
            "password": "password",
            "department": depts["Operations"],
            "phone": "+1 (555) 013-4411",
        },
    ]

    user_map: dict[str, User] = {}
    for u_def in user_definitions:
        res = await db.execute(select(User).where(User.email == u_def["email"]))
        existing = res.scalar_one_or_none()
        if not existing:
            user = User(
                email=u_def["email"],
                name=u_def["name"],
                role=u_def["role"],
                password_hash=hash_password(u_def["password"]),
                department_id=u_def["department"].id,
                phone=u_def["phone"],
                is_active=True,
                is_superuser=(u_def["role"] == "ADMIN"),
            )
            db.add(user)
            await db.flush()
            user_map[u_def["email"]] = user
            print(f"[Seed] Created user: {user.name} ({user.email}) - {user.role}")
        else:
            # Update password hash if needed
            existing.password_hash = hash_password(u_def["password"])
            existing.name = u_def["name"]
            existing.role = u_def["role"]
            existing.department_id = u_def["department"].id
            existing.is_active = True
            await db.flush()
            user_map[u_def["email"]] = existing
            print(f"[Seed] Updated user: {existing.name} ({existing.email}) - {existing.role}")

    return user_map


async def seed_tickets(db: AsyncSession, users: dict[str, User], depts: dict[str, Department]) -> None:
    """Seed initial realistic tickets across departments with dynamic timestamps."""
    res = await db.execute(select(Ticket))
    existing_tickets = res.scalars().all()
    if existing_tickets:
        print(f"[Seed] {len(existing_tickets)} tickets already exist in PostgreSQL.")
        return

    now = datetime.now(timezone.utc)

    ticket_specs = [
        {
            "ticket_number": "TICK-1001",
            "title": "VPN Connection Failure on macOS Sequoia",
            "description": "User unable to establish secure gateway tunnel after system update. Network diagnostic reports timeout.",
            "requester": users["emily.c@company.com"],
            "assigned_to": users["manikanta@company.com"],
            "department": depts["IT Support"],
            "category": "Network & Connectivity",
            "sub_category": "VPN Gateway",
            "priority": "HIGH",
            "status": "IN_PROGRESS",
            "created_at": now - timedelta(hours=3),
            "due_at": now + timedelta(hours=5),
            "escalated": False,
        },
        {
            "ticket_number": "TICK-1002",
            "title": "Payroll Software Access Denied for Q3 Audit",
            "description": "Finance user lacks permission for audit export. Needs immediate role elevation.",
            "requester": users["sudha@company.com"],
            "assigned_to": users["teamlead@company.com"],
            "department": depts["Finance"],
            "category": "Access & Permissions",
            "sub_category": "Software License",
            "priority": "CRITICAL",
            "status": "OPEN",
            "created_at": now - timedelta(hours=3, minutes=30),
            "due_at": now + timedelta(minutes=30),  # SLA Risk! (Remaining <= 25% of 4h)
            "escalated": True,
            "escalation_reason": "Executive audit deadline in 2 hours.",
        },
        {
            "ticket_number": "TICK-1003",
            "title": "New Employee Laptop Setup - Onboarding",
            "description": "Hardware provisioning for incoming Senior Product Designer joining next week.",
            "requester": users["adi@company.com"],
            "assigned_to": users["emily.c@company.com"],
            "department": depts["HR"],
            "category": "Hardware Procurement",
            "sub_category": "Laptop Provisioning",
            "priority": "MEDIUM",
            "status": "OPEN",
            "created_at": now - timedelta(hours=5),
            "due_at": now + timedelta(hours=19),
            "escalated": False,
        },
        {
            "ticket_number": "TICK-1004",
            "title": "Database Connection Timeout during Heavy CSV Dumps",
            "description": "Nightly reporting queries causing connection pool exhaustion on replica cluster.",
            "requester": users["mounika@company.com"],
            "assigned_to": users["manikanta@company.com"],
            "department": depts["IT Support"],
            "category": "Infrastructure",
            "sub_category": "Database Server",
            "priority": "CRITICAL",
            "status": "OPEN",
            "created_at": now - timedelta(hours=6),
            "due_at": now - timedelta(hours=2),  # SLA Breached! (Created 6h ago, 4h SLA expired)
            "escalated": True,
            "escalation_reason": "SLA Breached - unacknowledged production incident.",
        },
        {
            "ticket_number": "TICK-1005",
            "title": "Quarterly Workday License Audit & Cost Center Rebalancing",
            "description": "Audit inactive accounts and decommission unused developer seats.",
            "requester": users["sudha@company.com"],
            "assigned_to": users["emily.c@company.com"],
            "department": depts["Finance"],
            "category": "Software License",
            "sub_category": "Audit",
            "priority": "LOW",
            "status": "RESOLVED",
            "created_at": now - timedelta(days=1),
            "due_at": now + timedelta(days=1),
            "resolved_at": now - timedelta(hours=1),
            "resolution_notes": "Decommissioned 14 inactive seats. Cost savings applied.",
            "escalated": False,
        },
    ]

    for t_spec in ticket_specs:
        ticket = Ticket(
            ticket_number=t_spec["ticket_number"],
            title=t_spec["title"],
            description=t_spec["description"],
            requester_id=t_spec["requester"].id,
            assigned_to=t_spec["assigned_to"].id if t_spec["assigned_to"] else None,
            department_id=t_spec["department"].id,
            category=t_spec["category"],
            sub_category=t_spec.get("sub_category"),
            priority=t_spec["priority"],
            status=t_spec["status"],
            due_at=t_spec["due_at"],
            created_at=t_spec["created_at"],
            updated_at=t_spec["created_at"],
            resolved_at=t_spec.get("resolved_at"),
            resolution_notes=t_spec.get("resolution_notes"),
            escalated=t_spec.get("escalated", False),
            escalation_reason=t_spec.get("escalation_reason"),
        )
        db.add(ticket)
        await db.flush()

        comment = TicketComment(
            ticket_id=ticket.id,
            user_id=t_spec["requester"].id,
            comment="Ticket created and submitted for triage.",
            is_internal=False,
            created_at=t_spec["created_at"],
        )
        db.add(comment)

        if t_spec.get("resolution_notes"):
            res_comment = TicketComment(
                ticket_id=ticket.id,
                user_id=t_spec["assigned_to"].id,
                comment=f"Ticket marked as Resolved. {t_spec['resolution_notes']}",
                is_internal=False,
                created_at=t_spec.get("resolved_at") or now,
            )
            db.add(res_comment)

        print(f"[Seed] Created ticket: {ticket.ticket_number} - {ticket.title}")

    await db.flush()


async def run_seed() -> None:
    """Execute complete database seed."""
    async with AsyncSessionLocal() as session:
        try:
            print("--- Starting Database Seeding ---")
            depts = await seed_departments(session)
            users = await seed_users(session, depts)
            await seed_tickets(session, users, depts)
            await session.commit()
            print("--- Database Seeding Complete ---")
        except Exception as e:
            await session.rollback()
            print("Error during seed:", e)
            raise


if __name__ == "__main__":
    asyncio.run(run_seed())
