from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

CLOUDSQL_HOST = config("CLOUDSQL_HOST")
CLOUDSQL_PORT = config("CLOUDSQL_PORT")
CLOUDSQL_DB = config("CLOUDSQL_DB")
CLOUDSQL_USER = config("CLOUDSQL_USER")
CLOUDSQL_PASSWORD = config("CLOUDSQL_PASSWORD")

try:

    DATABASE_URL = (
        "postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}".format(
            port=CLOUDSQL_PORT,
            host=CLOUDSQL_HOST,
            db_name=CLOUDSQL_DB,
            username=CLOUDSQL_USER,
            password=CLOUDSQL_PASSWORD,
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
