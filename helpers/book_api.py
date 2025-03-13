import os
import requests
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Books API endpoint
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def search_google_books(query, max_results=10):
    """
    Search for books using the Google Books API
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 10)
    """
    try:
        api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
        base_url = "https://www.googleapis.com/books/v1/volumes"
        
        # Add API key to parameters
        params = {
            'q': query,
            'key': api_key,
            'maxResults': max_results
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        if 'items' not in data:
            return []
            
        books = []
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            book = {
                'title': volume_info.get('title', 'Unknown Title'),
                'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                'year': volume_info.get('publishedDate', 'Unknown')[:4],
                'genre': ', '.join(volume_info.get('categories', ['Unknown'])),
                'description': volume_info.get('description', 'No description available'),
                'cover_image': volume_info.get('imageLinks', {}).get('thumbnail', None)
            }
            books.append(book)
            
        return books
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching book data: {e}")
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
        response = requests.get(f"{GOOGLE_BOOKS_API_URL}/{google_id}")
        
        if response.status_code != 200:
            st.error(f"Error fetching book details: {response.status_code}")
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
