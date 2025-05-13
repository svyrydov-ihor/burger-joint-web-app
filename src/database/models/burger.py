from typing import List, TYPE_CHECKING
import enum
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .order_burger_item import OrderBurgerItem
    from .burger_ingredient_items import BurgerIngredientItem

class BurgerIngredient(enum.Enum): #will be implemented later, for now ignore
    Bun = "Bun"
    BeefPatty = "Beef patty"
    AmericanCheese = "American cheese"
    MozzarellaCheese = "Mozzarella cheese"
    TomatoSlices = "Tomato slices"
    ShreddedLettuce = "Shredded lettuce"
    SmokedBacon = "Smoked bacon"
    PickleSlices = "Pickle slices"
    Onions = "Onions"
    Mushrooms = "Mushrooms"
    Eggs = "Eggs"
    Ketchup = "Ketchup"
    Mustard = "Mustard"
    Mayonnaise = "Mayonnaise"
    PepperSauce = "Pepper sauce"

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

    class Config:
        from_attributes = True