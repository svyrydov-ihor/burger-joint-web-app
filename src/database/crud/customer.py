from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database.models.customer import Customer
from src.database.schemes.customer import CustomerCreate, CustomerUpdate

async def create_customer(db: AsyncSession, customer_in: CustomerCreate) -> Customer:
    existing_customer = await get_customer_by_phone(db, customer_in.phone)
    if existing_customer:
        raise ValueError("Customer with this phone already exists.")

    db_customer = Customer(**customer_in.model_dump())
    try:
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        logging.info(f"Customer {db_customer.id} created successfully.")
        return db_customer
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to create customer {customer_in.name}: {str(e)}.")
        raise

async def update_customer(db: AsyncSession, customer_id: int, customer_in: CustomerUpdate) -> Optional[Customer]:
    db_customer_to_update = await get_customer_by_id(db, customer_id)
    if not db_customer_to_update:
        logging.warning(f"Customer with id {customer_id} does not exist.")

    update_data = customer_in.model_dump(exclude_unset=True)

    if "phone" in update_data and update_data["phone"] != db_customer_to_update.phone:
        existing_customer_with_new_phone = await get_customer_by_phone(db, update_data["phone"])
        if existing_customer_with_new_phone and existing_customer_with_new_phone.id != customer_id:
            logging.warning(f"Attempt to update customer {customer_id} with phone number {update_data['phone']} that already exists for customer {existing_customer_with_new_phone.id}")
            raise ValueError(f"Phone number {update_data['phone']} is already in use by another customer.", params={}, orig=None)

    for key, value in update_data.items():
        setattr(db_customer_to_update, key, value)

    try:
        await db.commit()
        await db.refresh(db_customer_to_update)
        logging.info(f"Customer {db_customer_to_update.id} updated successfully.")
        return db_customer_to_update
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to update customer {customer_id}: {str(e)}.")
        raise

async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    query = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(query)
    customer = result.scalar_one_or_none()

    if not customer:
        logging.debug(f"Customer with id {customer_id} not found in DB.")
        return None

    logging.debug(f"Customer {customer.id} ('{customer.name}') found successfully in DB by ID.")
    return customer

async def get_customer_by_phone(db: AsyncSession, phone: str) -> Optional[Customer]:
    query = select(Customer).where(Customer.phone == phone)
    result = await db.execute(query)
    customer = result.scalar_one_or_none()

    if not customer:
        logging.debug(f"Customer with phone {phone} not found in DB.")
        return None

    logging.debug(f"Customer {customer.id} ('{customer.name}') found successfully in DB by phone.")
    return customer

async def get_all_customers(db: AsyncSession, offset: int = 0, limit: int = 100) -> List[Customer]:
    query = select(Customer).offset(offset).limit(limit).order_by(Customer.id)
    result = await db.execute(query)
    customers = result.scalars().all()
    logging.debug(f"Retrieved {len(customers)} customers, offset={offset}, limit={limit}.")
    return customers

async def delete_customer(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    existing_customer = await get_customer_by_id(db, customer_id)
    if not existing_customer:
        logging.warning(f"Customer with id {customer_id} not found for deletion.")
        return None
    try:
        await db.delete(existing_customer)
        await db.commit()
        logging.info(f"Customer {customer_id} deleted successfully.")
        return existing_customer
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to delete customer {customer_id}: {str(e)}.")
        raise