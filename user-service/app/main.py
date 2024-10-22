import asyncio
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
from contextlib import asynccontextmanager

from app.routes import user_routes, admin_routes
from app.db.db_connection import create_db_and_tables
from app.kafka.consumer import consume_user_events
from app.settings import KAFKA_USER_TOPIC


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    # Create a Kafka consumer task for the 'user-events' topic
    task = asyncio.create_task(consume_user_events(KAFKA_USER_TOPIC, 'broker:19092'))

    # Yield to let the application start
    yield

    # On app shutdown, stop the Kafka consumer task
    task.cancel()  # Ensure the task is canceled on shutdown
    try:
        await task
    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")


app = FastAPI(
    title = "User and Admin Service",
    description = "API for user",
    lifespan = lifespan,
    openapi_tags = [
        {"name": "Users", "description": "Operations with users"}
    ],
    root_path="/user-service"
)

app.include_router(user_routes.router, prefix="/api/user", tags=["users"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["admins"])


@app.get("/")
def read_root():
    return("User Service is up and running!")