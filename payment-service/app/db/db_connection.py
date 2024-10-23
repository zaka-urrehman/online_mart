from app.settings import DATABASE_URL
from sqlmodel import create_engine, SQLModel, Session
from fastapi import Depends 
from typing import Annotated

connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string,
    connect_args={},
    # echo=True,
    pool_recycle=3600,
    pool_pre_ping=True, 
    pool_timeout=30,
)

def get_session():
    with Session(engine) as session:
        yield session

DB_SESSION = Annotated[Session, Depends(get_session)]

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)