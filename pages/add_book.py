import streamlit as st
import uuid
from datetime import datetime
import sys
import os
from helpers.database import add_book
from helpers.book_api import search_books, get_book_details
import time

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.book_data import save_book, load_books

def show_add_book_page():
    """Display the add book page"""
    st.title("Add New Book")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📝 Manual Entry", "🔍 Search & Add"])
    
    # Tab 1: Manual Entry
    with tab1:
        with st.form("add_book_form"):
            title = st.text_input("Title*")
            author = st.text_input("Author*")
            year = st.text_input("Year")
            genre = st.text_input("Genre")
            description = st.text_area("Description")
            cover_image = st.text_input("Cover Image URL")
            
            status = st.selectbox("Reading Status", 
                ["To Read", "Reading", "Read", "Wishlist"]
            )
            
            rating = st.slider("Rating", 0, 5, 0)
            
            submitted = st.form_submit_button("Add Book")
            
            if submitted and title and author:
                book_data = {
                    'title': title,
                    'author': author,
                    'year': year,
                    'genre': genre,
                    'description': description,
                    'cover_image': cover_image,
                    'status': status,
                    'rating': rating
                }
                
                book_id = add_book(book_data)
                if book_id:
                    st.success(f"Book '{title}' added successfully!")
                    st.rerun()
                else:
                    st.error("Error adding book")
            elif submitted:
                st.error("Title and Author are required!")

    # Tab 2: Search & Add
    with tab2:
        # Search form
        with st.form("search_form"):
            search_query = st.text_input("Enter book title, author, or ISBN")
            search_submitted = st.form_submit_button("🔍 Search")
            
        if search_submitted and search_query:
            # Add loading spinner and message
            with st.spinner('🔍 Searching for books...'):
                # Create a placeholder for results
                results_placeholder = st.empty()
                
                # Perform search
                books = search_books(search_query)
                
                if books:
                    # Clear the placeholder and show results
                    results_placeholder.empty()
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
                                    st.write(f"**Description:** {book['description']}")
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
                    # Show no results message
                    results_placeholder.info("No books found. Try different search terms.")
        elif search_submitted:
            st.warning("Please enter a search term")
        else:
            st.info("Enter a book title, author, or ISBN and click Search to find books")

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
