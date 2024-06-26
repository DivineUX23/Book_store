import os
from PyPDF2 import PdfReader
import openai
from flask import current_app
from api.models import Book


class BookProcessor:
    """
    A class to process book data and generate AI-based summaries and descriptions.

    This class encapsulates functionality related to:
    - Extracting text from a PDF file.
    - Generating summaries and descriptions using OpenAI's GPT-3 model.
    """

    def __init__(self, book_id, app):
        """
        Initializes the BookProcessor with book ID and Flask app instance.

        Args:
            book_id: The ID of the book to process.
            app: The Flask application instance.
        """
        self.book_id = book_id
        self.book = Book.query.get_or_404(book_id)
        self.pdf_path = self.book.pdf_path
        self.app = app
        openai.api_key = self.app.config('OPENAI_API_KEY')


    def extract_text_from_pdf(self):
        """
        Extracts text from the PDF file associated with the book.

        Returns:
            A string containing the extracted text.

        Raises:
            FileNotFoundError: If the PDF file is not found.
        """
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            raise FileNotFoundError("PDF file not found for this book.")
        
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def generate_openai_response(self, prompt, max_tokens=150):
        """
        Generates a response from OpenAI's GPT-3 model.

        Args:
            prompt: The prompt for the AI model.
            max_tokens: The maximum number of tokens for the response.

        Returns:
            A string containing the AI-generated response.

        Raises:
            Exception: If there's an error interacting with OpenAI.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.0-turbo",
                temperature=0.7,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            self.app.logger.error(f"Error generating OpenAI response: {str(e)}")
            return "Unable to generate response at this time."

    def generate_summary(self, text):
        """
        Generates a summary of the book text using OpenAI.

        Args:
            text: The extracted text from the PDF.

        Returns:
            A string containing the generated summary.
        """
        prompt = f"Please provide a detailed summary of the following book text: {text[:4000]}..."
        return self.generate_openai_response(prompt)


    def generate_description(self, text):
        """
        Generates a brief description of the book text using OpenAI.

        Args:
            text: The extracted text from the PDF.

        Returns:
            A string containing the generated description.
        """
        prompt = f"Please provide a very brief description of the following book text without revealing any spoilers: {text[:4000]}..."
        return self.generate_openai_response(prompt)


    def process_book(self, mode='summary'):
        """
        Processes the book to generate a summary or description.

        Args:
            mode: 'summary' or 'description', determines the type of AI processing.

        Returns:
            A string containing the generated summary or description.

        Raises:
            ValueError: If the mode is invalid.
        """
        text = self.extract_text_from_pdf()
        if mode == 'summary':
            return self.generate_summary(text)
        elif mode == 'description':
            return self.generate_description(text)
        else:
            raise ValueError("Invalid mode. Choose 'summary' or 'description'.")
