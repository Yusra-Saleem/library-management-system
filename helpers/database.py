import mysql.connector
from mysql.connector import pooling
import streamlit as st
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'pool_name': 'mypool',
    'pool_size': 5,
    'host': st.secrets["DB"]["HOST"],
    'user': st.secrets["DB"]["USER"],
    'password': st.secrets["DB"]["PASSWORD"],
    'database': st.secrets["DB"]["NAME"]
}

# Create connection pool
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
except Exception as e:
    st.error(f"Error creating connection pool: {str(e)}")

def init_db():
    """Initialize the database tables"""
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Create tables with proper indexing and foreign keys
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255),
                year VARCHAR(4),
                genre VARCHAR(255),
                description TEXT,
                cover_image TEXT,
                user_id INT,
                rating TINYINT CHECK (rating >= 1 AND rating <= 5),
                status VARCHAR(50),
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_title (title),
                INDEX idx_author (author),
                INDEX idx_user_id (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reading_lists (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            )
        ''')

        connection.commit()
        st.success("Database initialized successfully!")

    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def add_book(book_data, user_id=None):
    """Add a book to the database"""
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        query = '''
            INSERT INTO books (title, author, year, genre, description, cover_image, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        values = (
            book_data['title'],
            book_data['author'],
            book_data['year'],
            book_data['genre'],
            book_data['description'],
            book_data['cover_image'],
            user_id
        )

        cursor.execute(query, values)
        connection.commit()
        book_id = cursor.lastrowid
        
        st.success(f"Book '{book_data['title']}' added successfully!")
        return book_id

    except Exception as e:
        st.error(f"Error adding book: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def get_all_books(user_id=None):
    """Get all books from the database"""
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        if user_id:
            query = 'SELECT * FROM books WHERE user_id = %s ORDER BY date_added DESC'
            cursor.execute(query, (user_id,))
        else:
            query = 'SELECT * FROM books ORDER BY date_added DESC'
            cursor.execute(query)

        books = cursor.fetchall()
        return books

    except Exception as e:
        st.error(f"Error fetching books: {str(e)}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def search_books(query, user_id=None):
    """Search books in database"""
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        search_query = f"%{query}%"
        if user_id:
            sql_query = '''
                SELECT * FROM books 
                WHERE user_id = %s AND
                (title LIKE %s OR author LIKE %s OR genre LIKE %s)
                ORDER BY date_added DESC
            '''
            cursor.execute(sql_query, (user_id, search_query, search_query, search_query))
        else:
            sql_query = '''
                SELECT * FROM books 
                WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s
                ORDER BY date_added DESC
            '''
            cursor.execute(sql_query, (search_query, search_query, search_query))

        books = cursor.fetchall()
        return books

    except Exception as e:
        st.error(f"Error searching books: {str(e)}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def update_book(book_id, book_data):
    """Update book information"""
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        query = '''
            UPDATE books 
            SET title = %s, author = %s, year = %s, genre = %s,
                description = %s, cover_image = %s, status = %s, rating = %s
            WHERE id = %s
        '''
        values = (
            book_data['title'],
            book_data['author'],
            book_data['year'],
            book_data['genre'],
            book_data['description'],
            book_data['cover_image'],
            book_data.get('status'),
            book_data.get('rating'),
            book_id
        )

        cursor.execute(query, values)
        connection.commit()
        return True

    except Exception as e:
        st.error(f"Error updating book: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
          
