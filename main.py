import streamlit as st
# First command must be set_page_config
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Then import other modules
import pandas as pd
import os
import json
import sys
import importlib
import traceback
from datetime import datetime
from helpers.database import init_db, add_book, get_all_books, delete_book

# Import helper modules
# from helpers.theme import setup_page, toggle_theme
from helpers.book_data import load_books, save_book, get_book_status_counts
from helpers.data_visualization import create_reading_status_chart, create_genre_distribution_chart
# from helpers.book_api import search_google_books
from helpers.auth import show_login_page, show_register_page, get_current_user, logout_user, require_login

# Import page modules using importlib to ensure they're freshly loaded
import pages.add_book
import pages.edit_book
import pages.search
import pages.analytics
import pages.recommendations
import pages.import_export

# Reload modules to ensure changes are picked up
importlib.reload(pages.add_book)
importlib.reload(pages.edit_book)
importlib.reload(pages.search)
importlib.reload(pages.analytics)
importlib.reload(pages.recommendations)
importlib.reload(pages.import_export)

# Get functions from modules after reload
show_add_book_page = pages.add_book.show_add_book_page
show_edit_book_page = pages.edit_book.show_edit_book_page
show_search_page = pages.search.show_search_page
show_analytics_page = pages.analytics.show_analytics_page
show_recommendations_page = pages.recommendations.show_recommendations_page
show_import_export_page = pages.import_export.show_import_export_page

# Load custom CSS
with open('assets/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize session state
if 'books' not in st.session_state:
    st.session_state.books = get_all_books()
# if 'dark_mode' not in st.session_state:
#     st.session_state.dark_mode = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
if 'filter_genre' not in st.session_state:
    st.session_state.filter_genre = 'All'
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = 'All'
if 'edit_book_id' not in st.session_state:
    st.session_state.edit_book_id = None

# Setup page with theme
# setup_page()

# Sidebar
with st.sidebar:
   
    st.title(" My Library" )
    
    # # Dark/Light Mode Toggl
    # toggle_theme()
    
    st.divider()
    
    # Sidebar Navigation
    if st.button("Home", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()
    
    if st.button("Add Book", use_container_width=True):
        st.session_state.current_page = 'add_book'
        st.rerun()
    
    if st.button("Search", use_container_width=True):
        st.session_state.current_page = 'search'
        st.rerun()
    
    if st.button("Analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()
    
    if st.button("Recommendations", use_container_width=True):
        st.session_state.current_page = 'recommendations'
        st.rerun()
    
    if st.button("Import/Export", use_container_width=True):
        st.session_state.current_page = 'import_export'
        st.rerun()
    
    st.divider()
    
    # Library Stats
    st.subheader("Library Stats")
    book_counts = get_book_status_counts(st.session_state.books)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Books", len(st.session_state.books))
    with col2:
        read_percentage = (book_counts.get('Read', 0) / len(st.session_state.books) * 100) if len(st.session_state.books) > 0 else 0
        st.metric("Read", f"{read_percentage:.1f}%")

# Main content
if st.session_state.current_page == 'home':
    # Home Page
    st.title("Personal Library Management System")
    
    # Quick Stats
    st.header("Quick Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Books", len(st.session_state.books))
    with col2:
        book_counts = get_book_status_counts(st.session_state.books)
        st.metric("Read", book_counts.get('Read', 0))
    with col3:
        st.metric("Wishlist", book_counts.get('Wishlist', 0))
    
    # Dashboard Charts
    st.subheader("Library Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(st.session_state.books) > 0:
            reading_status_fig = create_reading_status_chart(st.session_state.books)
            st.plotly_chart(reading_status_fig, use_container_width=True)
        else:
            st.info("Add books to see reading status statistics.")
    
    with col2:
        if len(st.session_state.books) > 0:
            genre_fig = create_genre_distribution_chart(st.session_state.books)
            st.plotly_chart(genre_fig, use_container_width=True)
        else:
            st.info("Add books to see genre distribution.")
    
    # Recent Books
    st.subheader("My Books")
    
    # Search and Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("Search Books", st.session_state.search_query)
        st.session_state.search_query = search
    
    with col2:
        if len(st.session_state.books) > 0:
            genres = ['All'] + list(set([book.get('genre', 'Unknown') for book in st.session_state.books]))
            genre_filter = st.selectbox("Filter by Genre", genres, index=genres.index(st.session_state.filter_genre) if st.session_state.filter_genre in genres else 0)
            st.session_state.filter_genre = genre_filter
        else:
            st.empty()
    
    with col3:
        statuses = ['All', 'Read', 'Reading', 'To Read', 'Wishlist']
        status_filter = st.selectbox("Filter by Status", statuses, index=statuses.index(st.session_state.filter_status) if st.session_state.filter_status in statuses else 0)
        st.session_state.filter_status = status_filter
    
    # Filter books based on search and filters
    filtered_books = st.session_state.books
    
    if st.session_state.search_query:
        filtered_books = [book for book in filtered_books if 
                         st.session_state.search_query.lower() in book.get('title', '').lower() or 
                         st.session_state.search_query.lower() in book.get('author', '').lower()]
    
    if st.session_state.filter_genre != 'All':
        filtered_books = [book for book in filtered_books if book.get('genre', 'Unknown') == st.session_state.filter_genre]
    
    if st.session_state.filter_status != 'All':
        filtered_books = [book for book in filtered_books if book.get('status', 'Unknown') == st.session_state.filter_status]
    
    # Display books in grid
    if filtered_books:
        book_cols = st.columns(3)
        for i, book in enumerate(filtered_books):
            with book_cols[i % 3]:
                with st.container(border=True):
                    st.subheader(book.get('title', 'Untitled'))
                    st.write(f"**Author:** {book.get('author', 'Unknown')}")
                    st.write(f"**Genre:** {book.get('genre', 'Unknown')}")
                    st.write(f"**Year:** {book.get('year', 'Unknown')}")
                    st.write(f"**Status:** {book.get('status', 'Unknown')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit 📝", key=f"edit_{i}", use_container_width=True):
                            st.session_state.edit_book_id = book.get('id')
                            st.session_state.current_page = 'edit_book'
                            st.rerun()
                    with col2:
                        if st.button(f"Delete 🗑️", key=f"delete_{i}", use_container_width=True):
                            delete_book(book.get('id'))
                            st.session_state.books = get_all_books()
                            st.rerun()
    else:
        st.info("No books match your search criteria. Add some books or change your filters.")

elif st.session_state.current_page == 'add_book':
    show_add_book_page()
    st.session_state.books = get_all_books()
elif st.session_state.current_page == 'edit_book':
    show_edit_book_page()
elif st.session_state.current_page == 'search':
    show_search_page()
elif st.session_state.current_page == 'analytics':
    show_analytics_page()
elif st.session_state.current_page == 'recommendations':
    show_recommendations_page()
elif st.session_state.current_page == 'import_export':
    show_import_export_page()
