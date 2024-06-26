from flask import Flask
#from api.routes import api
from messaging.rabbitmq_handler import setup_rabbitmq
from services.notification_service import init_socketio
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    """
    Creates and configures the Flask application.

    This function initializes the Flask app, configures extensions, registers blueprints, creates database tables, and defines routes.

    Args:
        config_class: The configuration class to use for the app.

    Returns:
        The configured Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    try:
        db.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        init_socketio(app)
        setup_rabbitmq(app)
    except Exception as e:
        app.logger.error(f"Failed to initialize extensions: {e}")

    from api.routes import api
    app.register_blueprint(api, url_prefix='/api')

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return "Welcome to the Bookstore API"

    from api.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)