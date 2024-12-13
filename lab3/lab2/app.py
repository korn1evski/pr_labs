from flask import Flask, request, jsonify, send_file
from database import SessionLocal, create_tables
from models.models import Book
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create a new session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route('/books', methods=['POST'])
def create_book():
    db = next(get_db())
    data = request.form

    # Extract and validate required fields
    name = data.get('name')
    author = data.get('author')
    price = data.get('price')

    # Check if the required fields are provided
    if not name:
        return jsonify({"error": "Missing required field: name"}), 400
    if not author:
        return jsonify({"error": "Missing required field: author"}), 400
    if not price:
        return jsonify({"error": "Missing required field: price"}), 400

    # Validate that price is a valid number
    try:
        price = float(price)
    except ValueError:
        return jsonify({"error": "Price must be a valid number"}), 400

    file = request.files.get('file')

    # Check if book with same name and author exists
    if db.query(Book).filter_by(name=name, author=author).first():
        return jsonify({"error": "Book with the same name and author already exists"}), 400

    # Handle the uploaded file if present
    file_path = None
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

    new_book = Book(
        name=name,
        author=author,
        price=price,
        file_path=file_path
    )

    db.add(new_book)
    db.commit()

    return jsonify({"message": "Book added successfully", "book": {
        "id": new_book.id,
        "name": new_book.name,
        "author": new_book.author,
        "price": new_book.price,
        "file_path": new_book.file_path
    }}), 201

# Read all books with pagination
@app.route('/books', methods=['GET'])
def get_books():
    db = next(get_db())
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=5, type=int)

    books = db.query(Book).offset(offset).limit(limit).all()
    result = [{
        "id": book.id,
        "name": book.name,
        "author": book.author,
        "price": book.price,
        "file_path": book.file_path
    } for book in books]

    return jsonify(result)

# Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    db = next(get_db())
    data = request.form

    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        return jsonify({"error": "Book not found"}), 404

    book.name = data.get('name', book.name)
    book.author = data.get('author', book.author)
    book.price = float(data.get('price', book.price))

    db.commit()
    return jsonify({"message": "Book updated successfully"})

# Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    db = next(get_db())

    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.delete(book)
    db.commit()
    return jsonify({"message": "Book deleted successfully"})

# Download the file associated with a book
@app.route('/books/<int:book_id>/download', methods=['GET'])
def download_file(book_id):
    db = next(get_db())

    book = db.query(Book).filter_by(id=book_id).first()
    if not book or not book.file_path:
        return jsonify({"error": "File not found"}), 404

    return send_file(book.file_path, as_attachment=True)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
