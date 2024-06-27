# Bookstore API Project Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Key Features](#key-features)
3. [File Structure](#file-structure)
4. [Services](#services)
   - [AI Service (BookProcessor)](#1-ai-service-bookprocessor)
   - [Email Service](#2-email-service)
   - [Notification Service](#3-notification-service)
   - [Messaging Services](#4-messaging-services)
5. [Main Application Structure](#5-main-application-structure)
6. [Routes Module Documentation](#routes-module-documentation)
7. [API Documentation](#api-documentation)
8. [Installation](#installation)
9. [Usage](#usage)
10. [Docker Deployment](#docker-deployment)

## Introduction

This project implements a robust bookstore API powered by Flask, providing features like user authentication, book management, notification systems, and AI-powered functionalities. The project is designed for efficient deployment and scalability using Docker and Docker Compose.

## Key Features

* **User Authentication:** Securely register and login users and admins, allowing them to interact with the system.
* **Book Management:** Add, update, delete, and retrieve information about books. Admin-only operations are restricted.
* **Notification System:** Send email notifications to users based on different events.
* **AI Integration:** Leverage OpenAI API for book summaries and short description generation.
* **File Upload:** Allow admins to upload book files (PDF) to the server.
* **RESTful API:** Provides a structured and consistent API for interacting with the bookstore data and placing orders.
* **Dockerized Deployment:** Encapsulated in Docker containers for easy deployment and management.
* **Database Integration:** Uses MySQL to store and manage data.
* **Message Queue:** Implements RabbitMQ to handle asynchronous tasks and notifications.

## File Structure

The project is structured as follows:

```
Book_store/
├── api
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   ├── __init__.py
├── config.py
├── messaging
│   ├── rabbitmq_handler.py
│   └── __init__.py
├── services
│   ├── ai_service.py
│   ├── email_services.py
│   ├── inventory_management.py
│   ├── notification_service.py
│   ├── order_processing.py
│   ├── shipping_service.py
│   └── __init__.py
├── app.py
├── Dockerfile
└── docker-compose.yml
```

## Services

### 1. AI Service (BookProcessor)

#### Purpose
The AI Service, implemented through the `BookProcessor` class, processes book data and generates AI-based summaries and descriptions using OpenAI's GPT-4 turbo model.

#### Key Features
- Extract text from PDF files
- Generate book summaries
- Create brief book descriptions

#### Usage
```python
from services.ai_service import BookProcessor

processor = BookProcessor(book_id, app)
summary = processor.process_book(mode='summary')
description = processor.process_book(mode='description')
```

#### Dependencies
- PyPDF2
- openai
- Flask

#### Configuration
Ensure the OpenAI API key is set in the Flask app configuration:
```python
app.config['OPENAI_API_KEY'] = 'your-api-key-here'
```

### 2. Email Service

#### Purpose
The Email Service provides functionality to send emails with attached PDF books to users after a purchase.

#### Key Features
- Send emails with PDF attachments

#### Usage
```python
from services.email_services import send_book_email

success = send_book_email(email, file_path, book_title)
```

#### Dependencies
- Flask-Mail

#### Configuration
Ensure the following configurations are set in the Flask app:
```python
app.config['MAIL_SERVER'] = 'your-mail-server'
app.config['MAIL_PORT'] = your-mail-port
app.config['MAIL_USERNAME'] = 'your-username'
app.config['MAIL_PASSWORD'] = 'your-password'
app.config['MAIL_USE_TLS'] = True  # or False
app.config['MAIL_USE_SSL'] = False  # or True
```

### 3. Notification Service

#### Purpose
The Notification Service manages real-time notifications using WebSocket connections through Flask-SocketIO.

#### Key Features
- Handle client connections and disconnections
- Send order status updates to specific users
- Broadcast global notifications to all connected clients

#### Usage
```python
from services.notification_service import init_socketio, send_order_status_update, send_global_notification

# Initialize SocketIO with your Flask app
init_socketio(app)

# Send an order status update
send_order_status_update(user_id, order_id, status)

# Send a global notification
send_global_notification(message)
```

#### Dependencies
- Flask-SocketIO

#### Configuration
Initialize SocketIO with your Flask app:
```python
from services.notification_service import init_socketio

init_socketio(app)
```

### 4. Messaging Services

#### Overview
The messaging services handle various aspects of order processing, inventory management, and shipping. These services use RabbitMQ for asynchronous communication between different parts of the application.

#### Components

##### 4.1 Inventory Management

**Purpose**: Manages the inventory updates based on order processing.

**Key Features**:
- Update inventory based on order data
- Handle insufficient stock scenarios
- Process inventory updates asynchronously

**Usage**:
```python
from services.inventory_management import update_inventory, start_inventory_processing

# Update inventory
update_inventory(update_data)

# Start inventory processing thread
start_inventory_processing()
```

##### 4.2 Order Processing

**Purpose**: Handles the creation and processing of orders.

**Key Features**:
- Create new orders
- Process orders asynchronously
- Update order status
- Initiate inventory updates and shipping

**Usage**:
```python
from services.order_processing import process_order, start_order_processing

# Process a new order
order = process_order(current_user, order_data)

# Start order processing thread
start_order_processing()
```

##### 4.3 Shipping Service

**Purpose**: Manages the shipping process for orders.

**Key Features**:
- Simulate shipping process
- Update order status
- Send notifications about order status
- Handle order delivery or cancellation

**Usage**:
```python
from services.shipping_service import initiate_shipping

# Initiate shipping for an order
initiate_shipping(order_id)
```

##### 4.4 RabbitMQ Handler

**Purpose**: Manages communication with RabbitMQ for asynchronous messaging.

**Key Features**:
- Publish orders and inventory updates to RabbitMQ queues
- Consume messages from RabbitMQ queues
- Handle connection to RabbitMQ

**Usage**:
```python
from messaging.rabbitmq_handler import rabbitmq, setup_rabbitmq

# Setup RabbitMQ with Flask app
setup_rabbitmq(app)

# Publish an order
rabbitmq.publish_order(order_data)

# Publish an inventory update
rabbitmq.publish_inventory_update(update_data)

# Start consuming orders
rabbitmq.process_orders(order_callback)

# Start consuming inventory updates
rabbitmq.process_inventory_updates(inventory_callback)
```

#### Dependencies
- pika (for RabbitMQ communication)
- Flask
- SQLAlchemy (implied by the use of `db.session`)

#### Configuration
Ensure the following configuration is set in your Flask app:

```python
app.config['RABBITMQ_URL'] = 'your-rabbitmq-url-here'
```

## 5. Main Application Structure

### Overview
This section covers the main structure of the bookstore application, including the app configuration, database models, and the main application file.

### Components

#### 5.1 Application Configuration (config.py)

The `Config` class in `config.py` defines the configuration settings for the application. It uses the `python-decouple` library to manage environment variables.

**Key Configurations**:
- Database settings (MySQL with PyMySQL)
- RabbitMQ URL
- OpenAI API key
- File upload settings
- CORS settings
- Email settings

**Usage**:
```python
from config import Config

app.config.from_object(Config)
```

#### 5.2 Database Models (models.py)

The `models.py` file defines the database models using SQLAlchemy ORM.

**Models**:
1. **User**
   - Attributes: id, username, email, password_hash, is_admin
   - Methods: set_password, check_password

2. **Book**
   - Attributes: id, title, author, price, pdf_path, stock, description

3. **Order**
   - Attributes: id, user_id, book_id, status, created_at, items
   - Methods: to_dict

4. **OrderStatus** (Enum)
   - Values: PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED

**Usage**:
```python
from app import db
from api.models import User, Book, Order, OrderStatus

# Create a new user
new_user = User(username="john_doe", email="john@example.com")
new_user.set_password("secure_password")
db.session.add(new_user)
db.session.commit()
```

#### 5.3 Main Application (app.py)

The `app.py` file is responsible for creating and configuring the Flask application.

**Key Features**:
- Initializes Flask extensions (SQLAlchemy, LoginManager, Mail, SocketIO, RabbitMQ)
- Registers blueprints
- Creates database tables
- Sets up user loader for Flask-Login

**Usage**:
```python
from app import create_app

app = create_app()
app.run()
```

## Routes Module Documentation

### Overview

This module defines the API routes for a bookstore application using Flask. It includes functionality for user authentication, book management, order processing, and notifications.

### Dependencies

- Flask
- Flask-Login
- SQLAlchemy (implied by the use of `db.session`)
- Custom services:
  - `notification_service`
  - `order_processing`
  - `inventory_management`
  - `ai_service`

### Key Components

#### Background Tasks

- `start_background_tasks()`: Initializes background threads for order processing and inventory management.

#### File Handling

- `allowed_file(filename)`: Checks if a file has an allowed extension (currently only PDF).

#### User Management

- `/create_admin` (POST): Creates an administrator account.
- `/register` (POST): Registers a new user.
- `/login` (POST): Logs in an existing user.
- `/logout` (GET): Logs out the current user.

#### Book Management

- `/books` (POST): Adds a new book to the bookstore.
- `/books/<int:book_id>` (PATCH): Updates an existing book.
- `/books/<int:book_id>` (DELETE): Deletes an existing book.
- `/books` (GET): Retrieves a list of all books.
- `/books/<int:book_id>` (GET): Retrieves a specific book by ID.
- `/books/<int:book_id>/summary` (GET): Retrieves a summary of a book.

#### Order Management

- `/orders` (POST): Places an order for a book.
- `/orders/<int:order_id>` (GET): Retrieves the status of an order.
- `/orders/<int:order_id>/cancel` (POST): Cancels an order.

#### Notifications

- `/notify` (POST): Sends a global notification to all connected clients.

### Authentication

Most routes require authentication using Flask-Login. Admin-specific routes check for `current_user.is_admin`.

### Error Handling

The module includes error handling for various scenarios, such as missing fields, unauthorized access, and database errors.

### File Upload

Book PDFs can be uploaded and are saved securely using `werkzeug.utils.secure_filename`.

### AI Integration

The module uses an AI service (`BookProcessor`) to generate summaries for books.

## API Documentation

### Authentication

#### Login
- **URL:** `/login`
- **Method:** `POST`
- **Data Params:** 
  ```json
  {
    "email": "[valid email address]",
    "password": "[password in plain text]"
  }
  ```
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "message": "Logged in successfully" }`
- **Error Response:** 
  - **Code:** 401
  - **Content:** `{ "message": "Invalid username or password" }`

#### Logout
- **URL:** `/logout`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "message": "Logged out successfully" }`

### User Management

#### Register User
- **URL:** `/register`
- **Method:** `POST`
- **Data Params:** 
  ```json
  {
    "username": "[username]",
    "email": "[valid email address]",
    "password": "[password in plain text]"
  }
  ```
- **Success Response:** 
  - **Code:** 201
  - **Content:** `{ "message": "User registered successfully" }`
- **Error Response:** 
  - **Code:** 400
  - **Content:** `{ "message": "Error registering user", "error": "[error message]" }`

#### Create Admin
- **URL:** `/create_admin`
- **Method:** `POST`
- **Data Params:** 
  ```json
  {
    "username": "[username]",
    "email": "[valid email address]",
    "password": "[password in plain text]"
  }
  ```
- **Success Response:** 
  - **Code:** 201
  - **Content:** `{ "message": "Admin account created successfully" }`
- **Error Response:** 
  - **Code:** 400
  - **Content:** `{ "message": "Admin account already exists" }`

### Book Management

#### Add Book
- **URL:** `/books`
- **Method:** `POST`
- **Headers:** `Content-Type: multipart/form-data`
- **Data Params:** 
  - `title`: String
  - `author`: String
  - `price`: Number
  - `stock`: Number
  - `pdf`: File (PDF)
- **Success Response:** 
  - **Code:** 201
  - **Content:** `{ "message": "Book added successfully", "book_id": [book_id] }`
- **Error Response:** 
  - **Code:** 400
  - **Content:** `{ "message": "Missing required fields" }`

#### Update Book
- **URL:** `/books/<book_id>`
- **Method:** `PATCH`
- **Headers:** `Content-Type: multipart/form-data`
- **Data Params:** 
  - `title`: String (optional)
  - `author`: String (optional)
  - `price`: Number (optional)
  - `stock`: Number (optional)
  - `pdf`: File (PDF) (optional)
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "message": "Book updated successfully" }`
- **Error Response:** 
  - **Code:** 500
  - **Content:** `{ "message": "Error updating book", "error": "[error message]" }`

#### Delete Book
- **URL:** `/books/<book_id>`
- **Method:** `DELETE`
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "message": "Book deleted successfully" }`
- **Error Response:** 
  - **Code:** 500
  - **Content:** `{ "message": "Error deleting book", "error": "[error message]" }`

#### Get All Books
- **URL:** `/books`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200
  - **Content:** Array of book objects
    ```json
    [
      {
        "id": 1,
    "title": "Book Title",
        "author": "Author Name",
        "price": 19.99,
        "stock": 10
      },
      ...
    ]
    ```

#### Get Single Book
- **URL:** `/books/<book_id>`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200
  - **Content:** Book object
    ```json
    {
      "id": 1,
      "title": "Book Title",
      "author": "Author Name",
      "price": 19.99,
      "stock": 10,
      "description": "Book description"
    }
    ```

#### Get Book Summary
- **URL:** `/books/<book_id>/summary`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "summary": "[book summary]" }`

### Order Management

#### Place Order
- **URL:** `/orders`
- **Method:** `POST`
- **Data Params:** 
  ```json
  {
    "book_id": 1,
    "quantity": 2
  }
  ```
- **Success Response:** 
  - **Code:** 201
  - **Content:** `{ "message": "Order placed successfully", "order_id": [order_id] }`
- **Error Response:** 
  - **Code:** 400
  - **Content:** `{ "error": "Order processing failed, try again" }`

#### Get Order Status
- **URL:** `/orders/<order_id>`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "status": "[order status]" }`
- **Error Response:** 
  - **Code:** 403
  - **Content:** `{ "message": "Unauthorized" }`

#### Cancel Order
- **URL:** `/orders/<order_id>/cancel`
- **Method:** `POST`
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "message": "Order cancelled successfully", "status": "[new status]" }`
- **Error Response:** 
  - **Code:** 400
  - **Content:** `{ "message": "Order cannot be cancelled", "status": "[current status]" }`

### Notifications

#### Send Global Notification
- **URL:** `/notify`
- **Method:** `POST`
- **Data Params:** 
  ```json
  {
    "message": "[notification message]"
  }
  ```
- **Success Response:** 
  - **Code:** 200
  - **Content:** `{ "message": "Notification sent" }`

Note: All endpoints except for registration, login, and public book listings require authentication. Make sure to include the necessary authentication headers or cookies in your requests.

## Installation

1. **Clone the repository:** 
    ```bash
    git clone https://github.com/DivineUX23/Book_store.git
    ```
2. **Install dependencies:**
    ```bash
    cd Book_store
    pip install -r requirements.txt
    ```
3. **Configure environment variables:**
    * Create a `.env` file in the project root directory.
    * Set the necessary environment variables as specified in the `config.py` file. Example:
      ```
      DATABASE_URI=mysql+pymysql://username:password@localhost/bookstore
      SECRET_KEY=your_secret_key
      RABBITMQ_URL=amqp://guest:guest@localhost:5672/
      OPENAI_API_KEY=your_openai_api_key
      MAIL_SERVER=smtp.example.com
      MAIL_PORT=587
      MAIL_USERNAME=your_email@example.com
      MAIL_PASSWORD=your_email_password
      MAIL_USE_TLS=True
      MAIL_USE_SSL=False
      ```
4. **Set up the database:**
    * Create a MySQL database named `bookstore`.
    * The tables will be automatically created when you run the application for the first time.

## Usage

1. **Start the application:**
    ```bash
    python app.py
    ```
2. **Access the API endpoints:**
    * Use a REST client like Postman or curl to interact with the API.
    * The API will be available at `http://localhost:5000` by default.
    * Refer to the API documentation section for details on available endpoints and usage.

## Docker Deployment

1. **Build the Docker image:**
    ```bash
    docker build -t Book_store .
    ```
2. **Start the Docker containers:**
    ```bash
    docker-compose up -d
    ```
3. **Access the API:**
    * The API will be available at `http://localhost:8080`.
4. **Stop the Docker containers:**
    ```bash
    docker-compose down
    ```

Note: Make sure you have Docker and Docker Compose installed on your system before attempting the Docker deployment.
