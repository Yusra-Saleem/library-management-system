import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from helpers.book_data import get_book_status_counts, get_genre_counts, get_year_counts

def create_reading_status_chart(books):
    """
    Create a pie chart showing the distribution of reading status
    
    Args:
        books (list): List of book dictionaries
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    status_counts = get_book_status_counts(books)
    
    # Prepare data for the chart
    statuses = list(status_counts.keys())
    counts = list(status_counts.values())
    
    # Define a color map for consistent colors
    color_map = {
        'Read': '#43A047',
        'Reading': '#1E88E5',
        'To Read': '#FFC107',
        'Wishlist': '#E91E63',
        'Unknown': '#9E9E9E'
    }
    
    # Get colors based on statuses
    colors = [color_map.get(status, '#9E9E9E') for status in statuses]
    
    # Create the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=statuses,
        values=counts,
        hole=.4,
        marker_colors=colors
    )])
    
    fig.update_layout(
        title_text="Reading Status",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    
    return fig

def create_genre_distribution_chart(books):
    """
    Create a bar chart showing the distribution of book genres
    
    Args:
        books (list): List of book dictionaries
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
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
    genres = [item[0] for item in sorted_genres]
    counts = [item[1] for item in sorted_genres]
    
    # Create the bar chart
    fig = go.Figure(data=[go.Bar(
        x=genres,
        y=counts,
        marker_color='#1E88E5'
    )])
    
    fig.update_layout(
        title_text="Top Genres",
        xaxis_title="Genre",
        yaxis_title="Number of Books",
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    
    return fig

def create_yearly_acquisition_chart(books):
    """
    Create a line chart showing books added over time
    
    Args:
        books (list): List of book dictionaries
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    # Prepare data - count books by date added
    dates = {}
    for book in books:
        date_added = book.get('date_added', 'Unknown')
        if date_added and date_added != 'Unknown':
            dates[date_added] = dates.get(date_added, 0) + 1
    
    # Sort dates and create cumulative sum
    sorted_dates = sorted(dates.items())
    dates_list = [item[0] for item in sorted_dates]
    counts = [item[1] for item in sorted_dates]
    cumulative = [sum(counts[:i+1]) for i in range(len(counts))]
    
    # Create the line chart
    fig = go.Figure()
    
    # Add bars for books added per date
    fig.add_trace(go.Bar(
        x=dates_list,
        y=counts,
        name='Books Added',
        marker_color='#43A047'
    ))
    
    # Add line for cumulative count
    fig.add_trace(go.Scatter(
        x=dates_list,
        y=cumulative,
        mode='lines+markers',
        name='Total Books',
        marker_color='#1E88E5',
        line=dict(width=3)
    ))
    
    fig.update_layout(
        title_text="Library Growth Over Time",
        xaxis_title="Date Added",
        yaxis_title="Number of Books",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    
    return fig

def create_publication_year_chart(books):
    """
    Create a histogram showing the distribution of publication years
    
    Args:
        books (list): List of book dictionaries
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    # Get years that are valid numbers
    years = []
    for book in books:
        year = book.get('year', 'Unknown')
        if year and year != 'Unknown':
            try:
                years.append(int(year))
            except (ValueError, TypeError):
                continue
    
    if not years:
        # Return empty figure if no valid years
        fig = go.Figure()
        fig.update_layout(
            title_text="Publication Years",
            xaxis_title="Year",
            yaxis_title="Number of Books",
            height=400,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        return fig
    
    # Create the histogram
    fig = px.histogram(
        x=years,
        nbins=min(20, len(set(years))),
        labels={'x': 'Publication Year', 'y': 'Number of Books'},
        color_discrete_sequence=['#1E88E5']
    )
    
    fig.update_layout(
        title_text="Publication Years",
        xaxis_title="Year",
        yaxis_title="Number of Books",
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    
    return fig

def create_reading_progress_chart(books):
    """
    Create a gauge chart showing reading progress
    
    Args:
        books (list): List of book dictionaries
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    read_count = len([book for book in books if book.get('status') == 'Read'])
    total_count = len(books)
    
    read_percentage = (read_count / total_count * 100) if total_count > 0 else 0
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = read_percentage,
        title = {'text': "Reading Progress"},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#43A047"},
            'steps': [
                {'range': [0, 25], 'color': "#EF5350"},
                {'range': [25, 50], 'color': "#FFA726"},
                {'range': [50, 75], 'color': "#FFEE58"},
                {'range': [75, 100], 'color': "#66BB6A"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    
    return fig
