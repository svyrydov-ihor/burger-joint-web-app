from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

if TYPE_CHECKING: # Для уникнення циклічних імпортів
    from .order import Order

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    orders: Mapped[List["Order"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan")

    class Config:
        from_attributes = True