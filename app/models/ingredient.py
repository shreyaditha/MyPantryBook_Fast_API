from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False, default="grams")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="other")

    # Relationships
    pantry_items = relationship("PantryItem", back_populates="ingredient")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")
