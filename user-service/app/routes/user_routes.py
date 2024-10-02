from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from app.models.user_models import UserRegister, User
from app.controllers.user_crud import add_user_in_db, get_all_users, delete_user_from_db, update_user_in_db
from app.controllers.auth_user import login_user, get_current_user 

router = APIRouter()


@router.get("/get_users")
def get_users(current_user: Annotated[User, (Depends(get_current_user))], users: Annotated[list, (Depends(get_all_users))]):
    """
    Get all users from the database. This endpoint uses the `get_all_users` dependency
    to fetch all users from the database and return them.

    Returns:
        users: A list of all users in the database.
    """
    return {
        "message" : "users fetched successfully",
        "users" : users
    } 

@router.post("/add_user")
def add_user(new_user : Annotated[UserRegister, (Depends(add_user_in_db))]):
    """
    Add a new user to the database. This endpoint uses the `add_user_in_db` dependency
    to add the user to the database and return the new user.    

    Returns:
        new_user: The new user object.
    """
    return {
            "message" : "user added successfully",
            "user" : {
                    "username" : new_user.first_name + " " + new_user.last_name,
                    "email" : new_user.email,
                    "phone" : new_user.phone
                }
            }

@router.put("/update_user")
def update_user(current_user: Annotated[User, (Depends(get_current_user))], updated_user: Annotated[User, (Depends(update_user_in_db))]):
    """
    Update a user in the database by their ID. This endpoint
    uses the `update_user_in_db` dependency to update the user
    in the database and return the updated user.    

    Returns:
        updated_user: The updated user object.
    """
    return {
            "message" : "user updated successfully",
            "user" : updated_user
        }

@router.delete("/delete_user")
def delete_user(current_user: Annotated[User, (Depends(get_current_user))], message: Annotated[dict, (Depends(delete_user_from_db))]):
    """
    Delete a user from the database by their ID. This endpoint uses the
    `delete_user_from_db` dependency to delete the user in the database and
    return a message indicating the success of the deletion.

    Returns:
        dict: A dictionary with a message key indicating the success of the
        deletion.
    """
    return message


@router.post("/login_user")
def login_user(token: Annotated[str, (Depends(login_user))]):
    """
    Login a user. This endpoint uses the `login_user` dependency to generate
    a token for the user and return it.

    Returns:
        token (str): The token to be returned.
    """
    if not token:
        HTTPException(
            status_code=400, detail="Try again, something occurred while generating token.")
    return token 