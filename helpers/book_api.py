import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Books API endpoint
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# Add this debug code temporarily
try:
    api_key = st.secrets["GOOGLE"]["GOOGLE_BOOKS_API_KEY"]
    st.write("API Key loaded successfully:", api_key[:10] + "...")  # Shows first 10 chars
except Exception as e:
    st.error(f"Error loading API key: {str(e)}")

# Open Library API endpoint
OPEN_LIBRARY_API_URL = "https://openlibrary.org/search.json"

def search_google_books(query, max_results=10):
    """
    Search for books using the Open Library API
    """
    try:
        # Clean and validate the query
        if not query or len(query.strip()) == 0:
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
            return []
        
        data = response.json()
        
        # Check if we got any results
        if 'docs' not in data or not data['docs']:
            return []
        
        books = []
        for doc in data['docs']:
            book = {
                'title': doc.get('title', 'Unknown Title'),
                'author': ', '.join(doc.get('author_name', ['Unknown Author'])),
                'year': str(doc.get('first_publish_year', 'Unknown')),
                'genre': ', '.join(doc.get('subject', ['Unknown'])[:3]),  # Get first 3 subjects
                'description': 'Available on Open Library',
                'cover_image': f"https://covers.openlibrary.org/b/id/{doc.get('cover_i')}-M.jpg" if doc.get('cover_i') else None
            }
            books.append(book)
        
        return books
        
    except Exception as e:
        st.error(f"Error searching books: {str(e)}")
        return []

def get_book_details(book_id):
    """
    Get detailed information about a specific book from Open Library
    """
    try:
        response = requests.get(f"https://openlibrary.org/works/{book_id}.json")
        
        if response.status_code != 200:
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

def get_book_details(google_id):
    """
    Get detailed information about a specific book
    
    Args:
        google_id (str): Google Books ID
        
    Returns:
        dict: Book information dictionary
    """
    if not google_id:
        return {}
    
    try:
        params = {
            'key': api_key
        }
        
        response = requests.get(f"{GOOGLE_BOOKS_API_URL}/{google_id}", params=params)
        
        if response.status_code != 200:
            return {}
        
        data = response.json()
        volume_info = data.get('volumeInfo', {})
        
        # Extract detailed book information
        book_details = {
            'title': volume_info.get('title', 'Unknown Title'),
            'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
            'year': volume_info.get('publishedDate', 'Unknown')[:4] if volume_info.get('publishedDate') else 'Unknown',
            'genre': ', '.join(volume_info.get('categories', ['Unknown'])) if volume_info.get('categories') else 'Unknown',
            'description': volume_info.get('description', ''),
            'page_count': volume_info.get('pageCount', 0),
            'isbn': next((id_info.get('identifier', '') for id_info in volume_info.get('industryIdentifiers', []) 
                          if id_info.get('type') == 'ISBN_13'), ''),
            'publisher': volume_info.get('publisher', 'Unknown'),
            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
            'google_id': google_id
        }
        
        return book_details
        
    except Exception as e:
        st.error(f"Error fetching book details: {str(e)}")
        return {}

def search_books(query, max_results=10):
    try:
        params = {
            'q': query,
            'limit': max_results
        }
        response = requests.get(OPEN_LIBRARY_API_URL, params=params)
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        books = []
        
        for doc in data.get('docs', [])[:max_results]:
            book = {
                'title': doc.get('title', 'Unknown Title'),
                'author': ', '.join(doc.get('author_name', ['Unknown Author'])),
                'year': str(doc.get('first_publish_year', 'Unknown')),
                'genre': ', '.join(doc.get('subject', ['Unknown'])),
                'description': doc.get('description', 'No description available'),
                'cover_image': f"https://covers.openlibrary.org/b/id/{doc.get('cover_i', '')}-M.jpg" if doc.get('cover_i') else None
            }
            books.append(book)
            
        return books
        
    except Exception as e:
        st.error(f"Error searching books: {str(e)}")
        return []

NYT_API_URL = "https://api.nytimes.com/svc/books/v3"
NYT_API_KEY = st.secrets["NYT"]["API_KEY"]  # You'll need to get this

def get_bestsellers():
    try:
        response = requests.get(
            f"{NYT_API_URL}/lists/current/hardcover-fiction.json",
            params={'api-key': NYT_API_KEY}
        )
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        books = []
        
        for book in data.get('results', {}).get('books', []):
            book_info = {
                'title': book.get('title'),
                'author': book.get('author'),
                'description': book.get('description'),
                'cover_image': book.get('book_image')
            }
            books.append(book_info)
            
        return books
        
    except Exception as e:
        st.error(f"Error fetching bestsellers: {str(e)}")
        return []
