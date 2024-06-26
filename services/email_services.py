from flask_mail import Message
from app import mail
from flask import current_app

#print(config("MAIL_USERNAME"), config("MAIL_PASSWORD"))

def send_book_email(email, file_path, book_title):
    """
    Sends an email with an attached PDF book.

    This function sends an email containing a message and attaches the PDF file of the purchased book.

    Args:
        email: The recipient's email address.
        file_path: The path to the PDF file.
        book_title: The title of the book.

    Returns:
        True if the email was sent successfully, False otherwise.
    """

    subject = f"Your book: {book_title}"
    body = f"Thank you for your purchase. Please find attached your book: {book_title}"
    
    msg = Message(subject=subject,
                  recipients=[email],
                  body=body)
    
    with current_app.open_resource(file_path) as fp:
        msg.attach(filename=f"{book_title}.pdf", content_type="application/pdf", data=fp.read())

    try:    
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Error sending book email: {str(e)}")
        return False
    
    return True