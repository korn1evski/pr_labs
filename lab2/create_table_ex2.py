from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

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
engine = create_engine(DATABASE_URL)

# Create all tables in the database (if they don't already exist)
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


# Example to add a book (you can skip this if you just want to create the table)
def add_book(name, author, price, link):
    new_book = Book(name=name, author=author, price=price, link=link)
    session.add(new_book)
    session.commit()
    print(f"Book '{name}' by '{author}' added to the database.")


# Example usage
if __name__ == "__main__":
    # Uncomment below line if you want to add a book for testing
    # add_book("The Great Gatsby", "F. Scott Fitzgerald", 10.99, "https://example.com/greatgatsby")
    print("Book model and books table are ready.")
