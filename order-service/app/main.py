import asyncio

from fastapi import FastAPI 
from contextlib import asynccontextmanager

from app.routes import cart_routes, order_routes
from app.db.db_connection import create_db_and_tables
from app.kafka.consumer import consume_payment_status_events
from app.settings import KAFKA_PAYMENT_STATUS_TOPIC




@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    # Create a Kafka consumer task for the  topic
    task = asyncio.create_task(consume_payment_status_events(KAFKA_PAYMENT_STATUS_TOPIC, 'broker:19092'))

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
    root_path="/order-service",
    lifespan=lifespan
)

app.include_router(cart_routes.router, prefix="/cart", tags=["cart"])
app.include_router(order_routes.router, prefix="/order", tags=["order"])

@app.get("/")
def read_root():
    return "Order Service is up and running!"