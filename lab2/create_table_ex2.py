from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

# Define the base class for declarative class definitions
Base = declarative_base()

# Define the Book model (table structure)
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Unique identifier, auto-incremented
    name = Column(String, nullable=False)  # Book name, cannot be null
    author = Column(String, nullable=False)  # Book author, cannot be null
    price = Column(Float, nullable=False)  # Book price, cannot be null
    link = Column(String, nullable=False)  # Link to the book, cannot be null

# Database connection settings
DATABASE_URL = "postgresql+psycopg2://postgres:drago2002@127.0.0.1:5432/pr_lab2"

# Create an engine that connects to the PostgreSQL server
engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")  # Using AUTOCOMMIT for instant database commits

# Create a scoped session to properly manage individual sessions for each request
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

# Create all tables in the database (if they don't already exist)
Base.metadata.create_all(engine)

# Example to add a book (each request has its own session)
def add_book(name, author, price, link):
    session = Session()  # Create a new session for this operation
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

# Example to get all books
def get_all_books():
    session = Session()  # Create a new session for this operation
    try:
        books = session.query(Book).all()
        return [
            {
                "id": book.id,
                "name": book.name,
                "author": book.author,
                "price": book.price,
                "link": book.link
            }
            for book in books
        ]
    except Exception as e:
        print(f"An error occurred while fetching books: {str(e)}")
        return []
    finally:
        session.close()

# Example to update a book by ID
def update_book(book_id, name=None, author=None, price=None, link=None):
    session = Session()  # Create a new session for this operation
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            print(f"Book with ID {book_id} not found.")
            return

        # Update fields if new values are provided
        if name:
            book.name = name
        if author:
            book.author = author
        if price:
            book.price = price
        if link:
            book.link = link

        session.commit()
        print(f"Book with ID {book_id} updated successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while updating the book: {str(e)}")
    finally:
        session.close()

# Example to delete a book by ID
def delete_book(book_id):
    session = Session()  # Create a new session for this operation
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            print(f"Book with ID {book_id} not found.")
            return

        session.delete(book)
        session.commit()
        print(f"Book with ID {book_id} deleted successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while deleting the book: {str(e)}")
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    # Uncomment below line if you want to add a book for testing
    # add_book("The Great Gatsby", "F. Scott Fitzgerald", 10.99, "https://example.com/greatgatsby")
    print("Book model and books table are ready.")
    # Example to fetch and print all books
    books = get_all_books()
    for book in books:
        print(book)
