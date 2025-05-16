from pydantic import BaseModel

class IngredientResponse(BaseModel):
    id: int
    name: str
    manufacturer: str

    class Config:
        from_attributes = True