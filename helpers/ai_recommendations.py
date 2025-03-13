import os
import json
import random
from openai import OpenAI
from helpers.book_data import load_books
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def get_book_recommendations(user_books, recommendation_type="similar"):
    """
    Get AI-powered book recommendations based on user's library
    
    Args:
        user_books (list): List of user's books
        recommendation_type (str): Type of recommendation ('similar', 'genre', 'surprise')
        
    Returns:
        list: List of recommended books
    """
    if not user_books:
        return []
    
    # Check if OpenAI API key is available
    if not OPENAI_API_KEY:
        # Fallback to simple recommendation if no API key
        return get_simple_recommendations(user_books, recommendation_type)
    
    try:
        # Prepare data for OpenAI prompt
        # Extract relevant information about user's library
        user_genres = [book.get('genre', 'Unknown') for book in user_books if book.get('genre')]
        user_authors = [book.get('author', 'Unknown') for book in user_books if book.get('author')]
        user_titles = [book.get('title', 'Unknown') for book in user_books if book.get('title')]
        
        # Create a prompt based on recommendation type
        if recommendation_type == "similar":
            prompt = (
                f"Based on these books in my library: {', '.join(user_titles[:5])}, "
                f"by authors: {', '.join(user_authors[:5])}, "
                f"recommend 5 similar books I might enjoy. "
                f"Format the response as a JSON array with objects containing 'title', 'author', and 'reason' fields."
            )
        elif recommendation_type == "genre":
            # Get most common genres
            genre_counts = {}
            for genre in user_genres:
                if genre and genre != 'Unknown':
                    for g in genre.split(', '):
                        genre_counts[g] = genre_counts.get(g, 0) + 1
            
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            top_genre_names = [g[0] for g in top_genres]
            
            prompt = (
                f"Based on my preference for these genres: {', '.join(top_genre_names)}, "
                f"recommend 5 highly regarded books in these genres that aren't already in my library: {', '.join(user_titles[:10])}. "
                f"Format the response as a JSON array with objects containing 'title', 'author', 'genre', and 'reason' fields."
            )
        else:  # surprise
            prompt = (
                "Recommend 5 surprising and unique books that might expand my reading horizons. "
                "They should be different from what I usually read but still engaging. "
                f"My current library includes: {', '.join(user_titles[:5])}. "
                f"Format the response as a JSON array with objects containing 'title', 'author', 'genre', and 'reason' fields."
            )
        
        # Call OpenAI API
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a literary expert providing book recommendations."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        # Parse response
        recommendations_text = response.choices[0].message.content
        recommendations = json.loads(recommendations_text)
        
        # Check if the response is in the expected format
        if isinstance(recommendations, dict) and 'recommendations' in recommendations:
            return recommendations['recommendations']
        elif isinstance(recommendations, list):
            return recommendations
        else:
            return get_simple_recommendations(user_books, recommendation_type)
            
    except Exception as e:
        print(f"Error getting AI recommendations: {str(e)}")
        # Fallback to simple recommendation
        return get_simple_recommendations(user_books, recommendation_type)

def get_simple_recommendations(user_books, recommendation_type="similar"):
    """
    Get simple book recommendations based on user's library when AI isn't available
    
    Args:
        user_books (list): List of user's books
        recommendation_type (str): Type of recommendation ('similar', 'genre', 'surprise')
        
    Returns:
        list: List of recommended books
    """
    # Sample classic book recommendations as fallback
    classic_recommendations = [
        {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "genre": "Fiction",
            "reason": "A timeless classic about justice and moral growth."
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "genre": "Dystopian",
            "reason": "Powerful examination of totalitarianism and surveillance."
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "genre": "Romance",
            "reason": "Brilliant social commentary with memorable characters."
        },
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Fiction",
            "reason": "Captivating portrayal of the American Dream in the 1920s."
        },
        {
            "title": "One Hundred Years of Solitude",
            "author": "Gabriel García Márquez",
            "genre": "Magical Realism",
            "reason": "A masterpiece of magical realism and family saga."
        }
    ]
    
    # Filter out books the user already has
    user_titles = [book.get('title', '').lower() for book in user_books]
    
    filtered_recommendations = [
        rec for rec in classic_recommendations 
        if rec["title"].lower() not in user_titles
    ]
    
    # If we've filtered out all recommendations, return the originals
    if not filtered_recommendations:
        return classic_recommendations[:3]
    
    return filtered_recommendations[:3]
