from datetime import date, datetime
from sqlalchemy import Integer, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    ingredient_id: Mapped[int] = mapped_column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    added_on: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="pantry_items")
    ingredient = relationship("Ingredient", back_populates="pantry_items")
    notifications = relationship("Notification", back_populates="pantry_item")
