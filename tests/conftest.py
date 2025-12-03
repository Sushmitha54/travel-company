import pytest
import os
import tempfile
from datetime import datetime, timedelta

from app import create_app
from models import db, User, Ride, Booking


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'MAIL_SUPPRESS_SEND': True,  # Suppress email sending in tests
    })

    with app.app_context():
        db.create_all()
        yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            name='Test User',
            email='test@example.com',
            contact='1234567890'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    # Log in the test user
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': False
    })
    return client


@pytest.fixture
def test_booking(app, test_user):
    """Create a test booking."""
    with app.app_context():
        booking = Booking(
            user_id=test_user.id,
            name='Test Passenger',
            location='Central Station',
            destination='Airport',
            travel_date=datetime.now().date() + timedelta(days=7),
            travel_time=datetime.now().time(),
            passengers=2,
            contact='9876543210'
        )
        db.session.add(booking)
        db.session.commit()
        return booking


@pytest.fixture
def test_ride(app, test_user):
    """Create a test ride."""
    with app.app_context():
        ride = Ride(
            driver_id=test_user.id,
            name='Test Ride',
            location='Central Station',
            destination='Airport',
            contact='1234567890'
        )
        db.session.add(ride)
        db.session.commit()
        return ride
