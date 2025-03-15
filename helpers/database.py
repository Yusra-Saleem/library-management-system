import streamlit as st
from pymongo import MongoClient
import certifi
from datetime import datetime

def get_database():
    """
    Connect to MongoDB and return the database object.
    """
    try:
        MONGODB_URI = st.secrets["MONGODB"]["MONGODB_URL"]
        client = MongoClient(
            MONGODB_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            retryWrites=True,
            w="majority"
        )
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
        return client.library_database
    except Exception as e:
        st.error(f"❌ Database connection error: {str(e)}")
        return None

def init_db():
    """
    Initialize the database and collections if they don't exist.
    """
    try:
        db = get_database()
        if db is not None:
            if 'books' not in db.list_collection_names():
                db.create_collection('books')
                print("✅ Created 'books' collection.")
            else:
                print("✅ 'books' collection already exists.")
            return True
        return False
    except Exception as e:
        st.error(f"❌ Error initializing database: {str(e)}")
        return False

def add_book(book_data):
    """
    Save a new book to the database.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books
            if 'id' not in book_data:
                book_data['id'] = str(datetime.now().timestamp())
            book_data['date_added'] = datetime.now().strftime('%Y-%m-%d')
            result = books_collection.insert_one(book_data)
            if result.inserted_id:
                print(f"✅ Book inserted with ID: {result.inserted_id}")
                return True
        return False
    except Exception as e:
        st.error(f"❌ Error saving book: {str(e)}")
        return False

def get_all_books():
    """
    Fetch all books from the database.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books
            books = list(books_collection.find({}, {'_id': 0}))
            print(f"📚 Fetched {len(books)} books from the database")
            return books
        return []
    except Exception as e:
        st.error(f"❌ Error loading books: {str(e)}")
        return []

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
                print(f"✅ Book deleted with ID: {book_id}")
                return True
        return False
    except Exception as e:
        st.error(f"❌ Error deleting book: {str(e)}")
        return False

def update_book(book_id, updated_data):
    """
    Update an existing book in the database.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books
            result = books_collection.update_one(
                {"id": book_id},
                {"$set": updated_data}
            )
            if result.modified_count > 0:
                print(f"✅ Book updated with ID: {book_id}")
                return True
        return False
    except Exception as e:
        st.error(f"❌ Error updating book: {str(e)}")
        return False

def get_book_by_id(book_id):
    """
    Get a book by its ID from the database.
    """
    try:
        db = get_database()
        if db is not None:
            books_collection = db.books
            book = books_collection.find_one({"id": book_id}, {'_id': 0})
            return book
        return None
    except Exception as e:
        st.error(f"❌ Error getting book: {str(e)}")
        return None
