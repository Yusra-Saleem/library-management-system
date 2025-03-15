import pandas as pd
import json
import streamlit as st
import io
import uuid
from datetime import datetime
from helpers.database import get_database

def export_to_csv(books):
    """
    Export books to CSV file
    
    Args:
        books (list): List of book dictionaries
        
    Returns:
        BytesIO: CSV file as bytes object
    """
    if not books:
        return None
    
    # Convert books to DataFrame
    df = pd.DataFrame(books)
    
    # Create CSV from DataFrame
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return csv_buffer

def export_to_json(books):
    """
    Export books to JSON file
    
    Args:
        books (list): List of book dictionaries
        
    Returns:
        BytesIO: JSON file as bytes object
    """
    if not books:
        return None
    
    # Create JSON from books list
    json_buffer = io.BytesIO()
    json_buffer.write(json.dumps(books, indent=4).encode())
    json_buffer.seek(0)
    
    return json_buffer

def import_from_csv(file):
    """
    Import books from CSV file
    
    Args:
        file: Uploaded CSV file
        
    Returns:
        tuple: (success boolean, message string, imported books list)
    """
    try:
        # Read CSV file
        df = pd.read_csv(file)
        
        # Convert DataFrame to list of dictionaries
        books = df.to_dict('records')
        
        # Validate the imported data
        required_fields = ['title', 'author']
        for book in books:
            # Check for required fields
            if not all(field in book for field in required_fields):
                return False, "CSV is missing required fields (title, author)", []
            
            # Add ID if missing
            if 'id' not in book or not book['id']:
                book['id'] = str(uuid.uuid4())
            
            # Add date_added if missing
            if 'date_added' not in book or not book['date_added']:
                book['date_added'] = datetime.now().strftime('%Y-%m-%d')
        
        return True, f"Successfully imported {len(books)} books", books
        
    except Exception as e:
        return False, f"Error importing CSV: {str(e)}", []

def import_from_json(file):
    """
    Import books from JSON file
    
    Args:
        file: Uploaded JSON file
        
    Returns:
        tuple: (success boolean, message string, imported books list)
    """
    try:
        # Read JSON file
        content = file.read().decode('utf-8')
        books = json.loads(content)
        
        # Validate the imported data
        if not isinstance(books, list):
            return False, "JSON does not contain a list of books", []
        
        # Check each book for required fields
        required_fields = ['title', 'author']
        for book in books:
            if not isinstance(book, dict):
                return False, "JSON contains invalid book entries", []
            
            # Check for required fields
            if not all(field in book for field in required_fields):
                return False, "JSON is missing required fields (title, author)", []
            
            # Add ID if missing
            if 'id' not in book or not book['id']:
                book['id'] = str(uuid.uuid4())
            
            # Add date_added if missing
            if 'date_added' not in book or not book['date_added']:
                book['date_added'] = datetime.now().strftime('%Y-%m-%d')
        
        return True, f"Successfully imported {len(books)} books", books
        
    except json.JSONDecodeError:
        return False, "Invalid JSON format", []
    except Exception as e:
        return False, f"Error importing JSON: {str(e)}", []

def merge_books(existing_books, imported_books, strategy='replace'):
    """
    Merge imported books with existing books
    
    Args:
        existing_books (list): Existing books
        imported_books (list): Imported books
        strategy (str): Merge strategy - 'replace', 'keep', or 'add'
        
    Returns:
        list: Merged books list
    """
    if strategy == 'replace':
        # Replace existing books with imported ones (based on ID)
        existing_ids = {book.get('id'): i for i, book in enumerate(existing_books)}
        result = existing_books.copy()
        
        for imported_book in imported_books:
            if imported_book.get('id') in existing_ids:
                # Replace existing book
                result[existing_ids[imported_book.get('id')]] = imported_book
            else:
                # Add new book
                result.append(imported_book)
                
        return result
        
    elif strategy == 'keep':
        # Keep existing books when there's a conflict
        existing_ids = {book.get('id') for book in existing_books}
        
        # Add only books that don't exist
        result = existing_books.copy()
        for imported_book in imported_books:
            if imported_book.get('id') not in existing_ids:
                result.append(imported_book)
                
        return result
        
    else:  # 'add' strategy
        # Add all imported books as new entries
        result = existing_books.copy()
        
        for imported_book in imported_books:
            # Generate new ID to avoid conflicts
            imported_book['id'] = str(uuid.uuid4())
            result.append(imported_book)
            
        return result
        
def save_books(books):
    """
    Save multiple books to the database.
    If a book already exists (based on ID), it will be updated.
    Otherwise, a new book will be added.
    
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
        
        # Save or update each book
        for book in books:
            # Check if the book already exists
            existing_book = books_collection.find_one({"id": book["id"]})
            
            if existing_book:
                # Update the existing book
                books_collection.replace_one({"id": book["id"]}, book)
                print(f"✅ Updated book with ID: {book['id']}")
            else:
                # Add a new book
                books_collection.insert_one(book)
                print(f"✅ Added new book with ID: {book['id']}")
        
        return True
    except Exception as e:
        st.error(f"❌ Error saving books: {str(e)}")
        return False
