import os
import requests
import streamlit as st

# Google Books API endpoint
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def search_google_books(query, max_results=10):
    """
    Search for books using the Google Books API
    """
    try:
        # Try to get API key from Streamlit secrets
        api_key = st.secrets.get("GOOGLE_BOOKS_API_KEY")
        
        # Check if API key is available
        if not api_key:
            st.error("API key not configured. Please add the API key in Streamlit Secrets.")
            return []
            
        # Validate the query
        if not query or len(query.strip()) == 0:
            st.warning("Please enter a search term")
            return []
            
        # Prepare API request parameters
        params = {
            'q': query,
            'key': api_key,
            'maxResults': max_results
        }
        
        # Make the request to Google Books API
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        
        # Check response status
        if response.status_code == 403:
            st.error("API access denied. Please check your API key configuration.")
            return []
        elif response.status_code != 200:
            st.error(f"Server returned status code: {response.status_code}")
            return []
            
        # Parse the response
        data = response.json()
        
        # Check if any results were found
        total_items = data.get('totalItems', 0)
        if total_items == 0:
            st.info(f"No books found for '{query}'")
            return []
            
        if 'items' not in data:
            st.warning("Search returned no results")
            return []
            
        # Extract book details
        books = []
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            book = {
                'title': volume_info.get('title', 'Unknown Title'),
                'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                'year': volume_info.get('publishedDate', 'Unknown')[:4] if volume_info.get('publishedDate') else 'Unknown',
                'genre': ', '.join(volume_info.get('categories', ['Unknown'])),
                'description': volume_info.get('description', 'No description available'),
                'cover_image': volume_info.get('imageLinks', {}).get('thumbnail', None),
                'google_id': item.get('id')  # Store Google Books ID for detailed info
            }
            books.append(book)
        
        if not books:
            st.warning("No valid books found in the response")
        
        return books
        
    except requests.exceptions.ConnectionError:
        st.error("Connection error. Please check your internet connection.")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
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
        # Make a request to fetch book details
        response = requests.get(f"{GOOGLE_BOOKS_API_URL}/{google_id}")
        
        if response.status_code != 200:
            st.error(f"Error fetching book details: {response.status_code}")
            return {}
        
        # Parse the response
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

# Streamlit App UI
st.title("Google Books Search")

# Search bar
query = st.text_input("Enter a book title, author, or keyword:")

# Search button
if st.button("Search"):
    if query:
        with st.spinner("Searching for books..."):
            books = search_google_books(query)
            if books:
                st.success(f"Found {len(books)} results!")
                for book in books:
                    st.subheader(book['title'])
                    st.write(f"**Author:** {book['author']}")
                    st.write(f"**Year:** {book['year']}")
                    st.write(f"**Genre:** {book['genre']}")
                    st.write(f"**Description:** {book['description']}")
                    if book['cover_image']:
                        st.image(book['cover_image'], caption=book['title'], width=150)
                    
                    # Button to view more details
                    if st.button(f"View Details for {book['title']}", key=book['google_id']):
                        book_details = get_book_details(book['google_id'])
                        if book_details:
                            st.subheader("Detailed Information")
                            st.write(f"**Publisher:** {book_details['publisher']}")
                            st.write(f"**Page Count:** {book_details['page_count']}")
                            st.write(f"**ISBN:** {book_details['isbn']}")
                            st.write(f"**Google Books ID:** {book_details['google_id']}")
                    st.write("---")
    else:
        st.warning("Please enter a search term.")