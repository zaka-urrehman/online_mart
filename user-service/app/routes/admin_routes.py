from fastapi import APIRouter, Depends, HTTPException 
from typing import Annotated
from app.models.user_models import UserRegister, User
from app.controllers.admin_crud import add_admin_in_db, get_all_admins, delete_admin_from_db, update_admin_in_db
from app.controllers.auth_user import login_user, get_current_user

router = APIRouter()

@router.get("/get-admins")
def get_admins(current_user: Annotated[User, (Depends(get_current_user))], admins: Annotated[list, (Depends(get_all_admins))]):
    """
    Get all admins from the database. This endpoint uses the `get_all_admins` dependency
    to fetch all admins from the database and return them.

    Returns:
        admins: A list of all admins in the database.
    """
    return {
        "message" : "admins fetched successfully",
        "admins" : admins
    }

@router.post("/add-admin")
def add_admin(new_admin: Annotated[UserRegister, (Depends(add_admin_in_db))]):
    """
    Add a new admin to the database. This endpoint uses the `add_admin_in_db` dependency
    to add the admin to the database and return the new admin.

    Returns:
        new_admin: The new admin object.
    """
    return {
        "message" : "admin added successfully",
        "admin" : {
            "username" : new_admin.first_name + " " + new_admin.last_name,
            "email" : new_admin.email,
            "phone" : new_admin.phone   
        }
    }

@router.put("/update-admin")
def update_admin(current_user: Annotated[User, (Depends(get_current_user))], updated_admin: Annotated[User, (Depends(update_admin_in_db))]):
    """
    Update an admin in the database by their ID. This endpoint
    uses the `update_admin_in_db` dependency to update the admin
    in the database and return the updated admin.

    Returns:
        updated_admin: The updated admin object.
    """
    return {
        "message" : "admin updated successfully",
        "admin" : updated_admin
    }

@router.delete("/delete-admin")
def delete_admin(current_user: Annotated[User, (Depends(get_current_user))], message: Annotated[dict, (Depends(delete_admin_from_db))]):
    """
    Delete an admin from the database by their ID. This endpoint uses the
    `delete_admin_from_db` dependency to delete the admin in the database and
    return a message indicating the success of the deletion.

    Returns:
        dict: A dictionary with a message key indicating the success of the deletion.
    """
    return message


# currently same auth process is used for admin and user, but the admin auth process will be seprate from user in future
@router.post("/login-admin")
def login_user(token: Annotated[str, (Depends(login_user))]):
    """
    Login an admin. This endpoint uses the `login_user` dependency to generate
    a token for the user and return it.

    Returns:
        token (str): The token to be returned.
    """
    if not token:
        HTTPException(
            status_code=400, detail="Try again, something occurred while generating token.")
    return token
