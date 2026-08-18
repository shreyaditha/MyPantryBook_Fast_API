"""Notifications endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.models.notification import Notification
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])

DEMO_USER_ID = settings.DEMO_USER_ID


@router.get("", response_model=list[NotificationOut])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    """Get all notifications for the demo user."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == DEMO_USER_ID)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(notification_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == DEMO_USER_ID,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.flush()
    await db.refresh(notif)
    return notif


@router.delete("/read-all", status_code=204)
async def clear_read_notifications(db: AsyncSession = Depends(get_db)):
    """Delete all read notifications."""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == DEMO_USER_ID,
            Notification.is_read == True,  # noqa: E712
        )
    )
    for n in result.scalars().all():
        await db.delete(n)
