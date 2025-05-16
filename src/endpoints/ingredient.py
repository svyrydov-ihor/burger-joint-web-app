from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.core.dependencies import get_db_session
from src.database.schemes.ingredient import IngredientResponse
from src.services.ingredient import IngredientService

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"]
)

@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def read_ingredient(
        ingredient_id: int,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        db_ingredient = await IngredientService.get_ingredient_by_id(db, ingredient_id)
        if db_ingredient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
        return db_ingredient
    except Exception as e:
        logging.error(f"Unhandled exception in read_ingredient for ID {ingredient_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to read ingredient")

@router.get("/", response_model=List[IngredientResponse])
async def read_all_ingredients(
        offset: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        return await IngredientService.get_all_ingredients(db, offset, limit)
    except Exception as e:
        logging.error(f"Unhandled exception in read_all_ingredients: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to read ingredients")