import streamlit as st
from helpers.ai_recommendations import get_book_recommendations
from helpers.book_api import search_books
from helpers.book_data import load_books, update_book_status

def show_recommendations_page():
    """Display the recommendations page with real-time updates"""
    st.title("Book Recommendations")
    
    # Fetch books from the database (real-time)
    books = load_books()
    
    if not books:
        st.info("Add some books to your library to get recommendations.")
        return
    
    # Recommendation type selection
    rec_type = st.radio(
        "Recommendation Type",
        ["Similar to my library", "Based on my favorite genres", "Surprise me!"],
        horizontal=True
    )
    
    # Convert selection to recommendation type parameter
    rec_type_param = "similar"
    if rec_type == "Based on my favorite genres":
        rec_type_param = "genre"
    elif rec_type == "Surprise me!":
        rec_type_param = "surprise"
    
    # Get recommendations button
    if st.button("Get Recommendations", use_container_width=True):
        with st.spinner("Generating recommendations..."):
            recommendations = get_book_recommendations(books, rec_type_param)
        
        if recommendations:
            st.subheader("Recommended Books")
            
            # Display recommendations in cards
            for i, book in enumerate(recommendations):
                with st.container(border=True):
                    st.subheader(book.get('title', 'Unknown Title'))
                    st.write(f"**Author:** {book.get('author', 'Unknown Author')}")
                    
                    if 'genre' in book:
                        st.write(f"**Genre:** {book.get('genre', 'Unknown')}")
                    
                    if 'reason' in book:
                        with st.expander("Why we recommend this"):
                            st.write(book.get('reason', ''))
                    
                    # Add button to find on Open Library
                    if st.button(f"Okay! Thank You", key=f"find_{i}"):
                        # Set search as the book title and author
                        search_query = f"{book.get('title', '')} {book.get('author', '')}"
                        st.session_state.rec_search_query = search_query
                        st.session_state.show_rec_search = True
                        st.rerun()
        else:
            st.error("Failed to generate recommendations. Please try again.")
    
    # Show Open Library search results if requested
    if "show_rec_search" in st.session_state and st.session_state.show_rec_search:
        st.divider()
        st.subheader("Open Library Search Results")
        
        query = st.session_state.rec_search_query
        with st.spinner("Searching..."):
            search_results = search_books(query)
        
        if search_results:
            # Display first 3 search results
            for i, book in enumerate(search_results[:3]):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(book.get('title', 'Unknown Title'))
                        st.write(f"**Author:** {book.get('author', 'Unknown Author')}")
                        st.write(f"**Year:** {book.get('year', 'Unknown')}")
                        st.write(f"**Genre:** {book.get('genre', 'Unknown')}")
                        
                        if 'description' in book and book['description']:
                            with st.expander("Description"):
                                st.write(book['description'][:300] + "..." if len(book['description']) > 300 else book['description'])
                    
                    with col2:
                        if 'cover_image' in book and book['cover_image']:
                            st.image(book['cover_image'], width=100)
        else:
            st.warning("No books found. Try another recommendation.")
        
        if st.button("Clear Search Results"):
            st.session_state.show_rec_search = False
            st.rerun()
    
    # Display reading suggestions based on library stats
    st.divider()
    st.subheader("Reading Suggestions")
    
    # Analyze library for patterns
    read_books = [book for book in books if book.get('status') == 'Read']
    to_read_books = [book for book in books if book.get('status') == 'To Read']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Genres to Explore**")
        
        # Find genres with few books
        genre_counts = {}
        for book in books:
            genre = book.get('genre', 'Unknown')
            if genre and genre != 'Unknown':
                # Split genres if they contain commas
                for g in genre.split(', '):
                    genre_counts[g] = genre_counts.get(g, 0) + 1
        
        # Sort by count
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1])
        
        # Suggest underrepresented genres (less than 2 books)
        underrepresented = [genre for genre, count in sorted_genres if count < 2]
        
        if underrepresented:
            for genre in underrepresented[:5]:
                st.write(f"- {genre}")
        else:
            st.write("Your library has a good variety of genres!")
    
    with col2:
        st.write("**Next Book to Read**")
        
        # Suggest a book from the to-read pile
        if to_read_books:
            # Sort by date added (newest first)
            to_read_books_with_date = [book for book in to_read_books if 'date_added' in book]
            if to_read_books_with_date:
                to_read_books_with_date.sort(key=lambda x: x['date_added'], reverse=True)
                suggested_book = to_read_books_with_date[0]
                
                st.write(f"- **{suggested_book.get('title', 'Unknown')}** by {suggested_book.get('author', 'Unknown')}")
                if st.button("Update Status"):
                    # Update book status in the database
                    if update_book_status(suggested_book.get('id'), 'Reading'):
                        st.success(f"Updated '{suggested_book.get('title')}' to 'Reading' status!")
                        st.rerun()  # Refresh the page to reflect changes
                    else:
                        st.error("Failed to update book status")
        else:
            st.write("Add books to your 'To Read' list first!")
