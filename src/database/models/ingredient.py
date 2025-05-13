from typing import List, TYPE_CHECKING
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .burger_ingredient_items import BurgerIngredientItem

class Ingredient(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)

    burger_items: Mapped[List["BurgerIngredientItem"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan", lazy="selectin")

    class Config:
        from_attributes = True