from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from ..database import Base

if TYPE_CHECKING:
    from .burger import Burger
    from .ingredient import Ingredient

class BurgerIngredientItem(Base):
    __tablename__ = "burger_ingredient_items"
    burger_id: Mapped[int] = mapped_column(
        ForeignKey("burgers.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    burger: Mapped["Burger"] = relationship(back_populates="ingredient_items")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="burger_items")