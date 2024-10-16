from fastapi import APIRouter, Depends
from typing import Annotated,Any
from fastapi.encoders import jsonable_encoder

from app.utils.auth import get_current_user
from app.models.models import Size, AddSize, SizeResponse
from app.controllers.size_crud import (
    get_all_sizes,
    get_size_by_id,
    add_size_in_db,
    update_size_in_db,
    delete_size_from_db
)

router = APIRouter()

# --------------------------------------------------------------------------
@router.get("/sizes", response_model=list[SizeResponse])
async def get_sizes(sizes: Annotated[list[Size], Depends(get_all_sizes)]):
    """
    Retrieve all sizes from the database.
    """
    
    serialized_sizes = jsonable_encoder(sizes)
    print("Serialized Sizes:", serialized_sizes)  # Debugging
    return serialized_sizes

# --------------------------------------------------------------------------
@router.get("/{size_id}", response_model=Size)
async def get_size(size: Annotated[Size, Depends(get_size_by_id)]):
    """
    Retrieve a size by its ID.
    """
    return size

# --------------------------------------------------------------------------
@router.post("/add-size", response_model=Size)
async def add_size(current_user: Annotated[Any, (Depends(get_current_user))], size: Annotated[AddSize, Depends(add_size_in_db)]):
    """
    Add a new size to the database.
    """
    return size

# --------------------------------------------------------------------------
@router.put("/update-size/{size_id}", response_model=Size)
async def update_size(current_user: Annotated[Any, (Depends(get_current_user))], size: Annotated[Size, Depends(update_size_in_db)]):
    """
    Update a size by its ID.
    """
    return size

# --------------------------------------------------------------------------
@router.delete("/delete-size/{size_id}")
async def delete_size(current_user: Annotated[Any, (Depends(get_current_user))], result: Annotated[dict, Depends(delete_size_from_db)]):
    """
    Delete a size by its ID.
    """
    return result
