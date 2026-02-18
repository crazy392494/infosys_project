"""
Authentication module for user registration and login
Handles password hashing and verification
"""

import bcrypt
import re
from typing import Optional, Tuple
from database import create_user, get_user_by_email


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 100:
        return False, "Password is too long"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username
    Returns: (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username is too long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""


def register_user(username: str, email: str, password: str) -> Tuple[bool, str, Optional[int]]:
    """
    Register a new user
    Returns: (success, message, user_id)
    """
    # Validate username
    is_valid, error = validate_username(username)
    if not is_valid:
        return False, error, None
    
    # Validate email
    if not validate_email(email):
        return False, "Invalid email format", None
    
    # Validate password
    is_valid, error = validate_password(password)
    if not is_valid:
        return False, error, None
    
    # Check if email already exists
    if get_user_by_email(email):
        return False, "Email already registered", None
    
    # Hash password and create user
    password_hash = hash_password(password)
    user_id = create_user(username, email, password_hash)
    
    if user_id:
        return True, "Registration successful", user_id
    else:
        return False, "Registration failed", None


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Authenticate a user
    Returns: (success, message, user_data)
    """
    if not email or not password:
        return False, "Email and password are required", None
    
    user = get_user_by_email(email)
    
    if not user:
        return False, "Invalid email or password", None
    
    if verify_password(password, user['password_hash']):
        # Don't return password hash to the application
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
        }
        return True, "Login successful", user_data
    else:
        return False, "Invalid email or password", None


def check_user_exists(email: str) -> bool:
    """Check if a user with the given email exists"""
    return get_user_by_email(email) is not None
