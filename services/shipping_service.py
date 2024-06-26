from flask import current_app
from api.models import Order, OrderStatus, db, Book, User
from services.notification_service import send_order_status_update
import time
import threading
from .email_services import send_book_email

def initiate_shipping(order_id):
    """
    Initiates the shipping process for an order.

    This function creates a separate thread to simulate the shipping process, updating the order status and sending notifications.

    Args:
        order_id: The ID of the order to ship.
    """
    threading.Thread(target=ship_order, args=(order_id,), daemon=True).start()


def ship_order(order_id):
    """
    Simulates the shipping process for a given order ID.

    This function retrieves the order, book, and user information, sends the book via email, updates the order status, and sends notifications.

    Args:
        order_id: The ID of the order to process.
    """
    with current_app.app_context():
        order = Order.query.get(order_id)
        book = Book.query.get(order.book_id)
        user = User.query.get(order.user_id)

        #Send book via email
        send_book_email(user.email, book.pdf_path, book.title)

        order.status = OrderStatus.SHIPPED
        db.session.commit()

        # Send notification about status update
        send_order_status_update(order.user_id, order.id, order.status.value)

        current_app.logger.info(f"Order {order_id} has been shipped")

        if send_book_email == True:
            order.status = OrderStatus.DELIVERED
            db.session.commit()
            current_app.logger.info(f"Order {order_id} has been delivered")
        else:
            order.status = OrderStatus.CANCELLED
            db.session.commit()
            current_app.logger.info(f"Order {order_id} has failed")

        # Send notification about status update
        send_order_status_update(order.user_id, order.id, order.status.value)

        current_app.logger.info(f"Order {order_id} has been delivered")