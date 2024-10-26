from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Annotated, Any

from app.db.db_connection import DB_SESSION
from app.controllers.inventory_controller import modify_product_quantity,increase,decrease,set
from app.utils.auth import get_current_user, decode_jwt_token

router = APIRouter()

def check_admin_role(token: str):
    # Decode the JWT token
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = decode_jwt_token(token)
    # Check if the role is 'admin'
    user_role = payload.get("role")
    if user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Sorry, only admin can access this API"
        )

# Route for increasing product quantity
@router.post("/increase-quantity/{product_id}")
async def increase_quantity(
    # current_user: Annotated[Any, (Depends(get_current_user))],    
    result : Annotated[dict, Depends(increase)],
    authorization: Annotated[str, Header()],  
):
    check_admin_role(authorization)
    return result

# Route for decreasing product quantity
@router.post("/decrease-quantity/{product_id}")
async def decrease_quantity(
    # current_user: Annotated[Any, (Depends(get_current_user))],   
    result : Annotated[dict, Depends(decrease)],
    authorization: Annotated[str, Header()],  
):
    check_admin_role(authorization)
    return result

# Route for setting product quantity
@router.post("/set-quantity/{product_id}")
async def set_quantity(
    # current_user: Annotated[Any, (Depends(get_current_user))],   
    result: Annotated[dict, Depends(set)],
    authorization: Annotated[str, Header()],  
):
    check_admin_role(authorization)
    return result
