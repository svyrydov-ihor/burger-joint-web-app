from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.core.dependencies import get_db_session
from src.database.schemes.burger import *
from src.services.burger import BurgerService

router = APIRouter(
    prefix="/burgers",
    tags=["Burgers"]
)

@router.post("/", response_model=BurgerResponse, status_code=status.HTTP_201_CREATED)
async def create_new_burger(
        burger_in: BurgerCreate,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        return await BurgerService.create_burger(db, burger_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logging.error(f"Unhandled exception in create_new_burger: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create burger")

@router.put("/{burger_id}", response_model=BurgerResponse)
async def update_existing_burger(
        burger_id: int,
        burger_in: BurgerUpdate,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        updated_burger = await BurgerService.update_burger(db, burger_id, burger_in)
        if updated_burger is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Burger not found")
        return updated_burger
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logging.error(f"Unhandled exception in update_existing_burger for ID {burger_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update burger")

@router.get("/{burger_id}", response_model=BurgerResponse)
async def read_burger(
        burger_id: int,
        db: AsyncSession = Depends(get_db_session)
        ):
    db_burger = await BurgerService.get_burger_by_id(db, burger_id)
    if db_burger is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Burger not found")
    return db_burger

@router.get("/", response_model=List[BurgerResponse])
async def read_all_burgers(
        offset: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session)
        ):
    return await BurgerService.get_all_burgers(db, offset, limit)

@router.delete("/{burger_id}", response_model=BurgerResponse)
async def delete_existing_burger(
        burger_id: int,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        deleted_burger = await BurgerService.delete_burger(db, burger_id)
        if deleted_burger is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Burger not found")
        return deleted_burger
    except Exception as e:
        logging.error(f"Unhandled exception in delete_existing_burger for ID {burger_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete burger")