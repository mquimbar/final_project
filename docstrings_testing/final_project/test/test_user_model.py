import pytest

from models.user_model import Users
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user_model import Users
#from clients.mongo_client import sessions_collection
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#def create_app(config_name="default"):
#    app = Flask(__name__)
#    app.config.from_object(config_by_name[config_name])
#    db.init_app(app)  # Initialize the SQLAlchemy extension with the app
#    return app

from pymongo import MongoClient

#@pytest.fixture(scope="module")
#def session():
#    """Fixture to provide a database session."""
#    # Create an in-memory SQLite database for testing
#    engine = create_engine("sqlite:///:memory:")
#    Base.metadata.create_all(engine)  # Create tables from models

    # Create a session factory and a session
#    Session = sessionmaker(bind=engine)
#    session = Session()

    # Yield session to the test functions
#    yield session

    # Clean up after tests
#    session.close()

@pytest.fixture(scope="module")
def session():
    """Fixture for providing a MongoDB client or session."""
    client = MongoClient("mongodb://localhost:27017")
    db = client.test_database  # Use your actual database name
    yield db  # Provide the database to the tests

    client.close()


@pytest.fixture
def sample_user():
    return {
        "username": "testuser",
        "password": "securepassword123"
    }


##########################################################
# User Creation
##########################################################

def test_create_user(session, sample_user):
    """Test creating a new user with a unique username."""
    Users.create_user(**sample_user)
    user = session.query(Users).filter_by(username=sample_user["username"]).first()
    assert user is not None, "User should be created in the database."
    assert user.username == sample_user["username"], "Username should match the input."
    assert len(user.salt) == 32, "Salt should be 32 characters (hex)."
    assert len(user.password) == 64, "Password should be a 64-character SHA-256 hash."

def test_create_duplicate_user(session, sample_user):
    """Test attempting to create a user with a duplicate username."""
    Users.create_user(**sample_user)
    with pytest.raises(ValueError, match="User with username 'testuser' already exists"):
        Users.create_user(**sample_user)

##########################################################
# User Authentication
##########################################################

def test_check_password_correct(session, sample_user):
    """Test checking the correct password."""
    Users.create_user(**sample_user)
    assert Users.check_password(sample_user["username"], sample_user["password"]) is True, "Password should match."

def test_check_password_incorrect(session, sample_user):
    """Test checking an incorrect password."""
    Users.create_user(**sample_user)
    assert Users.check_password(sample_user["username"], "wrongpassword") is False, "Password should not match."

def test_check_password_user_not_found(session):
    """Test checking password for a non-existent user."""
    with pytest.raises(ValueError, match="User nonexistentuser not found"):
        Users.check_password("nonexistentuser", "password")

##########################################################
# Update Password
##########################################################

def test_update_password(session, sample_user):
    """Test updating the password for an existing user."""
    Users.create_user(**sample_user)
    new_password = "newpassword456"
    Users.update_password(sample_user["username"], new_password)
    assert Users.check_password(sample_user["username"], new_password) is True, "Password should be updated successfully."

def test_update_password_user_not_found(session):
    """Test updating the password for a non-existent user."""
    with pytest.raises(ValueError, match="User nonexistentuser not found"):
        Users.update_password("nonexistentuser", "newpassword")


##########################################################
# Delete User
##########################################################

def test_delete_user(session, sample_user):
    """Test deleting an existing user."""
    Users.create_user(**sample_user)
    Users.delete_user(sample_user["username"])
    user = session.query(Users).filter_by(username=sample_user["username"]).first()
    assert user is None, "User should be deleted from the database."

def test_delete_user_not_found(session):
    """Test deleting a non-existent user."""
    with pytest.raises(ValueError, match="User nonexistentuser not found"):
        Users.delete_user("nonexistentuser")

##########################################################
# Get User
##########################################################

def test_get_id_by_username(session, sample_user):
    """
    Test successfully retrieving a user's ID by their username.
    """
    # Create a user in the database
    Users.create_user(**sample_user)

    # Retrieve the user ID
    user_id = Users.get_id_by_username(sample_user["username"])

    # Verify the ID is correct
    user = session.query(Users).filter_by(username=sample_user["username"]).first()
    assert user is not None, "User should exist in the database."
    assert user.id == user_id, "Retrieved ID should match the user's ID."


def test_get_id_by_username_user_not_found(session):
    """
    Test failure when retrieving a non-existent user's ID by their username.
    """
    with pytest.raises(ValueError, match="User nonexistentuser not found"):
        Users.get_id_by_username("nonexistentuser")