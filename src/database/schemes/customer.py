from typing import Optional
from pydantic import BaseModel

class CustomerBase(BaseModel):
    name: str
    phone: str

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int

    class Config:
        from_attributes = True

class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    phone: Optional[str] = None