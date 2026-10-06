"""Notifications API endpoints."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse, summary="Get user notifications")
async def get_notifications(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    """Retrieve all notifications for the authenticated user and count unread."""
    items, unread_count = await notification_service.get_user_notifications(db, current_user.id)
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items],
        unread_count=unread_count,
    )


@router.put("/{notification_id}/read", summary="Mark single notification as read")
async def mark_read(
    notification_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Mark a notification as read."""
    success = await notification_service.mark_notification_read(db, notification_id, current_user.id)
    return {"status": "success" if success else "not_found"}


@router.put("/read-all", summary="Mark all notifications as read")
async def mark_all_read(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Mark all notifications for current user as read."""
    count = await notification_service.mark_all_notifications_read(db, current_user.id)
    return {"marked_count": count}
