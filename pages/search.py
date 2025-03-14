import streamlit as st
import uuid
from datetime import datetime
import sys
import os
import requests

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.book_api import search_books
from helpers.database import add_book, get_all_books

def search_books(query, max_results=10):
    """Search books using Open Library API"""
    try:
        # Parameters for Open Library API
        params = {
            'q': query,
            'limit': max_results,
            'fields': 'title,author_name,first_publish_year,subject,cover_i'
        }
        
        # Make the request
        response = requests.get("https://openlibrary.org/search.json", params=params)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        if 'docs' not in data or not data['docs']:
            return []
        
        books = []
        for doc in data['docs']:
            book = {
                'title': doc.get('title', 'Unknown Title'),
                'author': ', '.join(doc.get('author_name', ['Unknown Author'])),
                'year': str(doc.get('first_publish_year', 'Unknown')),
                'genre': ', '.join(doc.get('subject', ['Unknown'])[:3]),
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

def show_search_page():
    """Display the search page"""
    st.title("Book Search")
    
    tab1, tab2 = st.tabs(["Search My Library", "Search Open Library"])
    
    with tab1:
        show_library_search()
    
    with tab2:
        show_open_library_search()

def show_library_search():
    """Display search interface for user's library"""
    st.subheader("Search My Library")
    
    # Search form with button
    with st.form("library_search_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("Search by Title or Author", st.session_state.get('search_query', ''))
        
        with col2:
            genres = ['All'] + list(set([book.get('genre', 'Unknown') for book in st.session_state.books]))
            genre_filter = st.selectbox("Filter by Genre", genres)
        
        with col3:
            statuses = ['All', 'Read', 'Reading', 'To Read', 'Wishlist']
            status_filter = st.selectbox("Filter by Status", statuses)
        
        search_submitted = st.form_submit_button("🔍 Search")
    
    if search_submitted:
        # Apply search and filters
        filtered_books = st.session_state.books
        
        if search_query:
            filtered_books = [book for book in filtered_books if 
                            search_query.lower() in book.get('title', '').lower() or 
                            search_query.lower() in book.get('author', '').lower()]
        
        if genre_filter != 'All':
            filtered_books = [book for book in filtered_books if book.get('genre', 'Unknown') == genre_filter]
        
        if status_filter != 'All':
            filtered_books = [book for book in filtered_books if book.get('status', 'Unknown') == status_filter]
        
        # Display results
        if filtered_books:
            st.success(f"Found {len(filtered_books)} books matching your criteria")
            
            for book in filtered_books:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(book.get('title', 'Untitled'))
                        st.write(f"**Author:** {book.get('author', 'Unknown')}")
                        st.write(f"**Genre:** {book.get('genre', 'Unknown')}")
                        st.write(f"**Year:** {book.get('year', 'Unknown')}")
                        st.write(f"**Status:** {book.get('status', 'Unknown')}")
                    with col2:
                        if book.get('cover_image'):
                            st.image(book['cover_image'], width=150)
        else:
            st.info("No books match your search criteria.")

def show_open_library_search():
    """Display Open Library search interface"""
    st.subheader("Search Open Library")
    
    # Search form with button
    with st.form("open_library_search"):
        search_query = st.text_input("Enter book title, author, or ISBN")
        max_results = st.slider("Maximum Results", 5, 20, 10)
        search_submitted = st.form_submit_button("🔍 Search")
    
    if search_submitted and search_query:
        with st.spinner('🔍 Searching for books...'):
            books = search_books(search_query, max_results)
            
            if books:
                st.success(f"Found {len(books)} books")
                
                for idx, book in enumerate(books):
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(book['title'])
                            st.write(f"**Author:** {book['author']}")
                            st.write(f"**Year:** {book['year']}")
                            st.write(f"**Genre:** {book['genre']}")
                            if book.get('description'):
                                with st.expander("Description"):
                                    st.write(book['description'])
                        with col2:
                            if book.get('cover_image'):
                                st.image(book['cover_image'], width=150)
                            button_key = f"add_{idx}_{book['title'][:30]}"
                            if st.button("Add to Library", key=button_key, type="primary"):
                                with st.spinner('Adding book to library...'):
                                    book_id = add_book(book)
                                    if book_id:
                                        st.success(f"Book '{book['title']}' added to library!")
                                        st.rerun()
                                    else:
                                        st.error("Error adding book")
            else:
                st.info("No books found. Try different search terms.")
    elif search_submitted:
        st.warning("Please enter a search term")
