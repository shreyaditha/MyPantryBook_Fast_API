"""Pantry CRUD endpoints."""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.models.pantry import PantryItem
from app.models.notification import Notification
from app.schemas.pantry import PantryItemCreate, PantryItemUpdate, PantryItemOut

router = APIRouter(prefix="/pantry", tags=["pantry"])

DEMO_USER_ID = settings.DEMO_USER_ID


async def _check_expiry_notifications(user_id: int):
    """Background task: create notifications for items expiring within 3 days."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        threshold = date.today() + timedelta(days=3)
        stmt = (
            select(PantryItem)
            .options(selectinload(PantryItem.ingredient))
            .where(
                PantryItem.user_id == user_id,
                PantryItem.expiry_date != None,  # noqa: E711
                PantryItem.expiry_date <= threshold,
            )
        )
        result = await db.execute(stmt)
        expiring = result.scalars().all()
        for item in expiring:
            days_left = (item.expiry_date - date.today()).days
            msg = (
                f"⚠️ {item.ingredient.name} expires "
                + ("today!" if days_left == 0 else f"in {days_left} day(s)!")
            )
            # Avoid duplicate notifications
            existing = await db.execute(
                select(Notification).where(
                    Notification.user_id == user_id,
                    Notification.pantry_item_id == item.id,
                    Notification.is_read == False,  # noqa: E712
                )
            )
            if not existing.scalar_one_or_none():
                db.add(Notification(user_id=user_id, pantry_item_id=item.id, message=msg))
        await db.commit()


@router.post("", response_model=PantryItemOut, status_code=201)
async def add_pantry_item(
    data: PantryItemCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Add an ingredient to the pantry."""
    item = PantryItem(user_id=DEMO_USER_ID, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item, ["ingredient"])
    background_tasks.add_task(_check_expiry_notifications, DEMO_USER_ID)
    return item


@router.get("", response_model=list[PantryItemOut])
async def list_pantry(db: AsyncSession = Depends(get_db)):
    """List all pantry items for the demo user, sorted by expiry date."""
    stmt = (
        select(PantryItem)
        .options(selectinload(PantryItem.ingredient))
        .where(PantryItem.user_id == DEMO_USER_ID)
        .order_by(PantryItem.expiry_date.asc().nulls_last())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/{item_id}", response_model=PantryItemOut)
async def update_pantry_item(
    item_id: int,
    data: PantryItemUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Update quantity or expiry date of a pantry item."""
    result = await db.execute(
        select(PantryItem)
        .options(selectinload(PantryItem.ingredient))
        .where(PantryItem.id == item_id, PantryItem.user_id == DEMO_USER_ID)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item, ["ingredient"])
    background_tasks.add_task(_check_expiry_notifications, DEMO_USER_ID)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_pantry_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Remove an item from the pantry."""
    result = await db.execute(
        select(PantryItem).where(PantryItem.id == item_id, PantryItem.user_id == DEMO_USER_ID)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    await db.delete(item)
