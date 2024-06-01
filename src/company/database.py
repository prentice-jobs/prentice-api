import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")
SUPABASE_DB = os.getenv("SUPABASE_DB")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

try:
    # Database url configuration
    DATABASE_URL = (
        "postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}".format(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            db_name=SUPABASE_DB,
            username=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
        )
    )

except Exception:
    raise ValueError("Database config values are missing or incorrect.")

if DATABASE_URL is None:
    raise ValueError("DB_URL environment variable is not set!")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
