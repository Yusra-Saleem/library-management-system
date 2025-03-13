import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path so we can import helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.data_visualization import (
    create_reading_status_chart, 
    create_genre_distribution_chart, 
    create_yearly_acquisition_chart,
    create_publication_year_chart,
    create_reading_progress_chart
)
from helpers.book_data import get_book_status_counts, get_genre_counts, get_year_counts

def show_analytics_page():
    """Display the analytics page"""
    st.title("Library Analytics")
    
    books = st.session_state.books
    
    if not books:
        st.info("Add some books to your library to see analytics.")
        return
    
    # Create a DataFrame for analysis
    df = pd.DataFrame(books)
    
    # Overview section
    st.subheader("Quick Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Books", len(books))
    with col2:
        status_counts = get_book_status_counts(books)
        st.metric("Read", status_counts.get('Read', 0))
    with col3:
        st.metric("Reading", status_counts.get('Reading', 0))
    with col4:
        st.metric("To Read", status_counts.get('To Read', 0))
    
    # Main analytics
    tab1, tab2, tab3 = st.tabs(["Reading Stats", "Library Composition", "Reading Habits"])
    
    with tab1:
        show_reading_stats(books)
    
    with tab2:
        show_library_composition(books)
    
    with tab3:
        show_reading_habits(books)

def show_reading_stats(books):
    """Display reading statistics charts"""
    st.subheader("Reading Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        reading_status_fig = create_reading_status_chart(books)
        st.plotly_chart(reading_status_fig, use_container_width=True)
    
    with col2:
        reading_progress_fig = create_reading_progress_chart(books)
        st.plotly_chart(reading_progress_fig, use_container_width=True)
    
    # Reading statistics
    st.subheader("Reading Metrics")
    
    # Calculate reading metrics
    total_books = len(books)
    read_books = len([book for book in books if book.get('status') == 'Read'])
    
    total_pages = sum([book.get('pages', 0) for book in books if book.get('pages', 0) > 0])
    read_pages = sum([book.get('pages', 0) for book in books if book.get('status') == 'Read' and book.get('pages', 0) > 0])
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        completion_rate = (read_books / total_books * 100) if total_books > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col2:
        page_completion = (read_pages / total_pages * 100) if total_pages > 0 else 0
        st.metric("Pages Read", f"{read_pages} / {total_pages} ({page_completion:.1f}%)")
    
    with col3:
        avg_pages = (total_pages / total_books) if total_books > 0 else 0
        st.metric("Average Book Length", f"{avg_pages:.0f} pages")
    
    # Rating distribution
    ratings = [book.get('rating', 0) for book in books if book.get('rating') is not None and book.get('rating') > 0]
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        
        st.subheader("Rating Distribution")
        
        # Create rating distribution
        rating_counts = {}
        for i in range(1, 6):
            rating_counts[i] = len([r for r in ratings if r == i])
        
        # Display as horizontal bar chart
        st.bar_chart(rating_counts)
        
        st.metric("Average Rating", f"{avg_rating:.1f} / 5")

def show_library_composition(books):
    """Display library composition charts"""
    st.subheader("Genre Distribution")
    
    # Genre distribution chart
    genre_fig = create_genre_distribution_chart(books)
    st.plotly_chart(genre_fig, use_container_width=True)
    
    # Publication years
    st.subheader("Publication Years")
    
    # Publication year chart
    year_fig = create_publication_year_chart(books)
    st.plotly_chart(year_fig, use_container_width=True)
    
    # Authors statistics
    st.subheader("Top Authors")
    
    # Count books by author
    author_counts = {}
    for book in books:
        author = book.get('author', 'Unknown')
        author_counts[author] = author_counts.get(author, 0) + 1
    
    # Sort and display top authors
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_authors_dict = {author: count for author, count in top_authors}
    
    # Display as horizontal bar chart
    st.bar_chart(top_authors_dict)

def show_reading_habits(books):
    """Display reading habits charts"""
    st.subheader("Library Growth Over Time")
    
    # Library growth chart
    growth_fig = create_yearly_acquisition_chart(books)
    st.plotly_chart(growth_fig, use_container_width=True)
    
    # Reading rate calculation
    read_books = [book for book in books if book.get('status') == 'Read']
    if read_books:
        # Sort by date added
        read_books_with_date = [book for book in read_books if 'date_added' in book]
        if read_books_with_date:
            read_books_with_date.sort(key=lambda x: x['date_added'])
            
            # Calculate days between first and last book
            first_date = read_books_with_date[0]['date_added']
            last_date = read_books_with_date[-1]['date_added']
            
            # Convert dates to datetime objects for calculation
            try:
                from datetime import datetime
                first = datetime.strptime(first_date, '%Y-%m-%d')
                last = datetime.strptime(last_date, '%Y-%m-%d')
                days_diff = (last - first).days
                
                if days_diff > 0:
                    reading_rate = len(read_books_with_date) / (days_diff / 30)  # Books per month
                    
                    st.subheader("Reading Rate")
                    st.metric("Books per Month", f"{reading_rate:.1f}")
            except:
                pass
    
    # Book completion time
    read_books_with_pages = [book for book in read_books if book.get('pages', 0) > 0]
    if read_books_with_pages:
        total_pages_read = sum([book.get('pages', 0) for book in read_books_with_pages])
        avg_pages_per_book = total_pages_read / len(read_books_with_pages)
        
        st.subheader("Reading Speed Estimation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Let user input their reading speed
            reading_speed = st.number_input("Your reading speed (pages per hour)", min_value=1, value=30)
            
            # Calculate average time to complete a book
            avg_hours_per_book = avg_pages_per_book / reading_speed
            st.metric("Average Time per Book", f"{avg_hours_per_book:.1f} hours")
        
        with col2:
            # Calculate time needed for current "To Read" pile
            to_read_books = [book for book in books if book.get('status') == 'To Read' and book.get('pages', 0) > 0]
            if to_read_books:
                to_read_pages = sum([book.get('pages', 0) for book in to_read_books])
                hours_needed = to_read_pages / reading_speed
                
                st.metric("Time Needed for 'To Read' Books", f"{hours_needed:.1f} hours")
                st.metric("Number of 'To Read' Books", len(to_read_books))
