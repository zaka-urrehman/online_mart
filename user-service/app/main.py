from fastapi import FastAPI
from app.routes import user_routes
from app.routes import admin_routes
from app.db.db_connection import create_db_and_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


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