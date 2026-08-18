from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str
    unit: str = "grams"
    category: str = "other"


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    category: str | None = None


class IngredientOut(IngredientBase):
    id: int

    model_config = {"from_attributes": True}
