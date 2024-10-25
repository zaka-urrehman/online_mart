from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Any
from app.db.db_connection import DB_SESSION
from app.controllers.inventory_controller import modify_product_quantity,increase,decrease,set
from app.utils.auth import get_current_user

router = APIRouter()

# Route for increasing product quantity
@router.post("/increase-quantity/{product_id}")
async def increase_quantity(
    # current_user: Annotated[Any, (Depends(get_current_user))],
    product_id: int,
    quantity: int,   
    result : Annotated[dict, Depends(increase)],
):
    return result

# Route for decreasing product quantity
@router.post("/decrease-quantity/{product_id}")
async def decrease_quantity(
    # current_user: Annotated[Any, (Depends(get_current_user))],
    product_id: int,
    quantity: int,
    result: dict = Depends(decrease)
):
    return result

# Route for setting product quantity
@router.post("/set-quantity/{product_id}")
async def set_quantity(
    # current_user: Annotated[Any, (Depends(get_current_user))],
    product_id: int,
    quantity: int,
    result: dict = Depends(set)
):
    return result
