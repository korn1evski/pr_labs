from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    file_path = Column(String, nullable=True)  # For storing the uploaded file path

    __table_args__ = (
        UniqueConstraint('name', 'author', name='unique_book'),
    )
