from flask import current_app
from messaging.rabbitmq_handler import rabbitmq
from api.models import Order, OrderStatus, db
import json
from services.notification_service import send_order_status_update
from services.shipping_service import initiate_shipping


def process_order(current_user, order_data):
    """
    Processes a new order.

    This function creates a new order in the database, publishes it to RabbitMQ for further processing, and sends an initial order status notification.

    Args:
        current_user: The user creating the order.
        order_data: The order data as a dictionary.

    Returns:
        The newly created order object, or None if an error occurred.
    """
    try:
        order = Order(user_id=current_user, book_id=order_data['book_id'], items=order_data['items'], status=OrderStatus.PENDING)

        db.session.add(order)
        db.session.commit()
    except Exception as e:
         current_app.logger.error(f"Error creating order: {str(e)}")
         return None

    rabbitmq.publish_order({
        'order_id': order.id,
        'items': order.items
    })

    # Send initial notification
    send_order_status_update(order.user_id, order.id, order.status.value)

    return order


def order_processor(ch, method, properties, body):
    """
    Processes an order message received from RabbitMQ.

    This function updates the order status to 'PROCESSING', sends a notification about the status update, publishes an inventory update message, and initiates the shipping process.

    Args:
        ch: The RabbitMQ channel.
        method: The delivery method.
        properties: The message properties.
        body: The message body.
    """
    order_data = json.loads(body)
    current_app.logger.info(f"Processing order: {order_data}")

    order = Order.query.get(order_data['order_id'])
    order.status = OrderStatus.PROCESSING
    db.session.commit()

    # Send notification about status update
    send_order_status_update(order.user_id, order.id, order.status.value)

    rabbitmq.publish_inventory_update({
        'order_id': order.id,
        'items': order.items
    })

    # After inventory is updated, initiate shipping
    initiate_shipping(order.id)


import threading
def start_order_processing():
    """
    Starts a separate thread to consume orders from RabbitMQ.
    """
    threading.Thread(target=rabbitmq.process_orders, args=(order_processor,), daemon=True).start()