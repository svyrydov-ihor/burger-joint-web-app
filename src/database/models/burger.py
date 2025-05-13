from typing import List, TYPE_CHECKING
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .order_burger_item import OrderBurgerItem
    from .burger_ingredient_items import BurgerIngredientItem

class Burger(Base):
    __tablename__ = "burgers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    order_items: Mapped[List["OrderBurgerItem"]] = relationship(
        back_populates="burger", lazy="selectin")
    ingredient_items: Mapped[List["BurgerIngredientItem"]] = relationship(
        back_populates="burger", lazy="selectin")

    @property
    def ingredients(self) -> List["str | None"]:
        return [item.ingredient.name for item in self.ingredient_items if item is not None]

    class Config:
        from_attributes = True