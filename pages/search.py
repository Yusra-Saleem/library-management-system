import streamlit as st
import uuid
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.book_api import search_google_books
from helpers.book_data import save_book, load_books

def show_search_page():
    """Display the search page"""
    st.title("Book Search")
    
    tab1, tab2 = st.tabs(["Search My Library", "Search Google Books"])
    
    with tab1:
        show_library_search()
    
    with tab2:
        show_google_books_search()

def show_library_search():
    """Display search interface for user's library"""
    st.subheader("Search My Library")
    
    # Search and filter inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search by Title or Author", st.session_state.search_query)
        st.session_state.search_query = search_query
    
    with col2:
        genres = ['All'] + list(set([book.get('genre', 'Unknown') for book in st.session_state.books]))
        genre_filter = st.selectbox("Filter by Genre", genres, index=genres.index(st.session_state.filter_genre) if st.session_state.filter_genre in genres else 0)
        st.session_state.filter_genre = genre_filter
    
    with col3:
        statuses = ['All', 'Read', 'Reading', 'To Read', 'Wishlist']
        status_filter = st.selectbox("Filter by Status", statuses, index=statuses.index(st.session_state.filter_status) if st.session_state.filter_status in statuses else 0)
        st.session_state.filter_status = status_filter
    
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
        st.write(f"Found {len(filtered_books)} books matching your criteria:")
        
        # Sort options
        sort_options = {
            "Title (A-Z)": lambda x: x.get('title', '').lower(),
            "Title (Z-A)": lambda x: x.get('title', '').lower(), 
            "Author (A-Z)": lambda x: x.get('author', '').lower(),
            "Author (Z-A)": lambda x: x.get('author', '').lower(),
            "Newest First": lambda x: x.get('year', 0),
            "Oldest First": lambda x: x.get('year', 0),
            "Recently Added": lambda x: x.get('date_added', ''),
            "Rating (High to Low)": lambda x: x.get('rating', 0)
        }
        
        sort_by = st.selectbox("Sort by", list(sort_options.keys()))
        
        # Apply sorting
        sort_key = sort_options[sort_by]
        reverse = sort_by in ["Title (Z-A)", "Author (Z-A)", "Newest First", "Recently Added", "Rating (High to Low)"]
        filtered_books.sort(key=sort_key, reverse=reverse)
        
        # Display books in grid
        book_cols = st.columns(2)
        for i, book in enumerate(filtered_books):
            with book_cols[i % 2]:
                with st.container(border=True):
                    st.subheader(book.get('title', 'Untitled'))
                    st.write(f"**Author:** {book.get('author', 'Unknown')}")
                    st.write(f"**Genre:** {book.get('genre', 'Unknown')}")
                    st.write(f"**Year:** {book.get('year', 'Unknown')}")
                    st.write(f"**Status:** {book.get('status', 'Unknown')}")
                    
                    rating = book.get('rating')
                    if rating is not None and rating > 0:
                        st.write(f"**Rating:** {'⭐' * rating}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit 📝", key=f"search_edit_{i}", use_container_width=True):
                            st.session_state.edit_book_id = book.get('id')
                            st.session_state.current_page = 'edit_book'
                            st.rerun()
                    with col2:
                        if st.button(f"View Details", key=f"search_details_{i}", use_container_width=True):
                            with st.expander("Book Details", expanded=True):
                                # Display additional details
                                if book.get('description'):
                                    st.write("**Description:**")
                                    st.write(book.get('description'))
                                
                                if book.get('notes'):
                                    st.write("**Notes:**")
                                    st.write(book.get('notes'))
                                
                                if book.get('pages'):
                                    st.write(f"**Pages:** {book.get('pages')}")
                                
                                if book.get('date_added'):
                                    st.write(f"**Added to Library:** {book.get('date_added')}")
    else:
        st.info("No books match your search criteria. Try different filters or add more books to your library.")

def show_google_books_search():
    """Display Google Books search interface"""
    st.subheader("Search Google Books")
    
    # Search input
    query = st.text_input("Search by Title, Author, or ISBN")
    max_results = st.slider("Maximum Results", 3, 20, 10)
    
    if query:
        with st.spinner("Searching Google Books..."):
            books = search_google_books(query, max_results)
        
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
                        
                        if st.button("Add to Library", key=f"google_add_{i}"):
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
                            
                            # Option to go back to home
                            if st.button("Return to Home"):
                                st.session_state.current_page = 'home'
                                st.rerun()
        else:
            st.warning("No books found. Try another search term.")
