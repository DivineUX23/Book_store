from flask_socketio import SocketIO, emit
from flask import current_app

socketio = SocketIO()

def init_socketio(app):
    """
    Initializes the SocketIO instance for the Flask application.

    Args:
        app: The Flask application instance.
    """
    socketio.init_app(app, cors_allowed_origins="*")


@socketio.on('connect')
def handle_connect():
    """
    Handles client connection events.

    Logs a message indicating that a client has connected.
    """
    current_app.logger.info('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles client disconnection events.

    Logs a message indicating that a client has disconnected.
    """
    current_app.logger.info('Client disconnected')


def send_order_status_update(user_id, order_id, status):
    """
    Sends a real-time notification to a specific user about an order status update.

    This function emits a custom event with the order ID and status to the connected client.

    Args:
        user_id: The ID of the user receiving the notification.
        order_id: The ID of the order.
        status: The new order status.
    """
    event_name = f'order_status_update_{user_id}'
    data = {
        'order_id': order_id,
        'status': status
    }
    socketio.emit(event_name, data)
    current_app.logger.info(f'Sent order status update for order {order_id} to user {user_id}')


def send_global_notification(message):
    """
    Sends a global notification to all connected clients.

    This function emits a 'global_notification' event with the message to all connected clients.

    Args:
        message: The message to be sent.
    """
    socketio.emit('global_notification', {'message': message})
    current_app.logger.info(f'Sent global notification: {message}')