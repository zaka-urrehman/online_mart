from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Any

from app.kafka.producer import KAFKA_PRODUCER 
from app.models.user_models import UserRegister, User
from app.controllers.user_crud import add_user_in_db, get_all_users, delete_user_from_db, update_user_in_db, send_user_to_kafka, add_user_address
from app.controllers.auth_user import login_user, get_current_user 
from app.settings import KAFKA_USER_TOPIC

router = APIRouter()


@router.get("/get-users")
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

@router.post("/add-user")
async def add_user(new_user: UserRegister, producer: KAFKA_PRODUCER):
    """
    API endpoint to add a user. The user data is sent to Kafka in Protobuf format.
    """
    user_data = {
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email,
        "phone": new_user.phone,
        "status": "pending",  # Setting status to pending until processed by the consumer
        "password": new_user.password
    }

    # Try to send user data to Kafka
    try:
        await send_user_to_kafka(producer, KAFKA_USER_TOPIC, user_data)
    except Exception as e:
        print(f"Error while sending data to Kafka: {e}")
        raise HTTPException(status_code=500, detail="Failed to send data to Kafka")

    # If successful, return a confirmation message
    return {
        "message": "User data sent to Kafka successfully",
        "user": {
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "phone": new_user.phone
        }
    }

@router.put("/update-user")
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

@router.delete("/delete-user")
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


@router.post("/login-user")
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


@router.post("/add-user-address")
def add_address_to_user(current_user: Annotated[User, (Depends(get_current_user))], response: Annotated[Any, Depends(add_user_address)]):
    """
    Add an address to a user.
    """
    return response