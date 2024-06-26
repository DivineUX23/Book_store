from flask import current_app, jsonify
from messaging.rabbitmq_handler import rabbitmq
from api.models import Book, Order, db, OrderStatus
import json
from services.notification_service import send_order_status_update


class InsufficientStockError(Exception):
    """
    Custom exception raised when insufficient stock is available.
    """
    pass

def update_inventory(update_data):
    """
    Updates inventory based on the provided order data.

    This function checks stock availability for all items in the order, updates the inventory if sufficient stock is available, and updates the order status accordingly.

    Args:
        update_data: A dictionary containing order ID and items with quantities.
    """

    current_app.logger.info(f"Updating inventory: {update_data}")
    
    order = Order.query.get(update_data['order_id'])
    
    try:
        for item in update_data['items']:
            book = Book.query.get_or_404(item['book_id'])
            if not book:
                raise ValueError(f"Book with id {item['book_id']} not found")
            if book.stock < item['quantity']:
                raise InsufficientStockError(f"Insufficient stock for book {book.title}")

        for item in update_data['items']:
            book = Book.query.get_or_404(item['book_id'])
            book.stock -= item['quantity']
            db.session.add(book)
        
        order.status = OrderStatus.PROCESSING

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.info(f"Inventory update failed {order.id}")
            return jsonify({'message': 'Error updating Inventory', 'error': str(e)}), 500

        current_app.logger.info(f"Inventory updated successfully for order {order.id}")
        # Send notification about status update
        send_order_status_update(order.user_id, order.id, order.status.value)

    except InsufficientStockError as e:
        current_app.logger.error(f"Insufficient stock for order {order.id}: {str(e)}")
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        send_order_status_update(order.user_id, order.id, order.status.value)

    except Exception as e:
        current_app.logger.error(f"Error processing order {order.id}: {str(e)}")
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        send_order_status_update(order.user_id, order.id, order.status.value)


def inventory_processor(ch, method, properties, body):
    """
    Processes an inventory update message received from RabbitMQ.

    This function calls the `update_inventory` function to handle the inventory update based on the message content.

    Args:
        ch: The RabbitMQ channel.
        method: The delivery method.
        properties: The message properties.
        body: The message body.
    """
    update_data = json.loads(body)
    update_inventory(update_data)

# Start consuming inventory updates in a separate thread
import threading
def start_inventory_processing():
    """
    Starts a separate thread to consume inventory updates from RabbitMQ.
    """
    threading.Thread(target=rabbitmq.process_inventory_updates, args=(inventory_processor,), daemon=True).start()