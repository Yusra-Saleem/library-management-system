import os
import json
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
import streamlit as st

# Authentication helper functions

def hash_password(password, salt=None):
    """
    Hash a password using SHA-256 with a random salt
    
    Args:
        password (str): The password to hash
        salt (str, optional): Salt to use. If None, a new random salt is generated
        
    Returns:
        tuple: (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt, then hash
    password_bytes = (password + salt).encode('utf-8')
    hashed = hashlib.sha256(password_bytes).hexdigest()
    
    return hashed, salt

def generate_session_token():
    """Generate a random session token"""
    return secrets.token_hex(32)

def get_users_file_path():
    """Get the path to the users JSON file"""
    # Create data directory if it doesn't exist
    if not os.path.exists('data/users'):
        os.makedirs('data/users')
    
    return 'data/users/users.json'

def load_users():
    """Load users from the JSON file"""
    users_file = get_users_file_path()
    
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            return json.load(f)
    
    return {}

def save_users(users):
    """Save users to the JSON file"""
    users_file = get_users_file_path()
    
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)

def create_user(username, password, email):
    """
    Create a new user
    
    Args:
        username (str): Username
        password (str): Password
        email (str): Email address
        
    Returns:
        tuple: (success boolean, message string)
    """
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists. Please choose another username."
    
    # Check if email is already used
    for user_id, user_data in users.items():
        if user_data.get('email') == email:
            return False, "Email address is already registered."
    
    # Hash the password
    hashed_password, salt = hash_password(password)
    
    # Create user ID
    user_id = str(uuid.uuid4())
    
    # Current time
    current_time = datetime.now().isoformat()
    
    # Create user data
    users[user_id] = {
        'username': username,
        'email': email,
        'password_hash': hashed_password,
        'salt': salt,
        'created_at': current_time,
        'last_login': current_time
    }
    
    # Create user library file
    user_library_path = os.path.join('data/users', f'{user_id}.json')
    with open(user_library_path, 'w') as f:
        json.dump([], f)
    
    # Save users
    save_users(users)
    
    return True, "Account created successfully. You can now log in."

def authenticate_user(username_or_email, password):
    """
    Authenticate a user
    
    Args:
        username_or_email (str): Username or email address
        password (str): Password
        
    Returns:
        tuple: (success boolean, user_id or message string)
    """
    users = load_users()
    
    # Find user by username or email
    found_user_id = None
    for user_id, user_data in users.items():
        if user_data.get('username') == username_or_email or user_data.get('email') == username_or_email:
            found_user_id = user_id
            break
    
    if found_user_id is None:
        return False, "Invalid username or email."
    
    # Get user data
    user_data = users[found_user_id]
    
    # Hash the provided password with the stored salt
    hashed_password, _ = hash_password(password, user_data.get('salt'))
    
    # Check if passwords match
    if hashed_password != user_data.get('password_hash'):
        return False, "Invalid password."
    
    # Update last login time
    users[found_user_id]['last_login'] = datetime.now().isoformat()
    save_users(users)
    
    return True, found_user_id

def get_current_user():
    """
    Get the current logged-in user
    
    Returns:
        dict or None: User data if logged in, None otherwise
    """
    if 'user_id' not in st.session_state:
        return None
    
    users = load_users()
    user_id = st.session_state.user_id
    
    if user_id not in users:
        # Clear invalid session
        st.session_state.pop('user_id', None)
        return None
    
    return {
        'user_id': user_id,
        'username': users[user_id].get('username'),
        'email': users[user_id].get('email')
    }

def logout_user():
    """Log out the current user"""
    st.session_state.pop('user_id', None)
    st.session_state.pop('books', None)

def load_user_books(user_id):
    """
    Load books for a specific user
    
    Args:
        user_id (str): User ID
        
    Returns:
        list: List of book dictionaries
    """
    user_library_path = os.path.join('data/users', f'{user_id}.json')
    
    if os.path.exists(user_library_path):
        with open(user_library_path, 'r') as f:
            return json.load(f)
    
    return []

def save_user_books(user_id, books):
    """
    Save books for a specific user
    
    Args:
        user_id (str): User ID
        books (list): List of book dictionaries
    """
    user_library_path = os.path.join('data/users', f'{user_id}.json')
    
    with open(user_library_path, 'w') as f:
        json.dump(books, f, indent=2)

def show_login_page():
    """Display the login page and handle authentication"""
    st.title("Login to Your Library")
    
    # Login form
    with st.form("login_form"):
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("Register", use_container_width=True)
    
    # Handle login
    if login_button:
        if not username_or_email or not password:
            st.error("Please enter both username/email and password.")
        else:
            success, result = authenticate_user(username_or_email, password)
            if success:
                # Set session state
                st.session_state.user_id = result
                
                # Load user's books
                st.session_state.books = load_user_books(result)
                
                # Show success message and redirect
                st.success("Logged in successfully!")
                st.session_state.current_page = 'home'
                st.rerun()
            else:
                st.error(result)
    
    # Switch to registration page
    if register_button:
        st.session_state.current_page = 'register'
        st.rerun()

def show_register_page():
    """Display the user registration page"""
    st.title("Create an Account")
    
    # Registration form
    with st.form("register_form"):
        username = st.text_input("Username", 
                               help="Choose a unique username (3-20 characters)")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password",
                              help="Choose a strong password (min. 8 characters)")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Terms and privacy checkbox
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back to Login", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("Create Account", use_container_width=True)
    
    # Validate and create account
    if register_button:
        # Validate inputs
        if not username or not email or not password or not confirm_password:
            st.error("All fields are required.")
        elif len(username) < 3 or len(username) > 20:
            st.error("Username must be between 3 and 20 characters.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not agree_terms:
            st.error("You must agree to the Terms of Service and Privacy Policy.")
        else:
            # Create user
            success, message = create_user(username, password, email)
            if success:
                st.success(message)
                st.session_state.current_page = 'login'
                st.rerun()
            else:
                st.error(message)
    
    # Go back to login page
    if back_button:
        st.session_state.current_page = 'login'
        st.rerun()

def require_login():
    """
    Check if user is logged in, redirect to login page if not
    
    Returns:
        boolean: True if user is logged in, False otherwise
    """
    user = get_current_user()
    if user is None:
        # Set session state to login page
        st.session_state.current_page = 'login'
        return False
    
    return True