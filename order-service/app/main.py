from fastapi import FastAPI 
from contextlib import asynccontextmanager
from app.routes import cart_routes, order_routes
from app.db.db_connection import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    yield



app = FastAPI(
    root_path="/order-service",
    lifespan=lifespan
)

app.include_router(cart_routes.router, prefix="/cart", tags=["cart"])
app.include_router(order_routes.router, prefix="/order", tags=["order"])

@app.get("/")
def read_root():
    return "Order Service is up and running!"