import pika
import json
from flask import current_app

class RabbitMQHandler:
    """
    A class for handling RabbitMQ communication.

    This class provides methods for publishing and consuming messages from RabbitMQ queues.
    """

    def __init__(self, app=None):
        """
        Initializes the RabbitMQHandler.

        Args:
            app: The Flask application instance.
        """
        self.app = app
        self.connection = None
        self.channel = None
        if app is not None:
            self.init_app(app)


    def init_app(self, app):
        """
        Initializes the RabbitMQ connection and declares queues.

        Args:
            app: The Flask application instance.
        """
        self.app = app
        app.extensions['rabbitmq'] = self

        try:
            # Establish a connection to RabbitMQ
            parameters = pika.URLParameters(app.config['RABBITMQ_URL'])
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare queues
            self.channel.queue_declare(queue='order_processing')
            self.channel.queue_declare(queue='inventory_update')
        except Exception as e:
            app.logger.error(f"Failed to connect to RabbitMQ: {e}")


    def publish_order(self, order_data):
        """
        Publishes an order to the 'order_processing' queue.

        Args:
            order_data: The order data as a dictionary.
        """
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='order_processing',
                body=json.dumps(order_data)
            )
            current_app.logger.info(f"Published order to RabbitMQ: {order_data}")
        except Exception as e:
            current_app.logger.error(f"Failed to publish order: {e}")


    def process_orders(self, callback):
        """
        Consumes orders from the 'order_processing' queue.

        Args:
            callback: A function to be called for each received order.
        """
        try:
            self.channel.basic_consume(
                queue='order_processing',
                on_message_callback=callback,
                auto_ack=True
            )
            current_app.logger.info("Started consuming orders from RabbitMQ")
            self.channel.start_consuming()
        except Exception as e:
            current_app.logger.error(f"Failed to consume orders: {e}")


    def publish_inventory_update(self, update_data):
        """
        Publishes an inventory update to the 'inventory_update' queue.

        Args:
            update_data: The inventory update data as a dictionary.
        """
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='inventory_update',
                body=json.dumps(update_data)
            )
            current_app.logger.info(f"Published inventory update to RabbitMQ: {update_data}")
        except Exception as e:
            current_app.logger.error(f"Failed to publish inventory update: {e}")


    def process_inventory_updates(self, callback):
        """
        Consumes inventory updates from the 'inventory_update' queue.

        Args:
            callback: A function to be called for each received inventory update.
        """
        try:
            self.channel.basic_consume(
                queue='inventory_update',
                on_message_callback=callback,
                auto_ack=True
            )
            current_app.logger.info("Started consuming inventory updates from RabbitMQ")
            self.channel.start_consuming()
        except Exception as e:
            current_app.logger.error(f"Failed to consume inventory updates: {e}")


    def close(self):
        """ Gracefully closes the RabbitMQ connection. """
        if self.connection and not self.connection.is_closed:
            self.channel.close()
            self.connection.close()
            current_app.logger.info("RabbitMQ connection closed.")


rabbitmq = RabbitMQHandler()


def setup_rabbitmq(app):
    """
    Sets up the RabbitMQHandler for the Flask application.

    Args:
        app: The Flask application instance.
    """
    rabbitmq.init_app(app)
    # Register a teardown function to close the connection on app shutdown
    app.teardown_appcontext(lambda exception: rabbitmq.close())
