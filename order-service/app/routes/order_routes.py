from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Any 
from sqlalchemy.orm import Session

from app.controllers.order_crud import (
    create_order, 
    get_order_by_id, 
    get_all_orders,
    update_order_status,
    delete_order
)
from app.models.order_models import OrderCreate, OrderStatusUpdate

router = APIRouter()

@router.post("/place-order", status_code=status.HTTP_201_CREATED)
def add_order(response : Annotated[Any, Depends(create_order)]):
    return response

@router.get("/orders/{order_id}")
def fetch_order(response: Annotated[Any, Depends(get_order_by_id)]):
    return response

@router.get("/orders")
def fetch_all_orders(response: Annotated[Any, Depends(get_all_orders)]):
    return response

@router.put("/update-status/{order_id}")
def change_order_status(response: Annotated[Any, Depends(update_order_status)]):
    return response

@router.delete("/delete-order/{order_id}")
def remove_order(response: Annotated[Any, Depends(delete_order)]):
    return response

