from app.settings import DATABASE_URL
from sqlmodel import create_engine, SQLModel

connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string,
    connect_args={},
    echo=True,
    pool_recycle=300,
    pool_pre_ping=True, 
    pool_timeout=30
)


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)