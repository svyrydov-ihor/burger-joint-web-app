from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from src.database.models.order import OrderStatus
from src.database.schemes.burger import BurgerResponse
from src.database.schemes.customer import CustomerResponse

class OrderBurgerItemResponse(BaseModel):
    burger: Optional[BurgerResponse] = None
    quantity: int
    burger_price: float
    item_subtotal: float

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
    burgers_with_quantity: Dict[str, int]
    total_price: float

    class Config:
        from_attributes = True

class OrderUpdate(OrderBase):
    customer_id: Optional[int] = None
    items: Optional[List[OrderBurgerItemCreate]] = None
    status: Optional[OrderStatus] = None