from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.core.dependencies import get_db_session
from src.database.crud import customer as crud
from src.database.schemes.customer import *

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_new_customer(
        customer_in: CustomerCreate,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        return await crud.create_customer(db, customer_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logging.error(f"Unhandled exception in create_new_customer: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create customer")

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_existing_customer(
        customer_id: int,
        customer_in: CustomerUpdate,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        updated_customer = await crud.update_customer(db, customer_id, customer_in)
        if updated_customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return updated_customer
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logging.error(f"Unhandled exception in update_existing_customer for ID {customer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update customer")

@router.get("/{customer_id}", response_model=CustomerResponse)
async def read_customer(
        customer_id: int,
        db: AsyncSession = Depends(get_db_session)
        ):
    db_customer = await crud.get_customer_by_id(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return db_customer

@router.get("/", response_model=List[CustomerResponse])
async def read_all_customers(
        offset: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session)
        ):
    return await crud.get_all_customers(db, offset, limit)

@router.delete("/{customer_id}", response_model=CustomerResponse)
async def delete_existing_customer(
        customer_id: int,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        deleted_customer = await crud.delete_customer(db, customer_id)
        if deleted_customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return deleted_customer
    except Exception as e:
        logging.error(f"Unhandled exception in delete_existing_customer for ID {customer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete customer")