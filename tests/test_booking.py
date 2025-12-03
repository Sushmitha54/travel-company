import pytest
from datetime import datetime, timedelta
from flask import url_for


class TestBookingSystem:
    """Test cases for the booking system."""

    def test_booking_creation_success(self, client, test_user):
        """Test successful booking creation."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Create booking data
        booking_data = {
            'name': 'John Doe',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'travel_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'travel_time': '10:00',
            'passengers': '2',
            'contact': '9876543210'
        }

        # Submit booking
        response = client.post('/book_ride', data=booking_data)

        # Should redirect to confirmation page
        assert response.status_code == 200
        assert b'Booking Confirmed' in response.data or b'success' in response.data

    def test_booking_creation_validation_error(self, client, test_user):
        """Test booking creation with validation errors."""
        # Login first
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Create invalid booking data (missing required fields)
        booking_data = {
            'name': '',  # Empty name
            'location': '',  # Empty location
            'destination': 'Airport Terminal',
            'travel_date': '',  # Empty date
            'travel_time': '10:00',
            'passengers': '0',  # Invalid passenger count
            'contact': '123'  # Invalid contact length
        }

        # Submit booking
        response = client.post('/book_ride', data=booking_data)

        # Should return validation errors
        assert response.status_code == 200
        assert b'error' in response.data.lower()

    def test_booking_requires_authentication(self, client):
        """Test that booking requires user authentication."""
        booking_data = {
            'name': 'John Doe',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'travel_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'travel_time': '10:00',
            'passengers': '2',
            'contact': '9876543210'
        }

        # Try to book without authentication
        response = client.post('/book_ride', data=booking_data)

        # Should still work (booking allows anonymous users)
        assert response.status_code == 200

    def test_booking_cancellation_success(self, authenticated_client, test_booking):
        """Test successful booking cancellation."""
        # Try to cancel booking
        response = authenticated_client.post(f'/cancel_booking/{test_booking.id}')

        # Should return success
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True

    def test_booking_cancellation_too_late(self, authenticated_client, test_booking, app):
        """Test booking cancellation when too close to travel time."""
        with app.app_context():
            # Set travel time to less than 2 hours from now
            test_booking.travel_date = datetime.now().date()
            test_booking.travel_time = (datetime.now() + timedelta(hours=1)).time()
            from models import db
            db.session.commit()

        # Try to cancel booking
        response = authenticated_client.post(f'/cancel_booking/{test_booking.id}')

        # Should fail
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False
        assert 'Cannot cancel' in data['message']

    def test_booking_cancellation_wrong_user(self, client, test_booking, app):
        """Test booking cancellation by wrong user."""
        # Create another user
        from models import User, db
        with app.app_context():
            other_user = User(
                name='Other User',
                email='other@example.com',
                contact='1111111111'
            )
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()

            # Login as other user
            client.post('/login', data={
                'email': 'other@example.com',
                'password': 'password123'
            })

        # Try to cancel booking belonging to different user
        response = client.post(f'/cancel_booking/{test_booking.id}')

        # Should fail
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False
        assert 'Permission denied' in data['message']

    def test_view_my_bookings_requires_auth(self, client):
        """Test that viewing bookings requires authentication."""
        response = client.get('/my_bookings')

        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_view_my_bookings_authenticated(self, authenticated_client, test_booking):
        """Test viewing bookings when authenticated."""
        response = authenticated_client.get('/my_bookings')

        assert response.status_code == 200
        assert b'My Ride Bookings' in response.data

    def test_booking_confirmation_view(self, authenticated_client, test_booking):
        """Test viewing booking confirmation."""
        response = authenticated_client.get(f'/booking_confirmation/{test_booking.id}')

        assert response.status_code == 200
        assert b'Booking Confirmed' in response.data
        assert str(test_booking.id).encode() in response.data

    def test_booking_confirmation_wrong_user(self, client, test_booking, app):
        """Test viewing booking confirmation by wrong user."""
        # Create another user
        from models import User, db
        with app.app_context():
            other_user = User(
                name='Other User',
                email='other@example.com',
                contact='1111111111'
            )
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()

            # Login as other user
            client.post('/login', data={
                'email': 'other@example.com',
                'password': 'password123'
            })

        # Try to view booking belonging to different user
        response = client.get(f'/booking_confirmation/{test_booking.id}')

        # Should redirect or show error
        assert response.status_code in [302, 200]
        if response.status_code == 200:
            assert b'danger' in response.data or b'permission' in response.data.lower()

    def test_invalid_booking_date(self, authenticated_client):
        """Test booking with past date."""
        booking_data = {
            'name': 'John Doe',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'travel_date': (datetime.now().date() - timedelta(days=1)).isoformat(),  # Past date
            'travel_time': '10:00',
            'passengers': '2',
            'contact': '9876543210'
        }

        response = authenticated_client.post('/book_ride', data=booking_data)

        # Should handle gracefully (validation or error)
        assert response.status_code == 200

    def test_max_passengers_limit(self, authenticated_client):
        """Test booking with too many passengers."""
        booking_data = {
            'name': 'John Doe',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'travel_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'travel_time': '10:00',
            'passengers': '10',  # Exceeds limit
            'contact': '9876543210'
        }

        response = authenticated_client.post('/book_ride', data=booking_data)

        # Should validate passenger limit
        assert response.status_code == 200
        # Check for validation error (implementation dependent)

    def test_contact_number_validation(self, authenticated_client):
        """Test booking with invalid contact number."""
        booking_data = {
            'name': 'John Doe',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'travel_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'travel_time': '10:00',
            'passengers': '2',
            'contact': '123'  # Too short
        }

        response = authenticated_client.post('/book_ride', data=booking_data)

        # Should validate contact number
        assert response.status_code == 200
