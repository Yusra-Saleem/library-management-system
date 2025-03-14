import streamlit as st
from pymongo import MongoClient
import certifi  # Import certifi for SSL certificate handling
from datetime import datetime

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

def get_all_books():
    """
    Fetch all books from the database.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books
            books = list(books_collection.find({}, {'_id': 0}))
            print(f"📚 Fetched {len(books)} books from the database")  # Debug statement
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

def delete_book(book_id):
    """
    Delete a book from the database by its ID.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books
            result = books_collection.delete_one({"id": book_id})
            if result.deleted_count > 0:
                print(f"✅ Book deleted with ID: {book_id}")  # Debug statement
                return True
        return False
    except Exception as e:
        st.error(f"❌ Error deleting book: {str(e)}")
        return False
