from typing import List, Dict, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from src.database.models import Burger
from src.database.models.order import Order, OrderStatus
from src.database.models.order_burger_item import OrderBurgerItem
from src.database.crud import order as crud_order
from src.database.schemes.order import OrderCreate, OrderUpdate
from src.services.customer import CustomerService


class OrderService:
    @staticmethod
    async def create_order(db: AsyncSession, order_in: OrderCreate) -> Order:
        try:
            customer = await CustomerService.get_customer_by_id(db, order_in.customer_id)
            if customer is None:
                raise ValueError(f"Customer with ID {order_in.customer_id} wasn't found in DB.")
            if order_in.items in ([], None):
                raise ValueError("Order must have at least one burger item.")
            for item in order_in.items:
                burger = await db.get(Burger, item.burger_id)
                if burger is None:
                    raise ValueError(f"Burger with ID {item.burger_id} wasn't found in DB.")

            order = await crud_order.create_order(db, order_in)
            logging.info(f"Order {order.id} created successfully via OrderService.")
            return order
        except ValueError as e:
            logging.warning(f"Failed to create order via OrderService: {str(e)}.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order creation: {str(e)}.")

    @staticmethod
    async def update_order(db: AsyncSession, order_id: int, order_in: OrderUpdate) -> Optional[Order]:
        try:
            order = await crud_order.update_order(db, order_id, order_in)
            logging.info(f"Order {order_id} updated successfully via OrderService.")
            return order
        except ValueError as e:
            logging.warning(f"Failed to update order via OrderService: {str(e)}.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order update: {str(e)}.")
            raise

    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: int) -> Order:
        try:
            order = await crud_order.get_order_by_id(db, order_id)
            if order is None:
                logging.debug(f"Order with id {order_id} not found in DB.")
                return None
            logging.info(f"Order {order_id} ('{order.id}') found successfully in DB by ID via OrderService.")
            return order
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order retrieval by ID: {str(e)}.")
            raise

    @staticmethod
    async def get_all_orders(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Order]:
        try:
            orders = await crud_order.get_all_orders(db, offset, limit)
            logging.debug(f"Retrieved {len(orders)} orders, offset={offset}, limit={limit} via OrderService.")
            return orders
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order retrieval: {str(e)}.")
            raise

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: int) -> Optional[Order]:
        try:
            order = await crud_order.delete_order(db, order_id)
            if order is None:
                logging.warning(f"Order with id {order_id} not found for deletion via OrderService.")
                return None
            logging.info(f"Order {order_id} deleted successfully via OrderService.")
            return order
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order deletion: {str(e)}.")