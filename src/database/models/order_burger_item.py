from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship, mapped_column

from ..database import Base

if TYPE_CHECKING:
    from .order import Order

class OrderBurgerItem(Base):
    __tablename__ = "order_burger_items"
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True)
    burger_id: Mapped[int] = mapped_column(
        ForeignKey("burgers.id", ondelete="SET NULL"), primary_key=True, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    order: Mapped["Order"] = relationship(back_populates="burger_items")
    burger: Mapped["Burger | None"] = relationship(back_populates="order_items")