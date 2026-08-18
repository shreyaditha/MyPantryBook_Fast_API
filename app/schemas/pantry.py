from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.ingredient import IngredientOut


class PantryItemCreate(BaseModel):
    ingredient_id: int
    quantity: float = 1.0
    expiry_date: Optional[date] = None


class PantryItemUpdate(BaseModel):
    quantity: Optional[float] = None
    expiry_date: Optional[date] = None


class PantryItemOut(BaseModel):
    id: int
    ingredient_id: int
    quantity: float
    expiry_date: Optional[date]
    added_on: datetime
    ingredient: IngredientOut

    model_config = {"from_attributes": True}
