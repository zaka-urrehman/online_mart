import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes import notification_routes
from app.db.db_connection import create_db_and_tables
from app.kafka.consumer import consume_notification_events
from app.settings import KAFKA_NOTIFICATION_TOPIC


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    # Create a Kafka consumer task for the 'user-events' topic
    task = asyncio.create_task(consume_notification_events(KAFKA_NOTIFICATION_TOPIC, 'broker:19092'))

    # Yield to let the application start
    yield

    # On app shutdown, stop the Kafka consumer task
    task.cancel()  # Ensure the task is canceled on shutdown
    try:
        await task
    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")


app = FastAPI(
    root_path="/notification-service",
    lifespan=lifespan, 
    title="Notification Service",
    openapi_tags=[
        {"name": "Notification", "description": "Service for notifications"}
    ]
) 


app.include_router(notification_routes.router, prefix="/notification", tags=["notification"])
@app.get("/")
def read_root():
    return "Notification Service is up and running!"


