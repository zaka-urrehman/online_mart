import json
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaConsumer

from app.db.db_connection import create_db_and_tables
from app.kafka.consumer import consume_order_events
from app.settings import KAFKA_ORDER_TOPIC
from app.routes import payment_routes 


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    # Create a Kafka consumer task for the topic
    task = asyncio.create_task(consume_order_events(KAFKA_ORDER_TOPIC, 'broker:19092'))

    # Yield to let the application start
    yield

    # On app shutdown, stop the Kafka consumer task
    print("Stopping Kafka consumer...")
    task.cancel()  # Ensure the task is canceled on shutdown
    try:
        await task
    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")


app = FastAPI(
    root_path="/payment-service",
    lifespan=lifespan, 
    title="Payment Service",
    openapi_tags=[
        {"name": "Payment", "description": "Service for Payment"}
    ]
) 

# Include the webhook router
app.include_router(payment_routes.router, prefix="/payment", tags=["payment"])

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/testing-route")
def testing(anything: str):
    return {"message": anything}