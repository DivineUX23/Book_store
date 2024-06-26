import os
from decouple import config

class Config:
    """
    Base configuration class for the application.

    This class defines the default configuration settings for the application.
    """

    # Basic configuration
    SECRET_KEY = config('SECRET_KEY', default='secret-key')
    DEBUG = config('DEBUG', default=False, cast=bool)
    
    # Database configuration
    DB_NAME = config('DB_NAME')
    DB_USER = config('DB_USER')
    DB_PASSWORD = config('DB_PASSWORD')
    DB_HOST = config('DB_HOST')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # RabbitMQ configuration
    RABBITMQ_URL = config('RABBITMQ_URL', default='amqp://guest:guest@localhost:5672/%2F')
    
    # OpenAI configuration
    OPENAI_API_KEY = config('OPENAI_API_KEY')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdfs')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for file uploads
    
    # CORS configuration
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')

    # Email configuration
    MAIL_SERVER = config('MAIL_SERVER', default='smtp.gmail.com')
    MAIL_PORT = config('MAIL_PORT', default=587, cast=int)
    MAIL_USE_TLS = config('MAIL_USE_TLS', default=True, cast=bool)
    MAIL_USERNAME = config('MAIL_USERNAME')
    MAIL_PASSWORD = config('MAIL_PASSWORD')