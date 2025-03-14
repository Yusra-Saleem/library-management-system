import sqlite3
import streamlit as st
from datetime import datetime

def add_book(book_data):
    """Add a book to database"""
    try:
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO books (
                title, author, year, genre, description, 
                cover_image, status, rating
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            book_data['title'],
            book_data['author'],
            book_data.get('year', ''),
            book_data.get('genre', ''),
            book_data.get('description', ''),
            book_data.get('cover_image', ''),
            book_data.get('status', 'To Read'),
            book_data.get('rating', 0)
        ))
        
        conn.commit()
        book_id = c.lastrowid
        conn.close()
        return book_id
        
    except Exception as e:
        st.error(f"Error adding book: {str(e)}")
        return None

def add_initial_books():
    """Add initial set of books to the database"""
    initial_books = [
        {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'year': '1960',
            'genre': 'Fiction',
            'description': 'A classic of modern American literature about justice and racial inequality in the American South.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222246-L.jpg',
            'status': 'Read',
            'rating': 5
        },
        {
            'title': '1984',
            'author': 'George Orwell',
            'year': '1949',
            'genre': 'Dystopian',
            'description': 'A dystopian novel about totalitarianism, surveillance, and the manipulation of truth.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222236-L.jpg',
            'status': 'Read',
            'rating': 4
        },
        {
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'year': '1813',
            'genre': 'Romance',
            'description': 'A romantic novel about the Bennet family and the proud Mr. Darcy.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222238-L.jpg',
            'status': 'Reading',
            'rating': 4
        },
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'year': '1925',
            'genre': 'Fiction',
            'description': 'A story of wealth, love, and the American Dream in the Roaring Twenties.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222237-L.jpg',
            'status': 'To Read',
            'rating': 0
        },
        {
            'title': 'Harry Potter and the Sorcerer\'s Stone',
            'author': 'J.K. Rowling',
            'year': '1997',
            'genre': 'Fantasy',
            'description': 'The first book in the Harry Potter series about a young wizard.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222240-L.jpg',
            'status': 'Read',
            'rating': 5
        },
        {
            'title': 'The Hobbit',
            'author': 'J.R.R. Tolkien',
            'year': '1937',
            'genre': 'Fantasy',
            'description': 'A fantasy novel about Bilbo Baggins and his quest to help reclaim a dwarf kingdom.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222241-L.jpg',
            'status': 'Read',
            'rating': 5
        },
        {
            'title': 'The Catcher in the Rye',
            'author': 'J.D. Salinger',
            'year': '1951',
            'genre': 'Fiction',
            'description': 'A story of teenage alienation and loss of innocence in New York City.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222242-L.jpg',
            'status': 'To Read',
            'rating': 0
        },
        {
            'title': 'The Lord of the Rings',
            'author': 'J.R.R. Tolkien',
            'year': '1954',
            'genre': 'Fantasy',
            'description': 'An epic high-fantasy novel about the quest to destroy the One Ring.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222243-L.jpg',
            'status': 'Reading',
            'rating': 4
        },
        {
            'title': 'Little Women',
            'author': 'Louisa May Alcott',
            'year': '1868',
            'genre': 'Fiction',
            'description': 'A story following the lives of the four March sisters.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222244-L.jpg',
            'status': 'Wishlist',
            'rating': 0
        },
        {
            'title': 'The Alchemist',
            'author': 'Paulo Coelho',
            'year': '1988',
            'genre': 'Fiction',
            'description': 'A philosophical story about following one\'s dreams.',
            'cover_image': 'https://covers.openlibrary.org/b/id/7222245-L.jpg',
            'status': 'Read',
            'rating': 4
        }
    ]

    for book in initial_books:
        add_book(book)

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            year TEXT,
            genre TEXT,
            description TEXT,
            cover_image TEXT,
            status TEXT DEFAULT 'To Read',
            rating INTEGER DEFAULT 0,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

    # Check if database is empty
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM books')
    count = c.fetchone()[0]
    conn.close()

    # Add initial books if database is empty
    if count == 0:
        add_initial_books()

def get_all_books():
    """Get all books from database"""
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM books ORDER BY date_added DESC')
    books = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return books

def search_local_books(query):
    """Search books in database"""
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    search_query = f"%{query}%"
    c.execute('''
        SELECT * FROM books 
        WHERE title LIKE ? 
        OR author LIKE ? 
        OR genre LIKE ?
    ''', (search_query, search_query, search_query))
    
    books = [dict(row) for row in c.fetchall()]
    conn.close()
    return books

def update_book(book_id, book_data):
    """Update book details"""
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('''
        UPDATE books 
        SET title=?, author=?, year=?, genre=?, description=?, 
            cover_image=?, status=?, rating=?
        WHERE id=?
    ''', (
        book_data['title'],
        book_data['author'],
        book_data['year'],
        book_data['genre'],
        book_data['description'],
        book_data['cover_image'],
        book_data.get('status', 'To Read'),
        book_data.get('rating', 0),
        book_id
    ))
    
    conn.commit()
    conn.close()

def delete_book(book_id):
    """Delete a book"""
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM books WHERE id=?', (book_id,))
    
    conn.commit()
    conn.close()
