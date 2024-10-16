from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from typing import Annotated
from datetime import datetime
from sqlalchemy import select 

from app.models.models import Size, AddSize
from app.db.db_connection import DB_SESSION

# --------------------------------------------------------------------------
def get_all_sizes(session: DB_SESSION):
    """
    Retrieve all sizes from the database.
    """
    # doing this because the simple select(Size) was not returning data in proper format(it was wrapping each item in tuple)
    statement = select(Size.size_id, Size.size_name, Size.created_at, Size.updated_at)
    result = session.exec(statement).all()

    # This should now directly give us the size objects without tuple wrapping
    sizes = [Size(size_id=r[0], size_name=r[1], created_at=r[2], updated_at=r[3]) for r in result]
    
    print("--------------------------------------------------------------------------: " , sizes)
    return sizes


# --------------------------------------------------------------------------
def get_size_by_id(size_id: int, session: DB_SESSION):
    """
    Retrieve a size by its ID.
    """
    size = session.get(Size, size_id)
    if not size:
        raise HTTPException(status_code=404, detail="Size not found.")
    return size

# --------------------------------------------------------------------------
def add_size_in_db(new_size: AddSize, session: DB_SESSION):
    """
    Add a new size to the database if it doesn't already exist.
    """
    # Check if a size with the same name already exists
    statement = select(Size).where(Size.size_name == new_size.size_name)
    existing_size = session.exec(statement).first()

    if existing_size:
        raise HTTPException(status_code=400, detail="Size with this name already exists.")

    # Create a new size
    size_to_add = Size(
        size_name=new_size.size_name,
    )
    session.add(size_to_add)
    session.commit()
    session.refresh(size_to_add)  # Get the newly created size with its ID

    return size_to_add

# --------------------------------------------------------------------------
def update_size_in_db(size_id: int, updated_data: AddSize, session: DB_SESSION):
    """
    Update a size by its ID.
    """
    size = session.get(Size, size_id)
    if not size:
        raise HTTPException(status_code=404, detail="Size not found.")

    # Update the size fields
    size.size_name = updated_data.size_name
    size.updated_at = datetime.utcnow()  # Update the 'updated_at' field to the current time

    session.commit()
    session.refresh(size)
    return size

# --------------------------------------------------------------------------
def delete_size_from_db(size_id: int, session: DB_SESSION):
    """
    Delete a size by its ID.
    """
    size = session.get(Size, size_id)
    if not size:
        raise HTTPException(status_code=404, detail="Size not found.")

    session.delete(size)
    session.commit()

    return {"message": "Size deleted successfully"}
