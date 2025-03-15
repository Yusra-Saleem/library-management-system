import requests
import streamlit as st
from helpers.database import add_book, get_all_books, search_local_books, init_db

# Open Library API endpoint
OPEN_LIBRARY_API_URL = "https://openlibrary.org/search.json"

# Initialize database
init_db()

def search_books(query, max_results=10):
    """
    Search for books using the Open Library API.
    """
    try:
        # Clean and validate the query
        if not query or len(query.strip()) == 0:
            st.warning("Please enter a search query.")
            return []
        
        # Parameters for Open Library API
        params = {
            'q': query,
            'limit': max_results,
            'fields': 'title,author_name,first_publish_year,subject,cover_i'
        }
        
        # Make the request
        response = requests.get(OPEN_LIBRARY_API_URL, params=params)
        
        # Check response status
        if response.status_code != 200:
            st.error(f"Error fetching data from Open Library: {response.status_code}")
            return []
        
        data = response.json()
        
        # Check if we got any results
        if 'docs' not in data or not data['docs']:
            st.info("No books found. Try a different search term.")
            return []
        
        books = []
        for doc in data['docs']:
            book = {
                'title': doc.get('title', 'Unknown Title'),
                'author': ', '.join(doc.get('author_name', ['Unknown Author'])),
                'year': str(doc.get('first_publish_year', 'Unknown')),
                'genre': ', '.join(doc.get('subject', ['Unknown'])[:3]),  # Get first 3 subjects
                'description': 'Available on Open Library',
                'cover_image': f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg" if doc.get('cover_i') else None,
                'status': 'To Read',
                'rating': 0
            }
            books.append(book)
        
        return books
        
    except Exception as e:
        st.error(f"Error searching books: {str(e)}")
        return []

def get_book_details(book_id):
    """
    Get detailed information about a specific book from Open Library.
    """
    try:
        response = requests.get(f"https://openlibrary.org/works/{book_id}.json")
        
        if response.status_code != 200:
            st.error(f"Error fetching book details: {response.status_code}")
            return {}
        
        data = response.json()
        
        book_details = {
            'title': data.get('title', 'Unknown Title'),
            'author': data.get('authors', [{'name': 'Unknown Author'}])[0].get('name'),
            'year': data.get('first_publish_date', 'Unknown')[:4],
            'genre': ', '.join(data.get('subjects', ['Unknown'])[:3]),
            'description': data.get('description', {}).get('value', 'No description available'),
            'cover_image': f"https://covers.openlibrary.org/b/id/{data.get('covers', [None])[0]}-L.jpg" if data.get('covers') else None
        }
        
        return book_details
        
    except Exception as e:
        st.error(f"Error fetching book details: {str(e)}")
        return {}

def save_book_to_library(book_data):
    """Save a book to local database."""
    try:
        return add_book(book_data)
    except Exception as e:
        st.error(f"Error saving book to library: {str(e)}")
        return False

def get_library_books():
    """Get all books from local library."""
    try:
        return get_all_books()
    except Exception as e:
        st.error(f"Error fetching library books: {str(e)}")
        return []

def search_library(query):
    """Search books in local library."""
    try:
        return search_local_books(query)
    except Exception as e:
        st.error(f"Error searching library: {str(e)}")
        return []
