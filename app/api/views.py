"""View routes for Jinja2 template rendering."""
import json
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.models.recipe import Recipe, RecipeIngredient
from app.models.pantry import PantryItem
from app.models.ingredient import Ingredient
from app.models.notification import Notification

import jinja2

router = APIRouter(tags=["views"])

# Python 3.14 + Jinja2 3.1.6 has a bug where dict globals are passed as
# unhashable LRU cache keys. Fix: use a plain dict cache (cache_size=0).
_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("app/templates"),
    cache_size=0,
    auto_reload=True,
)
templates = Jinja2Templates(env=_jinja_env)


DEMO_USER_ID = settings.DEMO_USER_ID


async def _get_unread_count(db: AsyncSession) -> int:
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == DEMO_USER_ID,
            Notification.is_read == False,  # noqa: E712
        )
    )
    return len(result.scalars().all())


@router.get("/")
async def landing(request: Request, db: AsyncSession = Depends(get_db)):
    unread = await _get_unread_count(db)
    return templates.TemplateResponse(request, "index.html", {"unread_count": unread})


@router.get("/pantry")
async def pantry_page(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(PantryItem)
        .options(selectinload(PantryItem.ingredient))
        .where(PantryItem.user_id == DEMO_USER_ID)
        .order_by(PantryItem.expiry_date.asc().nulls_last())
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    ingr_result = await db.execute(select(Ingredient).order_by(Ingredient.name))
    ingredients = ingr_result.scalars().all()
    unread = await _get_unread_count(db)
    return templates.TemplateResponse(
        request,
        "pantry.html",
        {"items": items, "ingredients": ingredients, "unread_count": unread, "now_date": date.today()},
    )


@router.get("/recipes")
async def recipes_page(
    request: Request,
    cuisine: Optional[str] = Query(None),
    max_prep_time: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    available_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
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

    pid_result = await db.execute(
        select(PantryItem.ingredient_id).where(PantryItem.user_id == DEMO_USER_ID)
    )
    pantry_ids = set(pid_result.scalars().all())

    if available_only:
        recipes = [
            r for r in recipes
            if len(r.recipe_ingredients) > 0
            and all(ri.ingredient_id in pantry_ids for ri in r.recipe_ingredients)
        ]

    recipe_data = []
    for r in recipes:
        total = len(r.recipe_ingredients)
        matched = sum(1 for ri in r.recipe_ingredients if ri.ingredient_id in pantry_ids)
        match_pct = round((matched / total) * 100) if total > 0 else 0
        recipe_data.append({"recipe": r, "match_pct": match_pct})

    unread = await _get_unread_count(db)
    return templates.TemplateResponse(
        request,
        "recipes.html",
        {
            "recipe_data": recipe_data,
            "cuisine": cuisine,
            "max_prep_time": max_prep_time,
            "search": search,
            "available_only": available_only,
            "unread_count": unread,
        },
    )


@router.get("/recipes/new")
async def new_recipe_page(request: Request, db: AsyncSession = Depends(get_db)):
    ingr_result = await db.execute(select(Ingredient).order_by(Ingredient.name))
    ingredients = ingr_result.scalars().all()
    unread = await _get_unread_count(db)
    return templates.TemplateResponse(
        request,
        "recipe_form.html",
        {"recipe": None, "ingredients": ingredients, "unread_count": unread},
    )


@router.get("/recipes/{recipe_id}/edit")
async def edit_recipe_page(recipe_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
        .where(Recipe.id == recipe_id)
    )
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()
    if not recipe:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)

    ingr_result = await db.execute(select(Ingredient).order_by(Ingredient.name))
    ingredients = ingr_result.scalars().all()
    unread = await _get_unread_count(db)
    return templates.TemplateResponse(
        request,
        "recipe_form.html",
        {"recipe": recipe, "ingredients": ingredients, "unread_count": unread},
    )


@router.get("/recipes/{recipe_id}")
async def recipe_detail_page(recipe_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
        .where(Recipe.id == recipe_id)
    )
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()
    if not recipe:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)

    pid_result = await db.execute(
        select(PantryItem.ingredient_id).where(PantryItem.user_id == DEMO_USER_ID)
    )
    pantry_ids = set(pid_result.scalars().all())

    steps = []
    if recipe.instructions:
        try:
            steps = json.loads(recipe.instructions)
        except Exception:
            steps = [recipe.instructions]

    unread = await _get_unread_count(db)
    return templates.TemplateResponse(
        request,
        "recipe_detail.html",
        {
            "recipe": recipe,
            "steps": steps,
            "pantry_ids": pantry_ids,
            "unread_count": unread,
        },
    )


@router.get("/suggestions")
async def suggestions_page(request: Request, db: AsyncSession = Depends(get_db)):
    pid_result = await db.execute(
        select(PantryItem.ingredient_id).where(PantryItem.user_id == DEMO_USER_ID)
    )
    pantry_ids = set(pid_result.scalars().all())

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
        match_pct = round((matched / total) * 100)
        suggestions.append({"recipe": recipe, "match_pct": match_pct, "matched": matched, "total": total})

    suggestions.sort(key=lambda x: x["match_pct"], reverse=True)
    unread = await _get_unread_count(db)
    return templates.TemplateResponse(
        request,
        "suggestions.html",
        {"suggestions": suggestions, "unread_count": unread},
    )


@router.get("/notifications")
async def notifications_page(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == DEMO_USER_ID)
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()
    unread = await _get_unread_count(db)
    return templates.TemplateResponse(
        request,
        "notifications.html",
        {"notifications": notifications, "unread_count": unread},
    )
