import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.book_data import get_book_by_id, update_book, load_books

def show_edit_book_page():
    """Display the edit book page"""
    st.title("Edit Book")
    
    # Get the book to edit
    book_id = st.session_state.edit_book_id
    book = get_book_by_id(book_id)
    
    if not book:
        st.error("Book not found")
        if st.button("Return to Home"):
            st.session_state.current_page = 'home'
            st.rerun()
        return
    
    with st.form("edit_book_form"):
        st.subheader(f"Editing: {book.get('title', 'Unknown Book')}")
        
        # Book fields
        title = st.text_input("Title", value=book.get('title', ''))
        author = st.text_input("Author", value=book.get('author', ''))
        year = st.text_input("Publication Year", value=book.get('year', ''))
        genre = st.text_input("Genre", value=book.get('genre', ''),
                             help="Enter genre (e.g., Fiction, Science Fiction, Biography)")
        
        # Reading status
        status_options = ["To Read", "Reading", "Read", "Wishlist"]
        default_status_index = status_options.index(book.get('status')) if book.get('status') in status_options else 0
        status = st.selectbox("Reading Status", status_options, index=default_status_index)
        
        # Additional fields
        col1, col2 = st.columns(2)
        with col1:
            rating = st.slider("Your Rating", 0, 5, book.get('rating', 0))
        with col2:
            pages = st.number_input("Number of Pages", min_value=0, value=book.get('pages', 0))
        
        # Add progress tracking if book is in 'Reading' status
        if status == "Reading":
            progress = st.slider("Reading Progress (%)", 0, 100, book.get('progress', 0))
        else:
            progress = book.get('progress', 0)
        
        notes = st.text_area("Notes", value=book.get('notes', ''))
        
        # Submit button
        col1, col2 = st.columns(2)
        with col1:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        with col2:
            submitted = st.form_submit_button("Save Changes", use_container_width=True)
        
        if submitted:
            if not title or not author:
                st.error("Title and author are required")
            else:
                # Update book dictionary
                updated_book = {
                    "id": book_id,
                    "title": title,
                    "author": author,
                    "year": year,
                    "genre": genre,
                    "status": status,
                    "rating": rating,
                    "pages": pages,
                    "progress": progress,
                    "notes": notes,
                    "date_added": book.get('date_added')
                }
                
                # Preserve other fields
                for key, value in book.items():
                    if key not in updated_book:
                        updated_book[key] = value
                
                # Update book using update_book function
                if update_book(book_id, updated_book):
                    st.success(f"Updated '{title}' in your library!")
                    st.session_state.books = load_books()  # Refresh the book list
                    st.session_state.current_page = 'home'  # Return to home page
                    st.rerun()
                else:
                    st.error("Failed to update the book. Please try again.")
        
        if cancelled:
            st.session_state.current_page = 'home'
            st.rerun()
