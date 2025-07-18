import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add project root to path
from app import create_app
from extensions import db
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session')
def app():
    app = create_app(testing=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def headers_for(app):
    def _headers(user_id=1, role='client'):
        with app.app_context():
            access_token = create_access_token(identity={"id": user_id, "role": role})
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    return _headers

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db
        db.session.rollback()
        db.drop_all()
        db.create_all()
