from sqlmodel import Session, select
from typing import Annotated
from fastapi import Depends, HTTPException
from aiokafka import AIOKafkaProducer

from app.protobuf import user_pb2
from app.kafka.producer import KAFKA_PRODUCER
from app.models.user_models import UserRegister, User
from app.db.db_connection import DB_SESSION
from app.utils.auth import hash_password

async def add_user_in_db(user_details: UserRegister, session: DB_SESSION):
    # Step-1: Check if user already exists (based on email or phone)
    statement = select(User).where((User.email == user_details.email) | (User.phone == user_details.phone))
    existing_user = session.exec(statement).first()  # Fetch the first result

    # Step-2: Raise an error if user already exists
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or phone already exists.")

    # Step-3: Hash the user's password
    hashed_password = hash_password(user_details.password)
    user_details.password = hashed_password  # Replace plain-text password with hashed password

    # Step-4: Create new user
    new_user = User(**user_details.model_dump())

    # Add and commit to the database
    session.add(new_user)
    session.commit()
    session.refresh(new_user)  # Refresh to get the newly created ID
    
    print("new user added in db: ",new_user)
    return new_user

#-----------------------------------------------------------------------------------------------------------------------
async def send_to_kafka(producer: AIOKafkaProducer, topic: str, user_data: dict):
    """
    Send serialized Protobuf data to Kafka topic.
    Args:
        producer (AIOKafkaProducer): Kafka producer instance.
        topic (str): Kafka topic to send data to.
        user_data (dict): User data to serialize and send.
    """
    try:
        # Create a Protobuf UserRegister object
        user = user_pb2.UserRegister()
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.email = user_data["email"]
        user.phone = user_data["phone"]
        user.status = user_data["status"]
        user.password = user_data["password"]

        # Serialize Protobuf object to binary format
        serialized_data = user.SerializeToString()
        print("serialized_data: ",serialized_data)
        # Send serialized data to Kafka
        await producer.send_and_wait(topic, serialized_data)
        print(f"Sent message to Kafka topic {topic}: {user_data}")
    
    except Exception as e:
        # Handle any exceptions during serialization or Kafka communication
        print(f"Failed to send message to Kafka: {e}")
        raise Exception(f"Error while sending data to Kafka: {e}")


#-----------------------------------------------------------------------------------------------------------------------

async def get_all_users(session: DB_SESSION):  
    try:
        # Step-1: Fetch all users from the database
        statement = select(User)
        users = session.exec(statement).all()  # Fetch all results       
        return users

    except HTTPException as e:
        # Step-3: Handle known HTTP exceptions (e.g., no users found)
        raise e

    except Exception as e:
        # Step-4: Handle any other unexpected exceptions
        print(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#-----------------------------------------------------------------------------------------------------------------------

async def update_user_in_db(user_id: int, user_details: User, session: DB_SESSION):
    try:
        # Step-1: Check if user exists
        user_to_update = session.get(User, user_id)
        if not user_to_update:
            raise HTTPException(status_code=400, detail="User not found")  # Fixed missing 'raise'

        # Step-2: Update the user's fields
        user_to_update.first_name = user_details.first_name
        user_to_update.last_name = user_details.last_name
        user_to_update.email = user_details.email
        user_to_update.phone = user_details.phone

        # Step-3: Hash the password if a new password is provided
        if user_details.password:
            hashed_password = hash_password(user_details.password)
            user_to_update.password = hashed_password
        else:
            # If no new password is provided, keep the current password
            user_to_update.password = user_to_update.password

        # Step-4: Commit the changes to the database
        session.commit()
        session.refresh(user_to_update)

        return user_to_update

    except HTTPException as e:
        raise e  # Re-raise known exceptions

    except Exception as e:
        print(f"An unexpected error occurred while updating the user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
#-----------------------------------------------------------------------------------------------------------------------

async def delete_user_from_db(user_id: int, session: DB_SESSION):
    try:
        # Step-1: Fetch the user by ID
        user_to_delete = session.get(User, user_id)

        # Step-2: If user does not exist, raise an error
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")

        # Step-3: Delete the user
        session.delete(user_to_delete)
        session.commit()

        return {"message": f"User with id {user_id} deleted successfully"}

    except HTTPException as e:
        raise e  # Re-raise known exceptions
    except Exception as e:
        print(f"An unexpected error occurred while deleting the user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")