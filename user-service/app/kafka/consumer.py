from aiokafka import AIOKafkaConsumer
import asyncio
from sqlmodel import Session

from app.db.db_connection import engine
from app.protobuf import user_pb2
from app.models.user_models import UserRegister
from app.controllers.user_crud import add_user_in_db

async def consume_user_events(topic: str, bootstrap_servers: str):
    """
    Generic Kafka consumer function that consumes messages from the given topic.
    Args:
        topic (str): The Kafka topic to listen to.
        bootstrap_servers (str): The Kafka bootstrap server.
    """
    # Create a Kafka consumer instance
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-group",
        auto_offset_reset='earliest'
    )

    # Start the Kafka consumer
    await consumer.start()
    try:
        # Continuously listen for messages from Kafka
        async for msg in consumer:
            print(f"Received message from Kafka: {msg.value}")

            # Deserialize the Protobuf message
            user = user_pb2.UserRegister()
            user.ParseFromString(msg.value)

            # Prepare the data for the database
            user_data = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "status": user.status,
                "password": user.password
            }

            # Manually create a session for this operation
            with Session(engine) as session:
                # Call add_user_in_db to insert the user
                await add_user_in_db(UserRegister(**user_data), session)

    finally:
        # Ensure to close the consumer when done
        await consumer.stop()
        print("Kafka consumer stopped.")


# TODO - Instead of adding each user to the database as soon as they are consumed, the consumer can accumulate users in a buffer and periodically insert them into the database in bulk.