from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from enum import Enum


class User(UserMixin, db.Model):
    """
    Represents a user in the application.

    Attributes:
        id: The unique identifier for the user.
        username: The user's username.
        email: The user's email address.
        password_hash: The hashed password for the user.
        is_admin: Indicates if the user is an administrator.
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """
        Sets the user's password.

        Args:
            password: The plain-text password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided password matches the stored password hash.

        Args:
            password: The plain-text password to check.

        Returns:
            True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)



class Book(db.Model):
    """
    Represents a book in the application.

    Attributes:
        id: The unique identifier for the book.
        title: The title of the book.
        author: The author of the book.
        price: The price of the book.
        pdf_path: The path to the PDF file for the book.
        stock: The number of copies in stock.
        description: A description of the book.
    """
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(255))
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)


class OrderStatus(Enum):
    """
    Represents the possible statuses of an order.
    """
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class Order(db.Model):
    """
    Represents an order in the application.

    Attributes:
        id: The unique identifier for the order.
        user_id: The ID of the user who placed the order.
        book_id: The ID of the book ordered.
        status: The current status of the order.
        created_at: The timestamp when the order was created.
        items: A dictionary containing the items in the order (just incase).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)   
    items = db.Column(db.JSON, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': self.items,
            'status': self.status.value
        }
