import os
import json
import uuid
import shutil
import streamlit as st
from datetime import datetime

# Path to the books data file
BOOKS_FILE_PATH = 'data/library.json'
SAMPLE_BOOKS_PATH = 'data/sample_books.json'

def get_user_library_path(user_id=None):
    """
    Get the path to the user's library file
    
    Args:
        user_id (str, optional): User ID. If None, the current user ID from session state is used.
        
    Returns:
        str: Path to the user's library file
    """
    if user_id is None:
        # If no user_id provided, check session state
        if 'user_id' in st.session_state:
            user_id = st.session_state.user_id
        else:
            # No logged-in user, use the default library
            return BOOKS_FILE_PATH
    
    # Return user-specific library path
    return os.path.join('data/users', f'{user_id}.json')

def load_books(user_id=None):
    """
    Load books from the JSON file
    
    Args:
        user_id (str, optional): User ID. If None, the current user ID from session state is used.
        
    Returns:
        list: List of book dictionaries
    """
    # Determine which library file to use
    library_path = get_user_library_path(user_id)
    
    # For guest users (not logged in), use the default behavior
    if library_path == BOOKS_FILE_PATH:
        if os.path.exists(BOOKS_FILE_PATH):
            try:
                with open(BOOKS_FILE_PATH, 'r') as f:
                    books = json.load(f)
                    if books:  # If the file exists and has data, return it
                        return books
                    # If file exists but is empty, try to load sample data
            except json.JSONDecodeError:
                pass  # Continue to the sample data loading if there's a JSON error
        
        # If library.json doesn't exist or is empty, check for sample data
        if os.path.exists(SAMPLE_BOOKS_PATH):
            try:
                with open(SAMPLE_BOOKS_PATH, 'r') as f:
                    sample_books = json.load(f)
                    # Create library.json with the sample data
                    with open(BOOKS_FILE_PATH, 'w') as out_f:
                        json.dump(sample_books, out_f, indent=4)
                    return sample_books
            except json.JSONDecodeError:
                pass  # Continue to creating an empty file if sample data is invalid
        
        # If no valid data found, create an empty file
        with open(BOOKS_FILE_PATH, 'w') as f:
            json.dump([], f)
        return []
    
    # For logged-in users, load from their library file
    if os.path.exists(library_path):
        try:
            with open(library_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If there's a JSON error, create an empty file
            with open(library_path, 'w') as f:
                json.dump([], f)
            return []
    
    # If user library doesn't exist, create an empty one
    with open(library_path, 'w') as f:
        json.dump([], f)
    return []

def save_books(books, user_id=None):
    """
    Save the entire book list to the JSON file
    
    Args:
        books (list): List of book dictionaries
        user_id (str, optional): User ID. If None, the current user ID from session state is used.
    """
    library_path = get_user_library_path(user_id)
    
    with open(library_path, 'w') as f:
        json.dump(books, f, indent=4)

def save_book(book_data, user_id=None):
    """
    Add a new book or update an existing one
    
    Args:
        book_data (dict): Book data dictionary
        user_id (str, optional): User ID. If None, the current user ID from session state is used.
        
    Returns:
        dict: Updated book data
    """
    books = load_books(user_id)
    
    # If book has an ID, it's an update
    if 'id' in book_data and book_data['id']:
        # Find and update the book
        for i, book in enumerate(books):
            if book.get('id') == book_data['id']:
                books[i] = book_data
                break
    else:
        # Add a new book with a unique ID
        book_data['id'] = str(uuid.uuid4())
        book_data['date_added'] = datetime.now().strftime('%Y-%m-%d')
        books.append(book_data)
    
    save_books(books, user_id)
    return book_data

def delete_book(book_id, user_id=None):
    """
    Delete a book by its ID
    
    Args:
        book_id (str): Book ID
        user_id (str, optional): User ID. If None, the current user ID from session state is used.
    """
    books = load_books(user_id)
    books = [book for book in books if book.get('id') != book_id]
    save_books(books, user_id)

def get_book_by_id(book_id, user_id=None):
    """
    Get a book by its ID
    
    Args:
        book_id (str): Book ID
        user_id (str, optional): User ID. If None, the current user ID from session state is used.
        
    Returns:
        dict or None: Book dictionary if found, None otherwise
    """
    books = load_books(user_id)
    for book in books:
        if book.get('id') == book_id:
            return book
    return None

def get_books_by_status(status, user_id=None):
    """
    Get books by their reading status
    
    Args:
        status (str): Reading status
        user_id (str, optional): User ID. If None, the current user ID from session state is used.
        
    Returns:
        list: List of book dictionaries
    """
    books = load_books(user_id)
    return [book for book in books if book.get('status') == status]

def get_book_status_counts(books):
    """Get count of books by reading status"""
    status_counts = {}
    for book in books:
        status = book.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    return status_counts

def get_genre_counts(books):
    """Get count of books by genre"""
    genre_counts = {}
    for book in books:
        genre = book.get('genre', 'Unknown')
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    return genre_counts

def get_year_counts(books):
    """Get count of books by publication year"""
    year_counts = {}
    for book in books:
        year = book.get('year', 'Unknown')
        if year and year != 'Unknown':
            year = str(year)
            year_counts[year] = year_counts.get(year, 0) + 1
    return year_counts

def get_reading_progress(books):
    """Calculate reading progress statistics"""
    total = len(books)
    if total == 0:
        return {'read_percentage': 0, 'reading_percentage': 0, 'to_read_percentage': 0}
    
    read = len([book for book in books if book.get('status') == 'Read'])
    reading = len([book for book in books if book.get('status') == 'Reading'])
    to_read = len([book for book in books if book.get('status') == 'To Read'])
    
    return {
        'read_percentage': (read / total) * 100,
        'reading_percentage': (reading / total) * 100,
        'to_read_percentage': (to_read / total) * 100
    }
