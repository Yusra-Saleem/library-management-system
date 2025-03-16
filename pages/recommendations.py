import streamlit as st
from helpers.ai_recommendations import get_book_recommendations
from helpers.book_api import search_books
from helpers.book_data import save_books, load_books

def show_recommendations_page():
    """Display the recommendations page with proper error handling"""
    st.title("Book Recommendations")
    
    if 'books' not in st.session_state:
        st.session_state.books = load_books()
    
    books = st.session_state.books
    
    if not books:
        st.info("📚 Add some books to your library to get personalized recommendations!")
        return
    
    # Recommendation type selection
    rec_type = st.radio(
        "Recommendation Type",
        ["Similar to my library", "Based on my favorite genres", "Surprise me!"],
        horizontal=True,
        key="rec_type"
    )
    
    # Convert selection to recommendation type parameter
    rec_type_param = "similar"
    if rec_type == "Based on my favorite genres":
        rec_type_param = "genre"
    elif rec_type == "Surprise me!":
        rec_type_param = "surprise"
    
    # Get recommendations section
    if st.button("Get Recommendations", key="get_recs", use_container_width=True):
        handle_recommendations(books, rec_type_param)
    
    # Show Open Library search results if requested
    if "show_rec_search" in st.session_state and st.session_state.show_rec_search:
        handle_search_results()
    
    # Reading suggestions section
    display_reading_suggestions(books)

def handle_recommendations(books, rec_type_param):
    """Handle recommendation generation and display"""
    with st.spinner("🔍 Analyzing your library and generating recommendations..."):
        try:
            recommendations = get_book_recommendations(books, rec_type_param)
            if recommendations:
                display_recommendations(recommendations)
            else:
                st.error("Failed to generate recommendations. Please try again.")
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")

def display_recommendations(recommendations):
    """Display recommendations in a grid layout"""
    st.subheader("Recommended Books")
    cols = st.columns(3)
    
    for i, book in enumerate(recommendations[:6]):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{book.get('title', 'Unknown Title')}**")
                st.caption(f"by {book.get('author', 'Unknown Author')}")
                
                if book.get('cover_image'):
                    st.image(book['cover_image'], use_column_width=True)
                
                if book.get('genre'):
                    st.write(f"*{book.get('genre')}*")
                
                if book.get('reason'):
                    with st.expander("Why we recommend this"):
                        st.write(book['reason'])
                
                if st.button("Find Details", key=f"find_{i}"):
                    handle_book_search(book)

def handle_book_search(book):
    """Handle Open Library search for recommended books"""
    search_query = f"{book.get('title', '')} {book.get('author', '')}"
    st.session_state.rec_search_query = search_query.strip()
    st.session_state.show_rec_search = True
    st.rerun()

def handle_search_results():
    """Display and handle search results"""
    st.divider()
    st.subheader("Open Library Search Results")
    
    if "rec_search_query" in st.session_state:
        with st.spinner("Searching Open Library..."):
            try:
                results = search_books(st.session_state.rec_search_query)
                display_search_results(results)
            except Exception as e:
                st.error(f"Search failed: {str(e)}")
    
    if st.button("Clear Search Results", key="clear_search"):
        st.session_state.show_rec_search = False
        st.rerun()

def display_search_results(results):
    """Display search results in a formatted way"""
    if results:
        for i, book in enumerate(results[:3]):
            with st.container(border=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**{book.get('title', 'Unknown Title')}**")
                    st.write(f"by {book.get('author', 'Unknown Author')}")
                    st.write(f"Published: {book.get('year', 'Unknown')}")
                    st.write(f"Genre: {book.get('genre', 'Unknown')}")
                    
                    if book.get('description'):
                        with st.expander("Description"):
                            st.write(book['description'][:300] + "..." 
                                   if len(book['description']) > 300 
                                   else book['description'])
                
                with cols[1]:
                    if book.get('cover_image'):
                        st.image(book['cover_image'], width=100)
    else:
        st.warning("No results found. Try a different search term.")

def display_reading_suggestions(books):
    """Display personalized reading suggestions"""
    st.divider()
    st.subheader("Personalized Reading Suggestions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Explore New Genres**")
        display_genre_suggestions(books)
    
    with col2:
        st.write("**Continue Reading**")
        display_reading_progress(books)

def display_genre_suggestions(books):
    """Display genre-based suggestions"""
    genre_counts = {}
    for book in books:
        if book.get('genre'):
            for genre in book['genre'].split(', '):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    if genre_counts:
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1])
        rare_genres = [g[0] for g in sorted_genres[:3] if g[1] < 3]
        
        if rare_genres:
            st.write("Try these less common genres in your library:")
            for genre in rare_genres:
                st.write(f"- {genre}")
        else:
            st.write("🌟 Your library has great genre diversity!")
    else:
        st.write("Add more books with genre information to get suggestions")

def display_reading_progress(books):
    """Display reading progress suggestions"""
    current_reading = [b for b in books if b.get('status') == 'Reading']
    to_read = [b for b in books if b.get('status') == 'To Read']
    
    if current_reading:
        book = current_reading[0]
        st.write(f"Continue reading:")
        st.markdown(f"📖 **{book.get('title')}** by {book.get('author')}")
        if st.button("Update Progress", key="update_progress"):
            handle_progress_update(book)
    elif to_read:
        book = to_read[0]
        st.write(f"Start reading:")
        st.markdown(f"📚 **{book.get('title')}** by {book.get('author')}")
        if st.button("Start Reading", key="start_reading"):
            handle_start_reading(book)
    else:
        st.write("Add books to your 'To Read' list to get started")

def handle_progress_update(book):
    """Handle reading progress updates"""
    new_progress = st.slider("Update Progress (%)", 0, 100, book.get('progress', 0),
                           key="progress_slider")
    if st.button("Save Progress", key="save_progress"):
        update_book_progress(book, new_progress)

def handle_start_reading(book):
    """Handle starting to read a book"""
    book['status'] = 'Reading'
    book['progress'] = 0
    if save_books([book]):
        st.success(f"Started reading {book.get('title')}!")
        st.session_state.books = load_books()
        st.rerun()
    else:
        st.error("Failed to update reading status")

def update_book_progress(book, progress):
    """Update reading progress in database"""
    book['progress'] = progress
    if save_books([book]):
        st.success(f"Updated progress for {book.get('title')}!")
        st.session_state.books = load_books()
        st.rerun()
    else:
        st.error("Failed to update progress")
