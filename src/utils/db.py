from prentice_logger import logger

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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
logger.info("PostgreSQL Con nection Established!")

def get_db():
    """This function is used to inject db_session dependency in every REST API requests"""

    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Rollback the db if any exception occurs
        logger.error("Error when yielding DB with SQLAlchemy")
        db.rollback()
    finally:
        # Close db session
        db.close()
