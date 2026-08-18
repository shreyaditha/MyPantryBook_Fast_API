"""Ingredient CRUD endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientOut

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("", response_model=IngredientOut, status_code=201)
async def create_ingredient(
    data: IngredientCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new ingredient."""
    existing = await db.execute(select(Ingredient).where(Ingredient.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ingredient with this name already exists")
    ingredient = Ingredient(**data.model_dump())
    db.add(ingredient)
    await db.flush()
    await db.refresh(ingredient)
    return ingredient


@router.get("", response_model=list[IngredientOut])
async def list_ingredients(
    search: Optional[str] = Query(None, description="Search by name"),
    db: AsyncSession = Depends(get_db),
):
    """List all ingredients, optionally filtered by name."""
    stmt = select(Ingredient)
    if search:
        stmt = stmt.where(Ingredient.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(Ingredient.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{ingredient_id}", response_model=IngredientOut)
async def get_ingredient(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single ingredient by ID."""
    result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
    ingredient = result.scalar_one_or_none()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.put("/{ingredient_id}", response_model=IngredientOut)
async def update_ingredient(
    ingredient_id: int,
    data: IngredientUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an ingredient."""
    result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
    ingredient = result.scalar_one_or_none()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ingredient, field, value)
    await db.flush()
    await db.refresh(ingredient)
    return ingredient


@router.delete("/{ingredient_id}", status_code=204)
async def delete_ingredient(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an ingredient."""
    result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
    ingredient = result.scalar_one_or_none()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    await db.delete(ingredient)
