from fastapi import APIRouter, Depends, Header
from typing import Annotated , Any 

from app.controllers.cart_crud import (add_item_to_cart,
                                        get_cart_details, 
                                        remove_item_from_cart,
                                        update_cart)


router = APIRouter() 


@router.get("/get-cart")
def get_cart(
    response: Annotated[list, Depends(get_cart_details)],
    ):
    return response


@router.post("/add-to-cart")
def add_to_cart(message: Annotated[Any, Depends(add_item_to_cart)]):
    return message


@router.delete("/remove-item")
def remove_item(response : Annotated[Any, Depends(remove_item_from_cart)]):
    return response


@router.put("/update-cart")
def update_cart_route(response : Annotated[Any, Depends(update_cart)]):
    return response    

