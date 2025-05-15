from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.core.dependencies import get_db_session
from src.database.crud import order as crud
from src.database.schemes.order import *

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(
        order_in: OrderCreate,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        return await crud.create_order(db, order_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logging.error(f"Unhandled exception in create_new_order: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")

@router.put("/{burger_id}", response_model=OrderResponse)
async def update_existing_order(
        order_id: int,
        order_in: OrderUpdate,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        updated_order = await crud.update_order(db, order_id, order_in)
        if updated_order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logging.error(f"Unhandled exception in update_existing_order for ID {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update order")

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
        order_id: int,
        db: AsyncSession = Depends(get_db_session)
        ):
    db_order = await crud.get_order_by_id(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return db_order

@router.get("/", response_model=List[OrderResponse])
async def read_all_orders(
        offset: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session)
        ):
    return await crud.get_all_orders(db, offset, limit)

@router.delete("/{order_id}", response_model=OrderResponse)
async def delete_existing_order(
        order_id: int,
        db: AsyncSession = Depends(get_db_session)
        ):
    try:
        deleted_order = await crud.delete_order(db, order_id)
        if deleted_order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return deleted_order
    except Exception as e:
        logging.error(f"Unhandled exception in delete_existing_order for ID {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete order")