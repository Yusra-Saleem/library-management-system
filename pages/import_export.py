import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.file_operations import (
    export_to_csv, 
    export_to_json, 
    import_from_csv, 
    import_from_json,
    merge_books ,
    save_books,
)
from helpers.book_data import load_books, save_books

def show_import_export_page():
    """Display the import/export page"""
    st.title("Import & Export Library Data")
    
    tab1, tab2 = st.tabs(["Export", "Import"])
    
    with tab1:
        show_export_section()
    
    with tab2:
        show_import_section()

def show_export_section():
    """Display the export section"""
    st.subheader("Export Your Library")
    
    books = st.session_state.books
    
    if not books:
        st.warning("Your library is empty. Add some books before exporting.")
        return
    
    # Export format selection
    export_format = st.radio("Select export format", ["CSV", "JSON"], horizontal=True)
    
    # Export options
    include_all = st.checkbox("Include all metadata", value=True, 
                            help="Include all book details like notes, date added, etc.")
    
    if not include_all:
        st.info("Basic export will only include title, author, year, genre, and status.")
    
    # Filter books based on options
    if not include_all:
        filtered_books = []
        for book in books:
            filtered_book = {
                'title': book.get('title', ''),
                'author': book.get('author', ''),
                'year': book.get('year', ''),
                'genre': book.get('genre', ''),
                'status': book.get('status', '')
            }
            filtered_books.append(filtered_book)
        export_books = filtered_books
    else:
        export_books = books
    
    # Export button
    if st.button("Export Library", use_container_width=True):
        if export_format == "CSV":
            csv_bytes = export_to_csv(export_books)
            if csv_bytes:
                st.download_button(
                    label="Download CSV",
                    data=csv_bytes,
                    file_name="my_library.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:  # JSON
            json_bytes = export_to_json(export_books)
            if json_bytes:
                st.download_button(
                    label="Download JSON",
                    data=json_bytes,
                    file_name="my_library.json",
                    mime="application/json",
                    use_container_width=True
                )

def show_import_section():
    """Display the import section"""
    st.subheader("Import Books")
    
    # Import instructions
    with st.expander("Import Instructions", expanded=True):
        st.markdown("""
        ### CSV Import Format
        Your CSV file should have the following columns:
        - `title` (required)
        - `author` (required)
        - `year` (optional)
        - `genre` (optional)
        - `status` (optional) - Can be "Read", "Reading", "To Read", or "Wishlist"
        
        ### JSON Import Format
        Your JSON file should be an array of book objects with at least:
        ```json
        [
          {
            "title": "Book Title",
            "author": "Author Name"
          }
        ]
        ```
        """)
    
    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "json"])
    
    if uploaded_file is not None:
        # Import strategy
        import_strategy = st.radio(
            "Import Strategy", 
            ["Add to existing library", "Replace existing books with same ID", "Keep existing books (ignore duplicates)"],
            index=0
        )
        
        strategy_map = {
            "Add to existing library": "add",
            "Replace existing books with same ID": "replace",
            "Keep existing books (ignore duplicates)": "keep"
        }
        
        # Map the selected strategy to the function parameter
        strategy = strategy_map[import_strategy]
        
        # Import button
        if st.button("Import Books", use_container_width=True):
            # Process the file based on its type
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type == 'csv':
                success, message, imported_books = import_from_csv(uploaded_file)
            elif file_type == 'json':
                success, message, imported_books = import_from_json(uploaded_file)
            else:
                success = False
                message = "Unsupported file type. Please upload a CSV or JSON file."
                imported_books = []
            
            if success:
                # Merge imported books with existing library
                existing_books = load_books()
                merged_books = merge_books(existing_books, imported_books, strategy)
                
                # Save merged books
                if save_books(merged_books):
                    # Update session state
                    st.session_state.books = merged_books
                    
                    # Show success message
                    st.success(f"{message} - Added to your library!")
                    
                    # Display preview of imported books
                    st.subheader("Imported Books Preview")
                    
                    # Create a DataFrame for display
                    df = pd.DataFrame(imported_books)
                    st.dataframe(df)
                    
                    # Option to return home
                    if st.button("Return to Home"):
                        st.session_state.current_page = 'home'
                        st.rerun()
                else:
                    st.error("Failed to save imported books to the database.")
            else:
                st.error(message)
