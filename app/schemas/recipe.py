from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.ingredient import IngredientOut


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity_needed: float = 1.0
    unit: str = "grams"


class RecipeIngredientOut(BaseModel):
    id: int
    ingredient_id: int
    quantity_needed: float
    unit: str
    ingredient: IngredientOut
    # Present in detail view only
    in_pantry: Optional[bool] = None

    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cuisine: str = "South Indian"
    prep_time_minutes: int = 30
    servings: int = 4
    difficulty: str = "medium"
    instructions: Optional[str] = None  # JSON string of step list
    ingredients: list[RecipeIngredientCreate] = []


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cuisine: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    instructions: Optional[str] = None
    ingredients: Optional[list[RecipeIngredientCreate]] = None


class RecipeOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cuisine: str
    prep_time_minutes: int
    servings: int
    difficulty: str
    instructions: Optional[str]
    image_url: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    recipe_ingredients: list[RecipeIngredientOut] = []

    model_config = {"from_attributes": True}


class RecipeSuggestion(RecipeOut):
    match_percent: float = 0.0
    matched_count: int = 0
    total_count: int = 0
