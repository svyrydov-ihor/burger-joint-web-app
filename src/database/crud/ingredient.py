from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database.models.ingredient import Ingredient

# only reading implemented

async def get_ingredient_by_id(db: AsyncSession, ingredient_id: int) -> Optional[Ingredient]:
    query = select(Ingredient).where(Ingredient.id == ingredient_id)
    result = await db.execute(query)
    ingredient = result.scalar_one_or_none()

    if not ingredient:
        logging.debug(f"Ingredient with id {ingredient_id} not found in DB.")
        return None

    logging.debug(f"Ingredient {ingredient.id} ('{ingredient.name}') found successfully in DB by ID.")
    return ingredient

async def get_all_ingredients(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Ingredient]:
    query = select(Ingredient).offset(offset).limit(limit).order_by(Ingredient.id)
    result = await db.execute(query)
    ingredients = result.scalars().all()
    logging.debug(f"Retrieved {len(ingredients)} ingredients, offset={offset}, limit={limit}.")
    return ingredients
