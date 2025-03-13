import streamlit as st
import uuid
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.book_data import save_book, load_books
from helpers.book_api import search_google_books, get_book_details

def show_add_book_page():
    """Display the add book page"""
    st.title("Add New Book")
    
    # Create tabs for manual entry and Google Books search
    tab1, tab2 = st.tabs(["Manual Entry", "Search Google Books"])
    
    with tab1:
        show_manual_entry_form()
    
    with tab2:
        show_google_books_search()

def show_manual_entry_form():
    """Display form for manual book entry"""
    with st.form("add_book_form"):
        st.subheader("Book Details")
        
        # Book fields
        title = st.text_input("Title", key="manual_title")
        author = st.text_input("Author", key="manual_author")
        year = st.text_input("Publication Year", key="manual_year")
        genre = st.text_input("Genre", key="manual_genre", 
                             help="Enter genre (e.g., Fiction, Science Fiction, Biography)")
        
        # Reading status
        status_options = ["To Read", "Reading", "Read", "Wishlist"]
        status = st.selectbox("Reading Status", status_options, key="manual_status")
        
        # Additional fields
        col1, col2 = st.columns(2)
        with col1:
            rating = st.slider("Your Rating", 0, 5, 0, key="manual_rating")
        with col2:
            pages = st.number_input("Number of Pages", min_value=0, key="manual_pages")
        
        notes = st.text_area("Notes", key="manual_notes")
        
        # Submit button
        submitted = st.form_submit_button("Add Book", use_container_width=True)
        
        if submitted:
            if not title or not author:
                st.error("Title and author are required")
            else:
                # Create book dictionary
                new_book = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "author": author,
                    "year": year,
                    "genre": genre,
                    "status": status,
                    "rating": rating,
                    "pages": pages,
                    "notes": notes,
                    "date_added": datetime.now().strftime('%Y-%m-%d')
                }
                
                # Save book
                save_book(new_book)
                
                # Update session state
                st.session_state.books = load_books()
                
                # Show success message
                st.success(f"Added '{title}' to your library!")
                
                # Clear form fields
                for key in st.session_state:
                    if key.startswith("manual_"):
                        st.session_state[key] = ""
                if "manual_rating" in st.session_state:
                    st.session_state["manual_rating"] = 0
                if "manual_pages" in st.session_state:
                    st.session_state["manual_pages"] = 0
                
                # Go back to home
                st.session_state.current_page = 'home'
                st.rerun()

def show_google_books_search():
    """Display Google Books search interface"""
    query = st.text_input("Search for books", key="google_search")
    
    if query:
        with st.spinner("Searching..."):
            books = search_google_books(query)
        
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
