from typing import List, Dict, Optional
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from src.database.models import Ingredient
from src.database.models.burger import Burger
from src.database.models.burger_ingredient_items import BurgerIngredientItem
from src.database.schemes.burger import BurgerCreate, BurgerUpdate

async def create_burger(db: AsyncSession, burger_in: BurgerCreate) -> Burger:
    db_burger = Burger(name=burger_in.name,
                       description=burger_in.description,
                       price=burger_in.price)
    db.add(db_burger)
    await db.flush()

    if burger_in.ingredient_ids in ([], None):
        raise ValueError("Burger must have at least one ingredient.")

    ingredient_items_to_add: List[BurgerIngredientItem] = []
    ingredient_quantities: Dict[int, int] = {}

    for ingredient_id in burger_in.ingredient_ids:
        ingredient_quantities[ingredient_id] = ingredient_quantities.get(ingredient_id, 0) + 1

    for ingredient_id, quantity in ingredient_quantities.items():
        db_ingredient = await db.get(Ingredient, ingredient_id)
        if not db_ingredient:
            raise ValueError(f"Ingredient with ID {ingredient_id} wasn't found in DB.")

        burger_ingredient_item = BurgerIngredientItem(burger_id=db_burger.id,
                                                      ingredient_id=ingredient_id,
                                                      quantity=quantity)
        ingredient_items_to_add.append(burger_ingredient_item)

    db.add_all(ingredient_items_to_add)

    try:
        await db.commit()

        query = (select(Burger)
                .where(Burger.id == db_burger.id)
                .options(selectinload(Burger.ingredient_items).selectinload(BurgerIngredientItem.ingredient)))
        result = await db.execute(query)
        refreshed_burger = result.scalar_one()

        if refreshed_burger:
            logging.info(f"Burger {db_burger.id} created successfully.")
            return db_burger

        logging.error(f"Failed to refresh burger {db_burger.id} after creation.")
        raise

    except ValueError as e:
        await db.rollback()
        logging.warning(str(e))
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to create burger {burger_in.name}: {str(e)}.")
        raise

async def update_burger(db: AsyncSession, burger_id: int, burger_in: BurgerUpdate) -> Optional[Burger]:
    db_burger_to_update = await get_burger_by_id(db, burger_id)

    if not db_burger_to_update:
        logging.warning(f"Burger with id {burger_id} does not exist.")
        return None

    update_data = burger_in.model_dump(exclude_unset=True)
    burger_fields_updated = False
    for key, value in update_data.items():
        if key != "ingredient_ids":
            if getattr(db_burger_to_update, key) != value:
                setattr(db_burger_to_update, key, value)
                burger_fields_updated = True

    if burger_fields_updated:
        db.add(db_burger_to_update)

    if "ingredient_ids" in update_data and update_data["ingredient_ids"] not in ([], None):
        query = delete(BurgerIngredientItem).where(BurgerIngredientItem.burger_id == burger_id)
        await db.execute(query)

        if update_data["ingredient_ids"]:
            ingredient_items_to_add: List[BurgerIngredientItem] = []
            ingredient_quantities: Dict[int, int] = {}
            for ingredient_id in update_data["ingredient_ids"]:
                ingredient_quantities[ingredient_id] = ingredient_quantities.get(ingredient_id, 0) + 1

            for ingredient_id, quantity in ingredient_quantities.items():
                db_ingredient = await db.get(Ingredient, ingredient_id)
                if not db_ingredient:
                    raise ValueError(f"Ingredient with ID {ingredient_id} wasn't found in DB.")

                burger_ingredient_item = BurgerIngredientItem(burger_id=db_burger_to_update.id,
                                                              ingredient_id=ingredient_id,
                                                              quantity=quantity)
                ingredient_items_to_add.append(burger_ingredient_item)

            if ingredient_items_to_add:
                db.add_all(ingredient_items_to_add)

    try:
        await db.commit()
        refreshed_burger = await get_burger_by_id(db, burger_id)

        if refreshed_burger:
            logging.info(f"Burger {db_burger_to_update.id} updated successfully.")
            return db_burger_to_update

        logging.error(f"Failed to re-fetch burger {db_burger_to_update.id} after update.")
        return db_burger_to_update

    except ValueError as e:
        await db.rollback()
        logging.warning(str(e))
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to update burger {burger_id}: {str(e)}.")
        raise

async def get_burger_by_id(db: AsyncSession, burger_id: int) -> Optional[Burger]:
    query = (select(Burger)
             .where(Burger.id == burger_id)
             .options(selectinload(Burger.ingredient_items).selectinload(BurgerIngredientItem.ingredient)))
    result = await db.execute(query)
    burger = result.scalar_one_or_none()

    if not burger:
        logging.debug(f"Burger {burger_id} not found in DB.")
        return None

    logging.info(f"Burger {burger_id} ('{burger.name}') found successfully in DB by ID.")
    return burger

async def get_all_burgers(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Burger]:
    query = (select(Burger)
             .offset(offset)
             .limit(limit)
             .order_by(Burger.id)
             .options(selectinload(Burger.ingredient_items).selectinload(BurgerIngredientItem.ingredient)))
    result = await db.execute(query)
    burgers = result.scalars().all()
    logging.debug(f"Retrieved {len(burgers)} burgers, offset={offset}, limit={limit}.")
    return burgers

async def delete_burger(db: AsyncSession, burger_id: int) -> Optional[Burger]:
    existing_burger = await get_burger_by_id(db, burger_id)
    if not existing_burger:
        logging.warning(f"Burger with id {burger_id} not found for deletion.")
        return None
    try:
        await db.delete(existing_burger)
        await db.commit()
        logging.info(f"Burger {burger_id} deleted successfully.")
        return existing_burger
    except IntegrityError as e:
        logging.warning(
            f"IntegrityError deleting burger {burger_id} via BurgerService: {e}. This burger is likely in use.")
        raise ValueError(f"Cannot delete burger: It is currently part of one or more existing orders.")
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to delete burger {burger_id}: {str(e)}.")
        raise