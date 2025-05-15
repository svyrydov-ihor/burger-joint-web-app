from typing import List, Dict, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from src.database.models import Burger
from src.database.models.order import Order, OrderStatus
from src.database.models.order_burger_item import OrderBurgerItem
from src.database.schemes.order import OrderCreate, OrderUpdate

async def create_order(db: AsyncSession, order_in: OrderCreate) -> Order:
    db_order = Order(customer_id=order_in.customer_id)
    db.add(db_order)
    await db.flush()

    if order_in.items in ([], None):
        raise ValueError("Order must have at least one burger item.")

    order_burger_items_to_add: List[OrderBurgerItem] = []
    order_burger_quantities: Dict[int, int] = {}

    for item in order_in.items:
        order_burger_quantities[item.burger_id] = order_burger_quantities.get(item.burger_id, 0) + item.quantity

    for burger_id, quantity in order_burger_quantities.items():
        db_burger = await db.get(Burger, burger_id)
        if not db_burger:
            raise ValueError(f"Burger with ID {burger_id} wasn't found in DB.")

        order_burger_item = OrderBurgerItem(order_id=db_order.id,
                                            burger_id=burger_id,
                                            quantity=quantity)
        order_burger_items_to_add.append(order_burger_item)

    db.add_all(order_burger_items_to_add)

    try:
        await db.commit()

        query = (select(Order)
                 .where(Order.id == db_order.id).
                 options(selectinload(Order.burger_items)
                         .selectinload(OrderBurgerItem.burger),
                         selectinload(Order.customer)))
        result = await db.execute(query)
        refreshed_order = result.scalar_one()

        if refreshed_order:
            logging.info(f"Order {db_order.id} created successfully.")
            return db_order

        logging.error(f"Failed to refresh order {db_order.id} after creation.")
        raise

    except ValueError as e:
        await db.rollback()
        logging.warning(str(e))
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to create order for customer {order_in.customer_id}: {str(e)}.")
        raise

async def update_order(db: AsyncSession, order_id: int, order_in: OrderUpdate) -> Optional[Order]:
    db_order_to_update = await get_order_by_id(db, order_id)

    if not db_order_to_update:
        logging.warning(f"Order with id {order_id} does not exist.")
        return None

    update_data = order_in.model_dump(exclude_unset=True)
    order_fields_updated = False
    for key, value in update_data.items():
        if key != "items" and key != "status":
            if getattr(db_order_to_update, key) != value:
                setattr(db_order_to_update, key, value)
                order_fields_updated = True

    if "status" in update_data and update_data["status"] in OrderStatus:
        db_order_to_update.status = update_data["status"]
        order_fields_updated = True

    if order_fields_updated:
        db.add(db_order_to_update)

    if "items" in update_data and update_data["items"] not in ([], None):
        query = delete(OrderBurgerItem).where(OrderBurgerItem.order_id == order_in.id)
        await db.execute(query)

        order_burger_items_to_add: List[OrderBurgerItem] = []
        order_burger_quantities: Dict[int, int] = {}

        for item in order_in.items:
            order_burger_quantities[item.burger_id] = order_burger_quantities.get(item.burger_id, 0) + item.quantity

        for burger_id, quantity in order_burger_quantities.items():
            db_burger = await db.get(Burger, burger_id)
            if not db_burger:
                raise ValueError(f"Burger with ID {burger_id} wasn't found in DB.")

            order_burger_item = OrderBurgerItem(order_id=order_id,
                                                burger_id=burger_id,
                                                quantity=quantity)
            order_burger_items_to_add.append(order_burger_item)

        if order_burger_items_to_add:
            db.add_all(order_burger_items_to_add)

    try:
        await db.commit()

        refreshed_order = get_order_by_id(db, order_id)

        if refreshed_order:
            logging.info(f"Order {order_id} updated successfully.")
            return db_order_to_update

        logging.error(f"Failed to refresh order {order_id} after update.")
        return db_order_to_update

    except ValueError as e:
        await db.rollback()
        logging.warning(str(e))
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to updated order {order_id}: {str(e)}.")
        raise

async def get_order_by_id(db: AsyncSession, order_id: int) -> Order:
    query = (select(Order)
             .where(Order.id == order_id)
             .options(selectinload(Order.burger_items)
                     .selectinload(OrderBurgerItem.burger),
                     selectinload(Order.customer)))
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        logging.debug(f"Order with id {order_id} not found in DB.")
        return None

    logging.info(f"Order {order_id} ('{order.id}') found successfully in DB by ID.")
    return order

async def get_all_orders(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Order]:
    query = (select(Order)
             .offset(offset)
             .limit(limit)
             .order_by(Order.id)
             .options(selectinload(Order.burger_items)
                     .selectinload(OrderBurgerItem.burger),
                     selectinload(Order.customer)))
    result = await db.execute(query)
    orders = result.scalars().all()
    logging.debug(f"Retrieved {len(orders)} orders, offset={offset}, limit={limit}.")
    return orders

async def delete_order(db: AsyncSession, order_id: int) -> Optional[Order]:
    existing_order = await get_order_by_id(db, order_id)
    if not existing_order:
        logging.warning(f"Order with id {order_id} not found for deletion.")
        return None
    try:
        await db.delete(existing_order)
        await db.commit()
        logging.info(f"Order {order_id} deleted successfully.")
        return existing_order
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to delete order {order_id}: {str(e)}.")
        raise