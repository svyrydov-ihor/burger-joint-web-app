from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, Field

from ..models.order import OrderStatus

if TYPE_CHECKING:
    from .burger import BurgerResponse
    from .customer import CustomerResponse

class OrderBurgerItemResponse(BaseModel):
    burger: Optional[BurgerResponse] = None
    quantity: int

    class Config:
        from_attributes = True

class OrderBurgerItemCreate(BaseModel):
    burger_id: int
    quantity: int = Field(default=1, gt=0)

class OrderBase(BaseModel):
    customer_id: int

class OrderCreate(OrderBase):
    items: List[OrderBurgerItemCreate]

class OrderResponse(OrderBase):
    id: int
    customer: CustomerResponse
    created_at: datetime
    status: OrderStatus
    burger_items: List[OrderBurgerItemResponse]

    class Config:
        from_attributes = True

class OrderUpdate(OrderBase):
    customer_id: Optional[int] = None
    items: Optional[List[OrderBurgerItemCreate]] = None
    status: Optional[OrderStatus] = None