from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    cuisine: Mapped[str] = mapped_column(String(50), nullable=False, default="South Indian")
    prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    servings: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")
    instructions: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of steps
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    creator = relationship("User", back_populates="recipes")
    recipe_ingredients = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id: Mapped[int] = mapped_column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity_needed: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    unit: Mapped[str] = mapped_column(String(30), nullable=False, default="grams")

    # Relationships
    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")
