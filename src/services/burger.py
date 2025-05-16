from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database.models.burger import Burger
from src.database.crud import burger as burger_crud
from src.database.schemes.burger import BurgerCreate, BurgerUpdate

class BurgerService:
    @staticmethod
    async def create_burger(db: AsyncSession, burger_in: BurgerCreate) -> Burger:
        try:
            if burger_in.ingredient_ids in ([], None):
                raise ValueError("Burger must have at least one ingredient.")
            if burger_in.price <= 0:
                raise ValueError("Burger price must be greater than zero.")

            db_burger = await burger_crud.create_burger(db, burger_in)
            logging.info(f"Burger {db_burger.id} created successfully via BurgerService.")
            return db_burger
        except ValueError as e:
            logging.warning(f"Failed to create burger via BurgerService: {str(e)}.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in BurgerService during burger creation: {str(e)}.")
            raise

    @staticmethod
    async def update_burger(db: AsyncSession, burger_id: int, burger_in: BurgerUpdate) -> Optional[Burger]:
        try:
            if hasattr(burger_in, "price") and burger_in.price <= 0:
                raise ValueError("Burger price must be greater than zero.")

            db_burger = await burger_crud.update_burger(db, burger_id, burger_in)
            if db_burger is None:
                logging.warning(f"Burger with id {burger_id} not found for update via BurgerService.")
                return None
            logging.info(f"Burger {db_burger.id} updated successfully via BurgerService.")
            return db_burger
        except ValueError as e:
            logging.warning(f"Failed to update burger via BurgerService: {str(e)}.")
        except Exception as e:
            logging.error(f"Unexpected error in BurgerService during burger update: {str(e)}.")
            raise

    @staticmethod
    async def get_burger_by_id(db: AsyncSession, burger_id: int) -> Optional[Burger]:
        try:
            db_burger = await burger_crud.get_burger_by_id(db, burger_id)
            if db_burger is None:
                logging.debug(f"Burger with id {burger_id} not found in DB via BurgerService.")
                return None
            logging.debug(f"Burger {db_burger.id} ('{db_burger.name}') found successfully in DB by ID via BurgerService.")
            return db_burger
        except Exception as e:
            logging.error(f"Unexpected error in BurgerService during burger retrieval by ID: {str(e)}.")
            raise

    @staticmethod
    async def get_all_burgers(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Burger]:
        try:
            db_burgers = await burger_crud.get_all_burgers(db, offset, limit)
            logging.debug(f"Retrieved {len(db_burgers)} burgers, offset={offset}, limit={limit} via BurgerService.")
            return db_burgers
        except Exception as e:
            logging.error(f"Unexpected error in BurgerService during burger retrieval: {str(e)}.")
            raise

    @staticmethod
    async def delete_burger(db: AsyncSession, burger_id: int) -> Optional[Burger]:
        try:
            db_burger = await burger_crud.delete_burger(db, burger_id)
            if db_burger is None:
                logging.warning(f"Burger with id {burger_id} not found for deletion via BurgerService.")
                return None
            logging.info(f"Burger {db_burger.id} deleted successfully via BurgerService.")
            return db_burger
        except Exception as e:
            logging.error(f"Unexpected error in BurgerService during burger deletion: {str(e)}.")
            raise