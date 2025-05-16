from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database.crud import customer as customer_crud
from src.database.models.customer import Customer
from src.database.schemes.customer import CustomerCreate, CustomerUpdate

class CustomerService:
    @staticmethod
    async def create_customer(db: AsyncSession, customer_in: CustomerCreate) -> Customer:
        try:
            db_customer = await customer_crud.create_customer(db, customer_in)
            logging.info(f"Customer {db_customer.id} created successfully via CustomerService.")
            return db_customer
        except ValueError as e:
            logging.warning(f"Failed to create customer via CustomerService: {str(e)}.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in CustomerService during customer creation: {str(e)}.")
            raise

    @staticmethod
    async def update_customer(db: AsyncSession, customer_id: int, customer_in: CustomerUpdate) -> Optional[Customer]:
        try:
            db_customer = await customer_crud.update_customer(db, customer_id, customer_in)
            if db_customer is None:
                logging.warning(f"Customer with id {customer_id} not found for update via CustomerService.")
                return None
            logging.info(f"Customer {db_customer.id} updated successfully via CustomerService.")
            return db_customer
        except ValueError as e:
            logging.warning(f"Failed to update customer via CustomerService: {str(e)}.")
        except Exception as e:
            logging.error(f"Unexpected error in CustomerService during customer update: {str(e)}.")
            raise

    @staticmethod
    async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        try:
            db_customer = await customer_crud.get_customer_by_id(db, customer_id)
            if db_customer is None:
                logging.debug(f"Customer with id {customer_id} not found in DB via CustomerService.")
                return None
            logging.debug(f"Customer {db_customer.id} ('{db_customer.name}') found successfully in DB by ID via CustomerService.")
            return db_customer
        except Exception as e:
            logging.error(f"Unexpected error in CustomerService during customer retrieval by ID: {str(e)}.")
            raise

    @staticmethod
    async def get_all_customers(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Customer]:
        try:
            db_customers = await customer_crud.get_all_customers(db, offset, limit)
            logging.debug(f"Retrieved {len(db_customers)} customers, offset={offset}, limit={limit} via CustomerService.")
            return db_customers
        except Exception as e:
            logging.error(f"Unexpected error in CustomerService during customer retrieval: {str(e)}.")
            raise

    @staticmethod
    async def delete_customer(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        try:
            db_customer = await customer_crud.delete_customer(db, customer_id)
            if db_customer is None:
                logging.warning(f"Customer with id {customer_id} not found for deletion via CustomerService.")
                return None
            logging.info(f"Customer {db_customer.id} deleted successfully via CustomerService.")
            return db_customer
        except Exception as e:
            logging.error(f"Unexpected error in CustomerService during customer deletion: {str(e)}.")
            raise