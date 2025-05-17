from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database.models import Burger
from src.database.models.order import Order
from src.database.crud import order as crud_order
from src.database.schemes.order import OrderCreate, OrderUpdate, OrderResponse
from src.database.schemes.customer import CustomerResponse
from src.services.customer import CustomerService


class OrderService:
    @staticmethod
    async def create_order(db: AsyncSession, order_in: OrderCreate) -> OrderResponse:
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

            created_order = await crud_order.create_order(db, order_in)
            order = await OrderService.get_order_by_id_with_total_price(db, created_order.id)
            logging.info(f"Order {order.id} created successfully via OrderService.")
            return order
        except ValueError as e:
            logging.warning(f"Failed to create order via OrderService: {str(e)}.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order creation: {str(e)}.")

    @staticmethod
    async def update_order(db: AsyncSession, order_id: int, order_in: OrderUpdate) -> Optional[OrderResponse]:
        try:
            await crud_order.update_order(db, order_id, order_in)
            order = await OrderService.get_order_by_id_with_total_price(db, order_id)
            logging.info(f"Order {order_id} updated successfully via OrderService.")
            return order
        except ValueError as e:
            logging.warning(f"Failed to update order via OrderService: {str(e)}.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order update: {str(e)}.")
            raise

    @staticmethod
    async def _calculate_total_price(order: Order) -> float:
        try:
            total_price = 0.0
            for item in order.burger_items:
                total_price += item.burger.price * item.quantity
            logging.debug(f"Total price for order {order.id} is {total_price} via OrderService.")
            return total_price
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order total price calculation: {str(e)}.")
            raise

    @staticmethod
    async def get_order_by_id_with_total_price(db: AsyncSession, order_id: int) -> OrderResponse:
        try:
            order_db = await crud_order.get_order_by_id(db, order_id)
            if order_db is None:
                logging.debug(f"Order with id {order_id} not found in DB.")
                return None

            total_price = await OrderService._calculate_total_price(order_db)

            customer_response = None
            if order_db.customer:
                customer_response = CustomerResponse.model_validate(order_db.customer)

            order_data = {
                "id": order_db.id,
                "customer": customer_response,
                "customer_id": order_db.customer_id,
                "created_at": order_db.created_at,
                "status": order_db.status,
                "burgers_with_quantity": order_db.burgers_with_quantity,
                "total_price": total_price}

            order_response = OrderResponse.model_validate(order_data)

            logging.info(f"Order {order_id} ('{order_db.id}') found successfully in DB by ID via OrderService.")
            return order_response
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order retrieval by ID: {str(e)}.")
            raise

    @staticmethod
    async def get_all_orders(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[OrderResponse]:
        try:
            orders_db = await crud_order.get_all_orders(db, offset, limit)
            orders_response = []

            for order_db in orders_db:
                total_price = await OrderService._calculate_total_price(order_db)

                customer_response = None
                if order_db.customer:
                    customer_response = CustomerResponse.model_validate(order_db.customer)

                order_data = {
                    "id": order_db.id,
                    "customer": customer_response,
                    "customer_id": order_db.customer_id,
                    "created_at": order_db.created_at,
                    "status": order_db.status,
                    "burgers_with_quantity": order_db.burgers_with_quantity,
                    "total_price": total_price}

                order_response = OrderResponse.model_validate(order_data)
                orders_response.append(order_response)

            logging.debug(f"Retrieved {len(orders_response)} orders, offset={offset}, limit={limit} via OrderService.")
            return orders_response
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order retrieval: {str(e)}.")
            raise

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: int) -> Optional[OrderResponse]:
        try:
            order = await OrderService.get_order_by_id_with_total_price(db, order_id)
            if order is None:
                logging.warning(f"Order with id {order_id} not found for deletion via OrderService.")
                return None
            await crud_order.delete_order(db, order_id)
            logging.info(f"Order {order_id} deleted successfully via OrderService.")
            return order
        except Exception as e:
            logging.error(f"Unexpected error in OrderService during order deletion: {str(e)}.")