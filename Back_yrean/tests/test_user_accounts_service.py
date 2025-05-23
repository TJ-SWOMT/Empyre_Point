import pytest
import uuid
from services.user_accounts_service import UserAccountsService
from psycopg2.extras import RealDictCursor
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="module")
def db_connection():
    """Create a database connection for testing."""
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_ENDPOINT'),
        'port': os.getenv('DB_PORT')
    }
    
    conn = psycopg2.connect(**db_params, cursor_factory=RealDictCursor)
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def clean_users_table(db_connection):
    """Clean up the users table before each test."""
    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM users")
        db_connection.commit()
    yield
    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM users")
        db_connection.commit()

@pytest.fixture(scope="function")
def user_service():
    """Create a fresh UserAccountsService instance for each test."""
    return UserAccountsService()

def test_create_user_success(user_service, clean_users_table):
    """Test successful user creation."""
    # Arrange
    username = "testuser"
    email = "test@example.com"
    password = "testpassword123"
    
    # Act
    user = user_service.create_user(username, email, password)
    
    # Assert
    assert user is not None
    assert user['username'] == username
    assert user['email'] == email
    assert 'password_hash' not in user
    assert 'user_id' in user
    assert 'created_at' in user

def test_create_duplicate_username(user_service, clean_users_table):
    """Test creating a user with a duplicate username."""
    # Arrange
    username = "testuser"
    email1 = "test1@example.com"
    email2 = "test2@example.com"
    password = "testpassword123"
    
    # Act
    user_service.create_user(username, email1, password)
    
    # Assert
    with pytest.raises(Exception) as exc_info:
        user_service.create_user(username, email2, password)
    assert "Username already exists" in str(exc_info.value)

def test_create_duplicate_email(user_service, clean_users_table):
    """Test creating a user with a duplicate email."""
    # Arrange
    username1 = "testuser1"
    username2 = "testuser2"
    email = "test@example.com"
    password = "testpassword123"
    
    # Act
    user_service.create_user(username1, email, password)
    
    # Assert
    with pytest.raises(Exception) as exc_info:
        user_service.create_user(username2, email, password)
    assert "Email already exists" in str(exc_info.value)

def test_get_user_by_id(user_service, clean_users_table):
    """Test retrieving a user by ID."""
    # Arrange
    username = "testuser"
    email = "test@example.com"
    password = "testpassword123"
    
    # Act
    created_user = user_service.create_user(username, email, password)
    retrieved_user = user_service.get_user_by_id(uuid.UUID(created_user['user_id']))
    
    # Assert
    assert retrieved_user is not None
    assert retrieved_user['username'] == username
    assert retrieved_user['email'] == email
    assert retrieved_user['user_id'] == created_user['user_id']

def test_get_nonexistent_user(user_service, clean_users_table):
    """Test retrieving a user that doesn't exist."""
    # Arrange
    nonexistent_id = uuid.uuid4()
    
    # Act
    user = user_service.get_user_by_id(nonexistent_id)
    
    # Assert
    assert user is None

def test_verify_password_success(user_service, clean_users_table):
    """Test successful password verification."""
    # Arrange
    username = "testuser"
    email = "test@example.com"
    password = "testpassword123"
    
    # Act
    user_service.create_user(username, email, password)
    verified_user = user_service.verify_password(username, password)
    
    # Assert
    assert verified_user is not None
    assert verified_user['username'] == username
    assert verified_user['email'] == email
    assert 'password_hash' not in verified_user

def test_verify_password_wrong_password(user_service, clean_users_table):
    """Test password verification with wrong password."""
    # Arrange
    username = "testuser"
    email = "test@example.com"
    password = "testpassword123"
    wrong_password = "wrongpassword"
    
    # Act
    user_service.create_user(username, email, password)
    verified_user = user_service.verify_password(username, wrong_password)
    
    # Assert
    assert verified_user is None

def test_verify_password_nonexistent_user(user_service, clean_users_table):
    """Test password verification for nonexistent user."""
    # Act
    verified_user = user_service.verify_password("nonexistent", "password123")
    
    # Assert
    assert verified_user is None 