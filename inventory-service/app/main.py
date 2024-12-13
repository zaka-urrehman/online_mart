import asyncio

from fastapi import FastAPI 
from contextlib import asynccontextmanager

from app.routes import inventory_routes
from app.db.db_connection import create_db_and_tables
from app.kafka.consumer import consume_add_product_events
from app.settings import KAFKA_ADD_PRODUCT_TOPIC

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    # Create a Kafka consumer task for the  topic
    task = asyncio.create_task(consume_add_product_events(KAFKA_ADD_PRODUCT_TOPIC, 'broker:19092'))

    yield
    # On app shutdown, stop the Kafka consumer task
    print("Stopping Kafka consumer...")
    task.cancel()  # Ensure the task is canceled on shutdown
    try:
        await task
    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")



app = FastAPI(
    root_path="/inventory-service",
    lifespan=lifespan
)


app.include_router(inventory_routes.router, prefix="/inventory", tags=["inventory"])
# app.include_router(size_routes.router, prefix="/size", tags=["size"])
# app.include_router(product_routes.router, prefix="/product", tags=["product"])

@app.get("/")
def read_root():
    return {"message": "Inventory Service is up and running!"}