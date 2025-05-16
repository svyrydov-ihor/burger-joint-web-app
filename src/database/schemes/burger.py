from typing import List, Optional, Dict
from pydantic import BaseModel

class BurgerBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class BurgerCreate(BurgerBase):
    ingredient_ids: List[int]

class BurgerResponse(BurgerBase):
    id: int
    ingredients: Dict[str, int]

    class Config:
        from_attributes = True

class BurgerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    ingredient_ids: Optional[List[int]] = None