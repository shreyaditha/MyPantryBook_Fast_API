"""Recipe CRUD + suggestion endpoints."""
import json
import os
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.models.recipe import Recipe, RecipeIngredient
from app.models.pantry import PantryItem
from app.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut, RecipeSuggestion, RecipeIngredientOut

router = APIRouter(prefix="/recipes", tags=["recipes"])

DEMO_USER_ID = settings.DEMO_USER_ID
UPLOAD_DIR = "app/static/uploads"
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    pass


def _recipe_to_out(recipe: Recipe, pantry_ids: Optional[set] = None) -> dict:
    """Convert a Recipe ORM object to a dict suitable for RecipeOut."""
    ri_list = []
    for ri in recipe.recipe_ingredients:
        in_pantry = (ri.ingredient_id in pantry_ids) if pantry_ids is not None else None
        ri_list.append(
            RecipeIngredientOut(
                id=ri.id,
                ingredient_id=ri.ingredient_id,
                quantity_needed=ri.quantity_needed,
                unit=ri.unit,
                ingredient=ri.ingredient,
                in_pantry=in_pantry,
            )
        )
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "cuisine": recipe.cuisine,
        "prep_time_minutes": recipe.prep_time_minutes,
        "servings": recipe.servings,
        "difficulty": recipe.difficulty,
        "instructions": recipe.instructions,
        "image_url": recipe.image_url,
        "created_by": recipe.created_by,
        "created_at": recipe.created_at,
        "recipe_ingredients": ri_list,
    }


async def _get_pantry_ingredient_ids(user_id: int, db: AsyncSession) -> set:
    result = await db.execute(
        select(PantryItem.ingredient_id).where(PantryItem.user_id == user_id)
    )
    return set(result.scalars().all())


@router.get("/suggestions", response_model=list[RecipeSuggestion])
async def get_suggestions(db: AsyncSession = Depends(get_db)):
    """
    Rank all recipes by percentage of required ingredients currently in the pantry.
    Returns recipes sorted by match percentage descending.
    """
    pantry_ids = await _get_pantry_ingredient_ids(DEMO_USER_ID, db)
    stmt = select(Recipe).options(
        selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
    )
    result = await db.execute(stmt)
    recipes = result.scalars().all()

    suggestions = []
    for recipe in recipes:
        total = len(recipe.recipe_ingredients)
        if total == 0:
            continue
        matched = sum(1 for ri in recipe.recipe_ingredients if ri.ingredient_id in pantry_ids)
        match_pct = round((matched / total) * 100, 1)
        base = _recipe_to_out(recipe, pantry_ids)
        suggestions.append(
            RecipeSuggestion(**base, match_percent=match_pct, matched_count=matched, total_count=total)
        )

    suggestions.sort(key=lambda r: r.match_percent, reverse=True)
    return suggestions


@router.post("", response_model=RecipeOut, status_code=201)
async def create_recipe(data: RecipeCreate, db: AsyncSession = Depends(get_db)):
    """Create a new recipe with nested ingredients."""
    recipe = Recipe(
        title=data.title,
        description=data.description,
        cuisine=data.cuisine,
        prep_time_minutes=data.prep_time_minutes,
        servings=data.servings,
        difficulty=data.difficulty,
        instructions=data.instructions,
        created_by=DEMO_USER_ID,
    )
    db.add(recipe)
    await db.flush()

    for ri_data in data.ingredients:
        ri = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ri_data.ingredient_id,
            quantity_needed=ri_data.quantity_needed,
            unit=ri_data.unit,
        )
        db.add(ri)

    await db.flush()
    await db.refresh(recipe, ["recipe_ingredients"])
    # Eagerly load nested ingredient objects
    stmt = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
        .where(Recipe.id == recipe.id)
    )
    result = await db.execute(stmt)
    recipe = result.scalar_one()
    return RecipeOut(**_recipe_to_out(recipe))


@router.get("", response_model=list[RecipeOut])
async def list_recipes(
    cuisine: Optional[str] = Query(None),
    max_prep_time: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    available_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """List recipes with optional filtering by cuisine, prep time, search term, and pantry availability."""
    stmt = select(Recipe).options(
        selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
    )
    if cuisine:
        stmt = stmt.where(Recipe.cuisine.ilike(f"%{cuisine}%"))
    if max_prep_time:
        stmt = stmt.where(Recipe.prep_time_minutes <= max_prep_time)
    if search:
        stmt = stmt.where(Recipe.title.ilike(f"%{search}%"))

    result = await db.execute(stmt)
    recipes = result.scalars().all()

    if available_only:
        pantry_ids = await _get_pantry_ingredient_ids(DEMO_USER_ID, db)
        recipes = [
            r for r in recipes
            if len(r.recipe_ingredients) > 0
            and all(ri.ingredient_id in pantry_ids for ri in r.recipe_ingredients)
        ]

    return [RecipeOut(**_recipe_to_out(r)) for r in recipes]


@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """Get full recipe detail with per-ingredient pantry match flags."""
    stmt = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
        .where(Recipe.id == recipe_id)
    )
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    pantry_ids = await _get_pantry_ingredient_ids(DEMO_USER_ID, db)
    return RecipeOut(**_recipe_to_out(recipe, pantry_ids))


@router.put("/{recipe_id}", response_model=RecipeOut)
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a recipe. If ingredients list provided, replaces all existing ingredient rows."""
    stmt = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_ingredients))
        .where(Recipe.id == recipe_id)
    )
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = data.model_dump(exclude_unset=True)
    ingredients_data = update_data.pop("ingredients", None)

    for field, value in update_data.items():
        setattr(recipe, field, value)

    if ingredients_data is not None:
        for ri in recipe.recipe_ingredients:
            await db.delete(ri)
        await db.flush()
        for ri_data in ingredients_data:
            db.add(RecipeIngredient(recipe_id=recipe.id, **ri_data))

    await db.flush()
    stmt = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
        .where(Recipe.id == recipe_id)
    )
    result = await db.execute(stmt)
    recipe = result.scalar_one()
    return RecipeOut(**_recipe_to_out(recipe))


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a recipe. Default cookbook recipes are protected from deletion."""
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.created_by is None or recipe_id <= 26:
        raise HTTPException(
            status_code=403,
            detail="Default South Indian cookbook recipes are protected and cannot be deleted."
        )
    await db.delete(recipe)


@router.post("/{recipe_id}/image", response_model=RecipeOut)
async def upload_recipe_image(
    recipe_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image for a recipe. Stores to /static/uploads."""
    stmt = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
        .where(Recipe.id == recipe_id)
    )
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"recipe_{recipe_id}{ext}"
    target_dir = UPLOAD_DIR
    try:
        os.makedirs(target_dir, exist_ok=True)
    except Exception:
        target_dir = "/tmp/uploads"
        os.makedirs(target_dir, exist_ok=True)

    filepath = os.path.join(target_dir, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    recipe.image_url = f"/static/uploads/{filename}"
    await db.flush()
    return RecipeOut(**_recipe_to_out(recipe))
