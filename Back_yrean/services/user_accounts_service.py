import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UserAccountsService:
    def __init__(self):
        """Initialize the service with database connection parameters."""
        self.db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_ENDPOINT'),
            'port': os.getenv('DB_PORT')
        }

    def _get_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(**self.db_params, cursor_factory=RealDictCursor)

    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user in the database.
        
        Args:
            username: The username for the new user
            email: The email address for the new user
            password: The plain text password to be hashed
            
        Returns:
            Dict containing the created user's information (excluding password)
            
        Raises:
            Exception: If user creation fails (e.g., duplicate username/email)
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Hash the password before storing
                    password_hash = generate_password_hash(password)
                    
                    # Insert the new user
                    cur.execute("""
                        INSERT INTO users (username, email, password_hash)
                        VALUES (%s, %s, %s)
                        RETURNING user_id, username, email, created_at
                    """, (username, email, password_hash))
                    
                    user = cur.fetchone()
                    conn.commit()
                    return dict(user)
                    
        except psycopg2.IntegrityError as e:
            if "users_username_key" in str(e):
                raise Exception("Username already exists")
            elif "users_email_key" in str(e):
                raise Exception("Email already exists")
            raise Exception("Failed to create user")
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: The UUID of the user to retrieve
            
        Returns:
            Dict containing user information or None if not found
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Convert UUID to string for database query
                    user_id_str = str(user_id)
                    cur.execute("""
                        SELECT user_id, username, email, created_at
                        FROM users
                        WHERE user_id = %s::uuid
                    """, (user_id_str,))
                    
                    user = cur.fetchone()
                    return dict(user) if user else None
                    
        except Exception as e:
            raise Exception(f"Error retrieving user: {str(e)}")

    def verify_password(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Verify a user's password and return their information if correct.
        
        Args:
            username: The username to verify
            password: The plain text password to verify
            
        Returns:
            Dict containing user information if password is correct, None otherwise
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, username, email, password_hash, created_at
                        FROM users
                        WHERE username = %s
                    """, (username,))
                    
                    user = cur.fetchone()
                    if user and check_password_hash(user['password_hash'], password):
                        # Remove password hash from returned data
                        user_dict = dict(user)
                        del user_dict['password_hash']
                        return user_dict
                    return None
                    
        except Exception as e:
            raise Exception(f"Error verifying password: {str(e)}") 