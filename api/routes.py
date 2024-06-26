from flask import Flask, jsonify, request, Blueprint, current_app
from .models import db, Book, Order, OrderStatus, User
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from services.notification_service import send_order_status_update, send_global_notification
from services.order_processing import process_order, start_order_processing
from services.inventory_management import start_inventory_processing
from services.ai_service import BookProcessor
import os
from werkzeug.utils import secure_filename


api = Blueprint('api', __name__)

@api.before_app_first_request
def start_background_tasks():
    """
    Starts background tasks for order processing and inventory management.

    This function is called before the first request to the API blueprint. It initializes separate threads for order processing and inventory management to handle these tasks asynchronously.
    """
    start_order_processing()
    start_inventory_processing()


ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """
    Checks if a file has an allowed extension (currently only PDF).

    Args:
        filename: The name of the file to check.

    Returns:
        True if the filename has an allowed extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/create_admin', methods=['POST'])
def create_admin():
    """
    Creates an administrator account.

    This route handles POST requests to create an administrator account. It validates the request data, creates a new admin user, and persists it to the database.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """

    data = request.json
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    if User.query.filter_by(is_admin=True).first():
        return jsonify({'message': 'Admin account already exists'}), 400
    
    admin = User(username=data['username'], email=data['email'], is_admin=True)
    admin.set_password(data['password'])
    db.session.add(admin)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating admin account', 'error': str(e)}), 500
    return jsonify({'message': 'Admin account created successfully'}), 201



@api.route('/register', methods=['POST'])
def register():
    """
    Registers a new user.

    This route handles POST requests to register new users. It validates the request data, creates a new user, and persists it to the database.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """
    data = request.json
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error registering user', 'error': str(e)}), 500
    return jsonify({'message': 'User registered successfully'}), 201

@api.route('/login', methods=['POST'])
def login():
    """
    Logs in an existing user.

    This route handles POST requests to log in users. It validates the request data, authenticates the user, and sets the session if successful.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """

    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid username or password'}), 401


@api.route('/logout')
@login_required
def logout():
    """
    Logs out the current user.

    This route handles GET requests to log out the current user. It clears the session and returns a success message.

    Returns:
        A JSON response indicating success.
    """
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200



@api.route('/books', methods=['POST'])
@login_required
def add_book():
    """
    Adds a new book to the bookstore.

    This route handles POST requests to add new books. It validates the request data, uploads the PDF file, creates a new book entry, and persists it to the database. It also generates a summary for the book using AI.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """

    if not current_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    title = request.form.get('title')
    author = request.form.get('author')
    price = request.form.get('price')
    pdf_file = request.files.get('pdf')
    stock = request.form.get('stock')

    if not all([title, author, price, pdf_file, stock]):
        return jsonify({'message': 'Missing required fields'}), 400

    if pdf_file and allowed_file(pdf_file.filename):
        if pdf_file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'message': 'File too large'}), 413
        filename = secure_filename(pdf_file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        pdf_path = os.path.join(upload_folder, filename)

        pdf_file.save(pdf_path)

        book = Book(title=title, author=author, price=float(price), pdf_path=pdf_path, stock=int(stock))
        db.session.add(book)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            os.remove(pdf_path)
            return jsonify({'message': 'Error adding book', 'error': str(e)}), 500

        processor = BookProcessor(book.id, current_app)
        description = processor.process_book(mode='summary')
        book.description = description
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error updating book description', 'error': str(e)}), 500

        return jsonify({'message': 'Book added successfully', 'book_id': book.id}), 201
    
    return jsonify({'message': 'Invalid file format'}), 400



@api.route('/books/<int:book_id>', methods=['PATCH'])
@login_required
def update_book(book_id):
    """
    Updates an existing book.

    This route handles PATCH requests to update book information. It validates the request data, updates the book entry, and persists it to the database. It also generates a new summary if the PDF file is updated.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """
    if not current_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    book = Book.query.get_or_404(book_id)
    book.title = request.form.get('title', book.title)
    book.author = request.form.get('author', book.author)
    book.price = request.form.get('price', book.price)
    book.stock = request.form.get('stock', book.stock)

    pdf_file = request.files.get('pdf')
    if pdf_file and allowed_file(pdf_file.filename):
        filename = secure_filename(pdf_file.filename)
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        new_pdf_path = os.path.join(upload_folder, filename)

        pdf_file.save(new_pdf_path)
        
        old_pdf_path = book.pdf_path
        book.pdf_path = new_pdf_path

        processor = BookProcessor(book.id, current_app)
        book.description = processor.process_book(mode='summary')

    try:
        db.session.commit()
        if old_pdf_path:
            os.remove(old_pdf_path)
    except Exception as e:
        db.session.rollback()
        if 'new_pdf_path' in locals():
            os.remove(new_pdf_path)
        return jsonify({'message': 'Error updating book', 'error': str(e)}), 500

    return jsonify({'message': 'Book updated successfully'}), 200



@api.route('/books/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    """
    Deletes an existing book.

    This route handles DELETE requests to delete books. It validates the request, retrieves the book, deletes it from the database, and removes the associated PDF file.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """

    if not current_user.is_admin:
        return jsonify({'message': 'Admin access required'}), 403
    
    book = Book.query.get_or_404(book_id)
    pdf_path = book.pdf_path
    
    try:
        db.session.delete(book)
        db.session.commit()
        if pdf_path:
            os.remove(pdf_path)
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting book', 'error': str(e)}), 500

    return jsonify({'message': 'Book deleted successfully'}), 200


@api.route('/books', methods=['GET'])
def get_books():
    """
    Retrieves a list of all books.

    This route handles GET requests to retrieve a list of books. It retrieves all books from the database and returns them in a JSON format.

    Returns:
        A JSON response containing a list of books.
    """
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': book.price,
        'stock': book.stock
    } for book in books]), 200


@api.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Retrieves a specific book by ID.

    This route handles GET requests to retrieve a specific book by its ID. It retrieves the book from the database and returns it in a JSON format.

    Returns:
        A JSON response containing the book details.
    """
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': book.price,
        'stock': book.stock,
        'description': book.description
    }), 200


