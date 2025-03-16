import json
import os
from datetime import datetime
import streamlit as st
from pymongo import MongoClient
import certifi  # Import certifi for SSL certificate handling

def get_database():
    """
    Connect to MongoDB and return the database object.
    """
    try:
        # Get MongoDB URI from secrets
        MONGODB_URI = st.secrets["MONGODB"]["MONGODB_URL"]
        
        # Create client with SSL/TLS configuration
        client = MongoClient(
            MONGODB_URI,
            tls=True,  # Enable TLS/SSL
            tlsCAFile=certifi.where(),  # Use certifi's CA bundle
            retryWrites=True,
            w="majority"
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")  # Debug statement
        
        # Return database
        return client.library_database
    except Exception as e:
        st.error(f"❌ Database connection error: {str(e)}")
        return None

def load_books():
    """
    Fetch all books from the database.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books
            books = list(books_collection.find({}, {'_id': 0}))
            print(f"📚 Loaded {len(books)} books from the database")  # Debug statement
            return books
        return []
    except Exception as e:
        st.error(f"❌ Error loading books: {str(e)}")
        return []

def save_book(book_data):
    """
    Save a new book to the database.
    """
    try:
        db = get_database()
        if db is not None:  # Proper None check
            books_collection = db.books
            # Add unique identifier if not present
            if 'id' not in book_data:
                book_data['id'] = str(datetime.now().timestamp())
            # Add timestamp
            book_data['date_added'] = datetime.now().strftime('%Y-%m-%d')
            # Insert the book
            result = books_collection.insert_one(book_data)
            # Check if insertion was successful
            if result.inserted_id:
                print(f"✅ Book inserted with ID: {result.inserted_id}")  # Debug statement
                return True
        return False
    except Exception as e:
        st.error(f"❌ Error saving book: {str(e)}")
        return False

def get_book_status_counts(books):
    """
    Get counts of books by status.
    """
    status_counts = {}
    for book in books:
        status = book.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    return status_counts

def search_local_books(query):
    """
    Search for books in the local database.
    """
    try:
        db = get_database()
        if db and query:
            books_collection = db.books
            search_query = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"author": {"$regex": query, "$options": "i"}},
                    {"genre": {"$regex": query, "$options": "i"}}
                ]
            }
            books = list(books_collection.find(search_query, {'_id': 0}))
            return books
        return []
    except Exception as e:
        st.error(f"❌ Error searching books: {str(e)}")
        return []

def get_all_books():
    """
    Fetch all books from the database.
    """
    return load_books()

def add_book(book_data):
    """
    Save a new book to the database.
    """
    return save_book(book_data)

def get_genre_counts(books):
    """
    Get counts of books by genre.
    """
    genre_counts = {}
    for book in books:
        genre = book.get('genre', 'Unknown')
        if genre and genre != 'Unknown':
            # Handle multiple genres separated by commas
            for g in genre.split(', '):
                genre_counts[g] = genre_counts.get(g, 0) + 1
    return genre_counts

def get_year_counts(books):
    """
    Get counts of books by publication year.
    """
    year_counts = {}
    for book in books:
        year = book.get('year', 'Unknown')
        if year and year != 'Unknown':
            try:
                # Convert to string in case it's a number
                year = str(year)
                year_counts[year] = year_counts.get(year, 0) + 1
            except Exception:
                continue
    return year_counts

def get_book_by_id(book_id):
    """
    Get a book by its ID from the database.
    """
    try:
        db = get_database()
        if db is not None:  # Explicitly check if database is not None
            books_collection = db.books
            book = books_collection.find_one({"id": book_id}, {'_id': 0})
            if book is not None:  # Explicitly check if book is not None
                return book
            else:
                print(f"❌ Book with ID {book_id} not found in the database.")
                return None
        else:
            print("❌ Database connection failed.")
            return None
    except Exception as e:
        st.error(f"❌ Error getting book: {str(e)}")
        return None

def update_book(book_id, updated_data):
    """
    Update an existing book in the database.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books

            # Update the book with the given ID
            result = books_collection.update_one(
                {"id": book_id},  # Find the book by its ID
                {"$set": updated_data}  # Update the fields with new data
            )

            if result.modified_count > 0:
                print(f"✅ Book updated with ID: {book_id}")
                return True
            else:
                print("❌ No changes made to the book.")
                return False
        else:
            print("❌ Database connection failed.")
            return False
    except Exception as e:
        st.error(f"❌ Error updating book: {str(e)}")
        return False
        


def save_books(books):
    """
    Save multiple books to the database.
    
    Args:
        books (list): List of books to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_database()
        if db is None:  # Explicitly check if database is None
            print("❌ Database connection failed.")
            return False
        
        books_collection = db.books
        
        # Insert all books
        if books:
            result = books_collection.insert_many(books)
            if result.inserted_ids:  # Directly check inserted_ids
                print(f"✅ Successfully saved {len(result.inserted_ids)} books.")
                return True
            else:
                print("❌ Failed to save books.")
                return False
        else:
            print("❌ No books to save.")
            return False
    except Exception as e:
        st.error(f"❌ Error saving books: {str(e)}")
        return False

def update_book_status(book_id, new_status):
    """
    Update the status of a book in the database.
    
    Args:
        book_id (str): ID of the book to update
        new_status (str): New status to set ('To Read', 'Reading', 'Read')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_database()
        if db is None:  # Explicitly check if database is None
            print("❌ Database connection failed.")
            return False
        
        books_collection = db.books
        result = books_collection.update_one(
            {"id": book_id},
            {"$set": {"status": new_status}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated book status for ID: {book_id}")
            return True
        else:
            print("❌ No changes made to the book.")
            return False
    except Exception as e:
        st.error(f"❌ Error updating book status: {str(e)}")
        return False

def get_book_status_counts(books):
    """Get counts of books by status"""
    status_counts = {}
    for book in books:
        status = book.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    return status_counts
