import streamlit as st
from datetime import datetime  # Import datetime module
from helpers.database import add_book, get_all_books
from helpers.book_api import search_books

def show_add_book_page():
    """Display the add book page"""
    st.title("Add Books")
    
    # Create tabs for different add methods
    tab1, tab2 = st.tabs(["📝 Manual Entry", "🔍 Search & Add"])
    
    with tab1:
        show_manual_entry_form()
    
    with tab2:
        show_search_form()

def show_manual_entry_form():
    """Display form for manual book entry"""
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
        
        submitted = st.form_submit_button("📚 Add Book", type="primary", use_container_width=True)
        
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
                'date_added': datetime.now().strftime('%Y-%m-%d')  # Use datetime module
            }
            
            if add_book(book_data):
                st.success(f"Added '{title}' to your library!")
                st.session_state.books = get_all_books()  # Refresh the book list
                st.rerun()  # Refresh the page
            else:
                st.error("Failed to add book to library")

def show_search_form():
    """Display form for searching and adding books"""
    search_query = st.text_input("Search for books", placeholder="Enter book title, author, or ISBN")
    if st.button("🔍 Search", type="primary"):
        with st.spinner("Searching for books..."):
            results = search_books(search_query)
            if results:
                st.success(f"Found {len(results)} books")
                for book in results:
                    with st.container(border=True):
                        st.markdown(f"### {book['title']}")
                        st.markdown(f"**Author:** {book['author']}")
                        st.markdown(f"**Year:** {book['year']}")
                        st.markdown(f"**Genre:** {book['genre']}")
                        if book.get('cover_image'):
                            st.image(book['cover_image'], width=100)
                        if st.button("📚 Add to Library", key=f"add_{book['title']}"):
                            if add_book(book):
                                st.success(f"Added '{book['title']}' to your library!")
                                st.session_state.books = get_all_books()  # Refresh the book list
                                st.rerun()  # Refresh the page
                            else:
                                st.error("Failed to add book to library")
            else:
                st.info("No books found. Try a different search term.")