@api.route('/orders', methods=['POST'])
@login_required
def place_order():
    """
    Places an order for a book.

    This route handles POST requests to place orders for books. It validates the request data, processes the order, and returns a success message.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """
    data = request.json
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    try:
        order = process_order(current_user.id, data)
        if order is None:
            return jsonify({'error': 'Order processing failed, try again'}), 400
        return jsonify({'message': 'Order placed successfully', 'order_id': order.id}), 201
    except Exception as e:
        return jsonify({'message': 'Error processing order', 'error': str(e)}), 500


@api.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order_status(order_id):
    """
    Retrieves the status of an order.

    This route handles GET requests to retrieve the status of an order. It validates the user's authorization and returns the order status.

    Returns:
        A JSON response containing the order status.
    """

    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return jsonify({'status': order.status.value}), 200



@api.route('/books/<int:book_id>/summary', methods=['GET'])
def get_book_summary(book_id):
    """
    Retrieves a summary of a book.

    This route handles GET requests to retrieve a summary of a book. It uses the AI service to generate a summary and returns it.

    Returns:
        A JSON response containing the book summary.
    """
    book = Book.query.get_or_404(book_id)
    processor = BookProcessor(book_id, current_app)
    summary = processor.process_book(mode='summary')

    return jsonify({'summary': summary}), 200

@api.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """
    Cancels an order.

    This route handles POST requests to cancel orders. It validates the user's authorization, updates the order status to 'CANCELLED', and sends a notification.

    Returns:
        A JSON response indicating success or failure, along with any errors.
    """

    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'message': 'Unauthorized'}), 403

    if order.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        order.status = OrderStatus.CANCELLED
        try:
            db.session.commit()
            send_order_status_update(order.user_id, order.id, order.status.value)
            return jsonify({'message': 'Order cancelled successfully', 'status': order.status.value}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error cancelling order', 'error': str(e)}), 500
    else:
        return jsonify({'message': 'Order cannot be cancelled', 'status': order.status.value}), 400


@api.route('/notify', methods=['POST'])
def send_notification():
    """
    Sends a global notification to all connected clients.

    This route handles POST requests to send global notifications. It retrieves the message from the request and broadcasts it to all connected clients.

    Returns:
        A JSON response indicating success.
    """
    message = request.json.get('message')
    send_global_notification(message)
    return jsonify({'message': 'Notification sent'}), 200