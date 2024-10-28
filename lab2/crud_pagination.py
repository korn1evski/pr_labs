from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# Initialize Flask app
app = Flask(__name__)

# Database connection settings
DATABASE_URL = "postgresql+psycopg2://postgres:drago2002@127.0.0.1:5432/pr_lab2"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")  # Using AUTOCOMMIT for immediate commits

# Create a scoped session to properly manage individual sessions for each request
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

# Define the base class for declarative class definitions
Base = declarative_base()

# Define the Book model (table structure)
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    link = Column(String, nullable=False)

# Create all tables in the database (if they don't already exist)
Base.metadata.create_all(engine)

# CRUD API Endpoints

# Add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    session = Session()  # Create a new session for this request
    try:
        new_book = Book(
            name=data['name'],
            author=data['author'],
            price=data['price'],
            link=data['link']
        )
        session.add(new_book)
        session.commit()
        return jsonify({'message': 'Book added successfully!', 'book_id': new_book.id}), 201

    except Exception as e:
        session.rollback()
        return jsonify({'message': 'An error occurred while adding the book.', 'error': str(e)}), 500

    finally:
        session.close()

# Get all books with pagination
@app.route('/books', methods=['GET'])
def get_books():
    session = Session()  # Create a new session for this request
    try:
        # Get pagination parameters from query string
        offset = int(request.args.get('offset', 0))  # Default offset to 0 if not provided
        limit = int(request.args.get('limit', 10))   # Default limit to 10 if not provided

        # Expunge any cached data to ensure fresh data retrieval
        session.expunge_all()

        # Query the books with offset and limit
        books_query = session.query(Book).offset(offset).limit(limit).all()
        books = [
            {
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'price': book.price,
                'link': book.link
            }
            for book in books_query
        ]

        return jsonify(books)

    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching books.', 'error': str(e)}), 500

    finally:
        session.close()


# Get a specific book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    session = Session()  # Create a new session for this request
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({'message': 'Book not found'}), 404

        return jsonify({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'price': book.price,
            'link': book.link
        })

    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching the book.', 'error': str(e)}), 500

    finally:
        session.close()

# Update a book by ID
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    session = Session()  # Create a new session for this request
    try:
        # Query for the existing book by ID
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({'message': 'Book not found'}), 404

        # Update only the provided fields
        if 'name' in data:
            book.name = data['name']
        if 'author' in data:
            book.author = data['author']
        if 'price' in data:
            book.price = data['price']
        if 'link' in data:
            book.link = data['link']

        session.commit()
        session.refresh(book)  # Refresh to make sure the changes are immediately reflected

        return jsonify({
            'message': 'Book updated successfully!',
            'updated_book': {
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'price': book.price,
                'link': book.link
            }
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({'message': 'An error occurred while updating the book.', 'error': str(e)}), 500

    finally:
        session.close()

# Delete a book by ID
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    session = Session()  # Create a new session for this request
    try:
        # Query for the book by ID
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return jsonify({'message': 'Book not found'}), 404

        session.delete(book)
        session.commit()
        return jsonify({'message': 'Book deleted successfully!'})

    except Exception as e:
        session.rollback()
        return jsonify({'message': 'An error occurred while deleting the book.', 'error': str(e)}), 500

    finally:
        session.close()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)
