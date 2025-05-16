from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database.crud import ingredient as ingredient_crud
from src.database.models.ingredient import Ingredient

class IngredientService:
    @staticmethod
    async def get_ingredient_by_id(db: AsyncSession, ingredient_id: int) -> Optional[Ingredient]:
        try:
            db_ingredient = await ingredient_crud.get_ingredient_by_id(db, ingredient_id)
            if db_ingredient is None:
                logging.debug(f"Ingredient with id {ingredient_id} not found in DB via IngredientService.")
                return None
            logging.info(f"Ingredient {db_ingredient.id} found successfully in DB via IngredientService.")
            return db_ingredient
        except Exception as e:
            logging.error(f"Unexpected error in IngredientService during ingredient retrieval by ID: {str(e)}.")
            raise

    @staticmethod
    async def get_all_ingredients(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Ingredient]:
        try:
            db_ingredients = await ingredient_crud.get_all_ingredients(db, offset, limit)
            logging.debug(f"Retrieved {len(db_ingredients)} ingredients, offset={offset}, limit={limit} via IngredientService.")
            return db_ingredients
        except Exception as e:
            logging.error(f"Unexpected error in IngredientService during ingredient retrieval: {str(e)}.")
            raise