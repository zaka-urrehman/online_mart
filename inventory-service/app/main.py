from fastapi import FastAPI 
from contextlib import asynccontextmanager

from app.routes import inventory_routes
from app.db.db_connection import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    yield


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