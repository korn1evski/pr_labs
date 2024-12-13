import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@postgres_lab_2:5432/my_lab2"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    retries = 5  # Retry up to 5 times
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to create tables... (Attempt {attempt + 1}/{retries})")
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created successfully.")
            break
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)  # Wait before retrying
    else:
        logger.error("Failed to create tables after several attempts.")
