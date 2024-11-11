from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    link = Column(String, nullable=False)
    file_metadata = relationship("FileMetadata", back_populates="book", uselist=False)

class FileMetadata(Base):
    __tablename__ = 'file_metadata'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_size = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    book = relationship("Book", back_populates="file_metadata")

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/my_lab2"

engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

Base.metadata.create_all(engine)

def add_book(name, author, price, link):
    session = Session()
    try:
        new_book = Book(name=name, author=author, price=price, link=link)
        session.add(new_book)
        session.commit()
        print(f"Book '{name}' by '{author}' added to the database.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {str(e)}")
    finally:
        session.close()

def add_file_metadata(book_id, filename, file_size):
    session = Session()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            print(f"Book with ID {book_id} not found.")
            return

        existing_file = session.query(FileMetadata).filter(FileMetadata.filename == filename).first()
        if existing_file:
            print(f"A file with the name '{filename}' already exists. Please use a unique name.")
            return

        new_file_metadata = FileMetadata(
            filename=filename,
            file_size=file_size,
            book_id=book.id
        )
        session.add(new_file_metadata)
        session.commit()
        print(f"File '{filename}' added to the database and linked to book ID {book_id}.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while adding file metadata: {str(e)}")
    finally:
        session.close()

def get_all_books_with_files():
    session = Session()
    try:
        books = session.query(Book).all()
        return [
            {
                "id": book.id,
                "name": book.name,
                "author": book.author,
                "price": book.price,
                "link": book.link,
                "file_metadata": {
                    "filename": book.file_metadata.filename,
                    "upload_time": book.file_metadata.upload_time,
                    "file_size": book.file_metadata.file_size
                } if book.file_metadata else None
            }
            for book in books
        ]
    except Exception as e:
        print(f"An error occurred while fetching books: {str(e)}")
        return []
    finally:
        session.close()

def delete_file_metadata(file_id):
    session = Session()
    try:
        file_metadata = session.query(FileMetadata).filter(FileMetadata.id == file_id).first()
        if not file_metadata:
            print(f"File metadata with ID {file_id} not found.")
            return

        session.delete(file_metadata)
        session.commit()
        print(f"File metadata with ID {file_id} deleted successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while deleting the file metadata: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    books = get_all_books_with_files()
    for book in books:
        print(book)
