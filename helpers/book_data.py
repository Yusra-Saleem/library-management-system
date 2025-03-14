import json
import os
from datetime import datetime
import streamlit as st
from pymongo import MongoClient

# MongoDB Atlas connection (Free tier)
MONGODB_URI = st.secrets["MONGODB"]["MONGODB_URL"]

def get_database():
    try:
        client = MongoClient(MONGODB_URI)
        return client.library_database
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def load_books():
    try:
        db = get_database()
        if db:
            books_collection = db.books
            books = list(books_collection.find({}, {'_id': 0}))
            return books
        return []
    except Exception as e:
        st.error(f"Error loading books: {str(e)}")
        return []

def save_book(book_data):
    try:
        db = get_database()
        if db:
            books_collection = db.books
            # Add timestamp
            book_data['date_added'] = datetime.now().strftime('%Y-%m-%d')
            result = books_collection.insert_one(book_data)
            return True
        return False
    except Exception as e:
        st.error(f"Error saving book: {str(e)}")
        return False

def get_book_status_counts(books):
    """Get counts of books by status"""
    status_counts = {}
    for book in books:
        status = book.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    return status_counts

def search_local_books(query):
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
        st.error(f"Error searching books: {str(e)}")
        return []

def get_all_books():
    return load_books()

def add_book(book_data):
    return save_book(book_data)

def get_genre_counts(books):
    """Get counts of books by genre"""
    genre_counts = {}
    for book in books:
        genre = book.get('genre', 'Unknown')
        if genre and genre != 'Unknown':
            # Handle multiple genres separated by commas
            for g in genre.split(', '):
                genre_counts[g] = genre_counts.get(g, 0) + 1
    return genre_counts

def get_year_counts(books):
    """Get counts of books by publication year"""
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
    """Get a book by its ID from the database"""
    try:
        db = get_database()
        if db:
            books_collection = db.books
            book = books_collection.find_one({"id": book_id}, {'_id': 0})
            return book
        return None
    except Exception as e:
        st.error(f"Error getting book: {str(e)}")
        return None

def save_books(books):
    """Save multiple books to the database"""
    try:
        db = get_database()
        if db:
            books_collection = db.books
            # Clear existing books
            books_collection.delete_many({})
            # Insert all books
            if books:
                books_collection.insert_many(books)
            return True
        return False
    except Exception as e:
        st.error(f"Error saving books: {str(e)}")
        return False
