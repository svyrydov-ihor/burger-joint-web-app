from typing import List, TYPE_CHECKING
import enum
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .order_burger_item import OrderBurgerItem
    from .burger_ingredient_items import BurgerIngredientItem

class BurgerIngredient(enum.Enum):
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

class Ingredient(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[BurgerIngredient] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)

    burger_items: Mapped[List["BurgerIngredientItem"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan", lazy="selectin")

    class Config:
        from_attributes = True
        use_enum_values = True