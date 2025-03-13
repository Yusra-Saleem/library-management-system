import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Books API endpoint
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# API Key (not recommended for production)
API_KEY = "AIzaSyBmi5kJxULV8VJqdYNqvf6ZcDptVQ_82VY"

def search_google_books(query, max_results=10):
    """
    Search for books using the Google Books API
    """
    try:
        # Clean and validate the query
        if not query or len(query.strip()) == 0:
            return []
        
        # Add API key to parameters
        params = {
            'q': query,
            'key': API_KEY,
            'maxResults': max_results
        }
        
        # Make the request
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        
        # Check response status
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        # Check if we got any results
        if 'items' not in data:
            return []
        
        books = []
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            book = {
                'title': volume_info.get('title', 'Unknown Title'),
                'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                'year': volume_info.get('publishedDate', 'Unknown')[:4] if volume_info.get('publishedDate') else 'Unknown',
                'genre': ', '.join(volume_info.get('categories', ['Unknown'])),
                'description': volume_info.get('description', 'No description available'),
                'cover_image': volume_info.get('imageLinks', {}).get('thumbnail', None)
            }
            books.append(book)
        
        return books
        
    except:
        return []

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
            'key': API_KEY
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
        
    except:
        return {}