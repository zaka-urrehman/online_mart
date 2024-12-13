from fastapi import FastAPI 
from contextlib import asynccontextmanager

from app.routes import category_routes, size_routes, product_routes
from app.db.db_connection import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()

    yield


app = FastAPI(
    root_path="/product-service",
    lifespan=lifespan
)


app.include_router(category_routes.router, prefix="/category", tags=["category"])
# app.include_router(size_routes.router, prefix="/size", tags=["size"])
app.include_router(product_routes.router, prefix="/product", tags=["product"])

@app.get("/")
def read_root():
    return {"message": "Product Service is up and running!"}