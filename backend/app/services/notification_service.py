"""Notification service — create and manage in-app notifications in PostgreSQL."""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.notification import Notification
from app.db.models.user import User


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    message: str,
    ticket_id: uuid.UUID | None = None,
) -> Notification:
    """Create a single notification record for a user."""
    notif = Notification(
        user_id=user_id,
        ticket_id=ticket_id,
        title=title,
        message=message,
        is_read=False,
    )
    db.add(notif)
    await db.flush()
    return notif


async def notify_team_leads_of_department(
    db: AsyncSession,
    department_id: uuid.UUID,
    title: str,
    message: str,
    ticket_id: uuid.UUID | None = None,
) -> list[Notification]:
    """Find all active team leads in a department and create notifications for each."""
    query = (
        select(User)
        .where(
            User.department_id == department_id,
            User.role == "TEAM_LEAD",
            User.is_active == True,  # noqa: E712
        )
    )
    res = await db.execute(query)
    team_leads = res.scalars().all()

    notifications = []
    for tl in team_leads:
        notif = Notification(
            user_id=tl.id,
            ticket_id=ticket_id,
            title=title,
            message=message,
            is_read=False,
        )
        db.add(notif)
        notifications.append(notif)

    if notifications:
        await db.flush()

    return notifications


async def get_user_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 50,
) -> tuple[list[Notification], int]:
    """Retrieve notifications for a user and the count of unread items."""
    query = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(query)
    items = list(res.scalars().all())

    unread_query = (
        select(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
    )
    unread_res = await db.execute(unread_query)
    unread_count = len(unread_res.scalars().all())

    return items, unread_count


async def mark_notification_read(
    db: AsyncSession,
    notification_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Mark a specific notification as read."""
    query = (
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )
    res = await db.execute(query)
    await db.flush()
    return (res.rowcount or 0) > 0


async def mark_all_notifications_read(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """Mark all notifications for a user as read."""
    query = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
    )
    res = await db.execute(query)
    await db.flush()
    return res.rowcount or 0
