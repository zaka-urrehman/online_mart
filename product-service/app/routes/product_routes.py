from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import  Annotated

from app.models.models import AddProduct, Product, ProductSize
from app.controllers.product_crud import (
    get_all_products, get_product_by_id, add_product_in_db,
    update_product_in_db, delete_product_from_db, assign_sizes_to_product
)

router = APIRouter()

# ========================================= GET ALL PRODUCTS =====================================================

@router.get("/products")
async def get_products(products: Annotated[list[Product], Depends(get_all_products)]):
    """
    Retrieve all products from the database.
    """
    return products

# ========================================= GET PRODUCT BY ID ====================================================

@router.get("/{product_id}")
async def get_product(product: Annotated[Product, Depends(get_product_by_id)]):
    """
    Retrieve a product by its ID.
    """
    return product

# ========================================= CREATE NEW PRODUCT ===================================================

@router.post("/add-product")
async def add_product(product: Annotated[Product, Depends(add_product_in_db)]):
    """
    Add a new product to the database.
    """
    return {
        "message": "Product added successfully",
        "product": product
    }
    
# ========================================= UPDATE PRODUCT =======================================================

@router.put("/update-product/{product_id}")
async def update_product(product_id: int, product: Annotated[Product, Depends(update_product_in_db)]):
    """
    Update an existing product.
    """
    return {"message" : "product updated successfully", "product" : product}
# ========================================= DELETE PRODUCT =======================================================

@router.delete("/delete-product/{product_id}")
async def delete_product(message: Annotated[dict, Depends(delete_product_from_db)]):
    """
    Delete a product by its ID.
    """
    return message

# ========================================= ASSIGN SIZES TO PRODUCT ==============================================

@router.post("/assign-sizes/{product_id}")
async def assign_sizes(product_id: int, size_ids: list[int], message: Annotated[dict, Depends(assign_sizes_to_product)]):
    """
    Assign sizes to a product.
    """
    return message
