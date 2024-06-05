from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.utils.settings import (
    POSTGRES_DB_HOST,
    POSTGRES_DB_PORT,
    POSTGRES_DB_NAME,
    POSTGRES_DB_USER,
    POSTGRES_DB_PASSWORD
)

try:
    DATABASE_URL = (
        "postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}".format(
            host=POSTGRES_DB_HOST,
            port=POSTGRES_DB_PORT,
            db_name=POSTGRES_DB_NAME,
            username=POSTGRES_DB_USER,
            password=POSTGRES_DB_PASSWORD,
        )
    )

except Exception:
    raise ValueError("Database config values are missing or incorrect.")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set!")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print("PostgreSQL Connection Established!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
