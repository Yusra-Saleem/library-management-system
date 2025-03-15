import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.database import get_book_by_id, update_book, load_books

def show_edit_book_page():
    """Display the edit book page"""
    st.title("Edit Book")
    
    # Ensure edit_book_id is set in session state
    if 'edit_book_id' not in st.session_state:
        st.error("No book selected for editing")
        if st.button("Return to Home"):
            st.session_state.current_page = 'home'
            st.rerun()
        return
    
    # Get the book to edit
    book_id = st.session_state.edit_book_id
    print(f"📚 Editing book with ID: {book_id}")  # Debug statement
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
                
                # Save book
                if update_book(book_id, updated_book):
                    st.success(f"Updated '{title}' in your library!")
                    st.session_state.current_page = 'home'
                    st.rerun()
                else:
                    st.error("Failed to update the book. Please try again.")
        
        if cancelled:
            st.session_state.current_page = 'home'
            st.rerun()
