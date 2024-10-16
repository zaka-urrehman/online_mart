from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.models import Category, AddCategory
from app.db.db_connection import DB_SESSION

# --------------------------------------------------------------------------
def get_all_categories(session: DB_SESSION):
    """
    Retrieve all categories from the database.
    """
    statement = select(Category)
    result = session.exec(statement).all()
    return result

# --------------------------------------------------------------------------
def get_category_by_id(cat_id: int, session: DB_SESSION):
    """
    Retrieve a category by its ID.
    """
    category = session.get(Category, cat_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category

# --------------------------------------------------------------------------
def add_category_in_db(new_category: AddCategory, session: DB_SESSION):
    """
    Add a new category to the database if it doesn't already exist.
    """
    # Step 1: Check if a category with the same name already exists
    statement = select(Category).where(Category.cat_name == new_category.cat_name)
    existing_category = session.exec(statement).first()

    if existing_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists.")

    # Step 2: Convert AddCategory to Category and add it to the database
    category_to_add = Category(
        cat_name=new_category.cat_name,
        description=new_category.description
    )

    session.add(category_to_add)
    session.commit()
    session.refresh(category_to_add)  # Get the newly created category with its ID

    return category_to_add


# --------------------------------------------------------------------------
def update_category_in_db(cat_id: int, updated_data: AddCategory, session: DB_SESSION):
    """
    Update a category by its ID.
    """
    category = session.get(Category, cat_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    
    # Update category fields
    category.cat_name = updated_data.cat_name
    category.description = updated_data.description
    category.updated_at = datetime.utcnow()

    
    session.commit()
    session.refresh(category)
    return category

# --------------------------------------------------------------------------
def delete_category_from_db(cat_id: int, session: DB_SESSION):
    """
    Delete a category by its ID.
    """
    category = session.get(Category, cat_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    session.delete(category)
    session.commit()
    return {"message": "Category deleted successfully"}
