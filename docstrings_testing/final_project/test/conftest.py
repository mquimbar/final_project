import pytest

from docstrings_testing.final_project.app_orig import create_app
from config import TestConfig
from db import db

@pytest.fixture(scope="function")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def session(app):
    with app.app_context():
        yield db.session