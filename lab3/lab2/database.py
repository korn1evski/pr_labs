import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base

DATABASE_URL = "postgresql://postgres:postgres@postgres_lab_2:5432/my_lab2"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    retries = 5  # Retry up to 5 times
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)  # Wait before retrying
    else:
        print("Failed to create tables after several attempts.")
