import streamlit as st
import uuid
from datetime import datetime
import sys
import os
from helpers.database import add_book
from helpers.book_api import search_books, get_book_details
import time
from helpers.book_data import save_book, load_books

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def show_add_book_page():
    """Display the add book page"""
    st.title("Add Books")
    
    # Create tabs for different add methods
    tab1, tab2 = st.tabs(["📝 Manual Entry", "🔍 Search & Add"])
    
    with tab1:
        show_manual_entry_form()
    
    with tab2:
        show_search_form()

def show_search_form():
    st.markdown("""
        <style>
        .search-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .book-card {
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin-bottom: 15px;
        }
        .add-button {
            width: 100%;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Search bar and button in a container
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        search_query = st.text_input("🔍", placeholder="Search by title, author, or ISBN", label_visibility="collapsed")
    with search_col2:
        search_clicked = st.button("Search", type="primary", use_container_width=True)
    
    if search_clicked and search_query:
        with st.spinner("🔍 Searching for books..."):
            try:
                results = search_books(search_query)
                
                if results:
                    st.success(f"Found {len(results)} books")
                    for i, book in enumerate(results):
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"### {book['title']}")
                                st.markdown(f"**Author:** {book['author']}")
                                if 'year' in book:
                                    st.markdown(f"**Year:** {book['year']}")
                                if 'genre' in book:
                                    st.markdown(f"**Genre:** {book['genre']}")
                                if 'description' in book:
                                    with st.expander("Description"):
                                        st.write(book['description'])
                            
                            with col2:
                                if book.get('cover_image'):
                                    st.image(book['cover_image'], width=100)
                                st.button("📚 Add to Library", 
                                        key=f"add_{i}", 
                                        type="primary",
                                        use_container_width=True,
                                        on_click=lambda b=book: add_book_from_search(b))
                else:
                    st.info("No books found. Try a different search term.")
            except Exception as e:
                st.error(f"Error searching books: {str(e)}")
    elif search_clicked:
        st.warning("Please enter a search term")

def show_manual_entry_form():
    """Display form for manual book entry"""
    st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            margin-top: 10px;
        }
        .stForm > div {
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.form("add_book_form", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
        title = st.text_input("Title*", placeholder="Enter book title")
        author = st.text_input("Author*", placeholder="Enter author name")
        year = st.text_input("Year", placeholder="Publication year")
        genre = st.text_input("Genre", placeholder="Book genre(s)")
        
        with col2:
        description = st.text_area("Description", placeholder="Book description")
        cover_image = st.text_input("Cover Image URL", placeholder="URL to book cover image")
        status = st.selectbox("Reading Status", ["To Read", "Reading", "Read"])
        rating = st.slider("Rating", 0, 5, 0)
        
        # Center the submit button and make it prominent
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("📚 Add Book", use_container_width=True, type="primary")
        
        if submitted:
            if not title or not author:
                st.error("Title and Author are required!")
                return
            
            book_data = {
                'title': title,
                'author': author,
                'year': year,
                'genre': genre,
                'description': description,
                'cover_image': cover_image,
                'status': status,
                'rating': rating,
                'date_added': datetime.now().strftime('%Y-%m-%d')
            }
            
            if save_book(book_data):
                st.success(f"Added '{title}' to your library!")
                st.session_state.books = load_books()
                st.experimental_rerun()
            else:
                st.error("Failed to add book to library")

def show_google_books_search():
    """Display Google Books search interface"""
    query = st.text_input("Search for books", key="google_search")
    
    if query:
        with st.spinner("Searching..."):
            books = search_books(query)
        
        if books:
            st.write(f"Found {len(books)} results:")
            
            # Display search results in cards
            for i, book in enumerate(books):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(book['title'])
                        st.write(f"**Author:** {book['author']}")
                        st.write(f"**Year:** {book['year']}")
                        st.write(f"**Genre:** {book['genre']}")
                        
                        if book.get('description'):
                            with st.expander("Description"):
                                st.write(book['description'][:300] + "..." if len(book['description']) > 300 else book['description'])
                    
                    with col2:
                        if book.get('thumbnail'):
                            st.image(book['thumbnail'], width=100)
                        
                        if st.button("Add to Library", key=f"add_google_{i}"):
                            # Get detailed book info
                            if book.get('google_id'):
                                detailed_book = get_book_details(book['google_id'])
                                if detailed_book:
                                    book.update(detailed_book)
                            
                            # Create book dictionary
                            new_book = {
                                "id": str(uuid.uuid4()),
                                "title": book['title'],
                                "author": book['author'],
                                "year": book['year'],
                                "genre": book['genre'],
                                "status": "To Read",
                                "rating": 0,
                                "pages": book.get('page_count', 0),
                                "description": book.get('description', ''),
                                "date_added": datetime.now().strftime('%Y-%m-%d')
                            }
                            
                            # Save book
                            save_book(new_book)
                            
                            # Update session state
                            st.session_state.books = load_books()
                            
                            # Show success message
                            st.success(f"Added '{book['title']}' to your library!")
                            
                            # Go back to home
                            st.session_state.current_page = 'home'
                            st.rerun()
        else:
            st.warning("No books found. Try another search term.")
def add_book_from_search(book):
    with st.spinner("Adding to library..."):
        book_data = {
            'title': book['title'],
            'author': book['author'],
            'year': book.get('year', 'Unknown'),
            'genre': book.get('genre', ''),
            'description': book.get('description', ''),
            'cover_image': book.get('cover_image', ''),
            'status': 'To Read',
            'rating': 0,
            'date_added': datetime.now().strftime('%Y-%m-%d')
        }
        
        if save_book(book_data):
            st.success(f"Added '{book['title']}' to your library!")
            st.session_state.books = load_books()
        else:
            st.error("Failed to add book to library")

