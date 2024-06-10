from prentice_logger import logger
from firebase_admin import initialize_app as firebase_initialize_app

firebase_client = firebase_initialize_app()
logger.info(f"Initialized firebase client: {firebase_client.name}")