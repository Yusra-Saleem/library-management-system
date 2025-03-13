import streamlit as st
import pandas as pd

# Defensive imports for plotly
try:
    import plotly
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError as e:
    st.error(f"Failed to import plotly: {str(e)}")
    st.error("Please make sure plotly is installed correctly")
    raise

from helpers.book_data import get_book_status_counts, get_genre_counts, get_year_counts

def create_reading_status_chart(books):
    """
    Create a bar chart showing the distribution of reading status
    """
    status_counts = get_book_status_counts(books)
    
    # Convert to DataFrame for Streamlit
    df = pd.DataFrame({
        'Status': list(status_counts.keys()),
        'Count': list(status_counts.values())
    }).set_index('Status')
    
    st.bar_chart(df)
    return None

def create_genre_distribution_chart(books):
    """
    Create a bar chart showing the distribution of book genres
    """
    genre_counts = get_genre_counts(books)
    
    # If a book has multiple genres (comma-separated), count each genre separately
    expanded_genre_counts = {}
    for genre, count in genre_counts.items():
        if ', ' in genre:
            for g in genre.split(', '):
                expanded_genre_counts[g] = expanded_genre_counts.get(g, 0) + count
        else:
            expanded_genre_counts[genre] = expanded_genre_counts.get(genre, 0) + count
    
    # Sort genres by count and take top 10
    sorted_genres = sorted(expanded_genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Convert to DataFrame
    df = pd.DataFrame({
        'Genre': [item[0] for item in sorted_genres],
        'Count': [item[1] for item in sorted_genres]
    }).set_index('Genre')
    
    st.bar_chart(df)
    return None

def create_yearly_acquisition_chart(books):
    """
    Create a line chart showing books added over time
    """
    dates = {}
    for book in books:
        date_added = book.get('date_added', 'Unknown')
        if date_added and date_added != 'Unknown':
            dates[date_added] = dates.get(date_added, 0) + 1
    
    # Sort dates and create DataFrame
    df = pd.DataFrame({
        'Date': sorted(dates.keys()),
        'Books Added': [dates[date] for date in sorted(dates.keys())]
    }).set_index('Date')
    
    st.line_chart(df)
    return None

def create_publication_year_chart(books):
    """
    Create a bar chart showing the distribution of publication years
    """
    years = []
    for book in books:
        year = book.get('year', 'Unknown')
        if year and year != 'Unknown':
            try:
                years.append(int(year))
            except (ValueError, TypeError):
                continue
    
    if years:
        df = pd.DataFrame({'Year': years})
        year_counts = df['Year'].value_counts().sort_index()
        st.bar_chart(year_counts)
    return None

def create_reading_progress_chart(books):
    """
    Create a metric showing reading progress
    """
    read_count = len([book for book in books if book.get('status') == 'Read'])
    total_count = len(books)
    
    read_percentage = (read_count / total_count * 100) if total_count > 0 else 0
    
    st.metric(
        label="Reading Progress",
        value=f"{read_percentage:.1f}%",
        delta=f"{read_count} of {total_count} books"
    )
    return None
