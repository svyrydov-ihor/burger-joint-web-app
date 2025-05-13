from typing import List, TYPE_CHECKING
import enum
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .order_burger_item import OrderBurgerItem
    from .customer import Customer

class OrderStatus(enum.Enum):
    Pending = "Pending"
    Processing = "Processing"
    Completed = "Completed"
    Cancelled = "Cancelled"

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[OrderStatus] = mapped_column(String(64), nullable=False, default=OrderStatus.Pending.value)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    burger_items: Mapped[List["OrderBurgerItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin")

    @property
    def burgers(self) -> List["Burger | None"]:
        return [item.burger for item in self.burger_items if item.burger is not None]

    @property
    def burgers_with_quantity(self) -> dict:
        return {item.burger: item.quantity for item in self.burger_items if item.burger is not None}

    class Config:
        from_attributes = True
        use_enum_values = True