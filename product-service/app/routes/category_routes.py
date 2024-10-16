from fastapi import APIRouter, Depends
from typing import Annotated, Any

from app.utils.auth import get_current_user
from app.models.models import Category, AddCategory
from app.db.db_connection import DB_SESSION
from app.controllers.category_crud import (
    get_all_categories,
    get_category_by_id,
    add_category_in_db,
    update_category_in_db,
    delete_category_from_db
)

router = APIRouter()

# --------------------------------------------------------------------------
@router.get("/categories")
async def get_categories( categories: Annotated[list[Category], Depends(get_all_categories)]):
    """
    Retrieve all categories from the database.
    """
    return {
        "message": "Categories fetched successfully",
        "categories": categories
    }

# --------------------------------------------------------------------------
@router.get("/{cat_id}")
async def get_category(category: Annotated[Category, Depends(get_category_by_id)]):
    """
    Retrieve a category by its ID.
    """
    return {
        "message": "Category fetched successfully",
        "category": category
    }

# --------------------------------------------------------------------------
@router.post("/add-category")
async def add_category(current_user: Annotated[Any, (Depends(get_current_user))], category: Annotated[Category, Depends(add_category_in_db)]):
    """
    Add a new category to the database.
    """
    return {
        "message": "Category added successfully",
        "category": category
    }

# --------------------------------------------------------------------------
@router.put("/update-category/{cat_id}")
async def update_category(current_user: Annotated[Any, (Depends(get_current_user))], category: Annotated[Category, Depends(update_category_in_db)]):
    """
    Update an existing category by its ID.
    """
    return {
        "message": "Category updated successfully",
        "category": category
    }

# --------------------------------------------------------------------------
@router.delete("/delete-category/{cat_id}")
async def delete_category(current_user: Annotated[Any, (Depends(get_current_user))], result: Annotated[dict, Depends(delete_category_from_db)]):
    """
    Delete a category by its ID.
    """
    return result
