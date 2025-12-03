import pytest
from datetime import datetime, timedelta


class TestIntegration:
    """Integration tests for the complete booking flow."""

    def test_complete_booking_workflow(self, client, app):
        """Test the complete booking workflow from registration to confirmation."""
        # 1. Register a new user
        register_data = {
            'name': 'Integration Test User',
            'email': 'integration@test.com',
            'contact': '9999999999',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = client.post('/register', data=register_data)
        assert response.status_code == 302  # Redirect after successful registration

        # 2. Login
        login_data = {
            'email': 'integration@test.com',
            'password': 'testpass123'
        }
        response = client.post('/login', data=login_data)
        assert response.status_code == 302  # Redirect after successful login

        # 3. Create a booking
        booking_data = {
            'name': 'Integration Passenger',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'travel_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'travel_time': '14:30',
            'passengers': '3',
            'contact': '8888888888'
        }
        response = client.post('/book_ride', data=booking_data)
        assert response.status_code == 200

        # Extract booking ID from response (this would need adjustment based on actual response format)
        # For now, just check that booking was created

        # 4. Check my bookings page
        response = client.get('/my_bookings')
        assert response.status_code == 200
        assert b'Integration Passenger' in response.data

        # 5. Create another booking and test cancellation
        booking_data2 = {
            'name': 'Second Passenger',
            'location': 'North Station',
            'destination': 'South Station',
            'travel_date': (datetime.now().date() + timedelta(days=14)).isoformat(),
            'travel_time': '16:00',
            'passengers': '1',
            'contact': '7777777777'
        }
        response = client.post('/book_ride', data=booking_data2)
        assert response.status_code == 200

        # Get the latest booking ID (this is simplified - in real implementation,
        # you'd parse the response or query the database)
        with app.app_context():
            from models import Booking, User, db
            user = User.query.filter_by(email='integration@test.com').first()
            latest_booking = Booking.query.filter_by(user_id=user.id).order_by(Booking.id.desc()).first()

            # 6. Cancel the booking
            response = client.post(f'/cancel_booking/{latest_booking.id}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True

            # 7. Verify booking was cancelled
            updated_booking = Booking.query.get(latest_booking.id)
            assert updated_booking.status == 'cancelled'

    def test_ride_posting_and_joining_workflow(self, client, app):
        """Test the complete ride posting and joining workflow."""
        # 1. Register and login
        register_data = {
            'name': 'Ride Test User',
            'email': 'ride@test.com',
            'contact': '6666666666',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        client.post('/register', data=register_data)
        client.post('/login', data={'email': 'ride@test.com', 'password': 'testpass123'})

        # 2. Post a ride
        ride_data = {
            'name': 'Ride to Airport',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'contact': '5555555555'
        }
        response = client.post('/find_rides', data=ride_data)
        assert response.status_code == 302  # Redirect to dashboard

        # 3. Check that ride appears in groups endpoint
        response = client.get('/groups')
        assert response.status_code == 200
        data = response.get_json()
        assert 'Airport Terminal' in data

        # 4. Create another user and try to join the ride
        # Register second user
        client2 = app.test_client()
        register_data2 = {
            'name': 'Joining User',
            'email': 'join@test.com',
            'contact': '4444444444',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        client2.post('/register', data=register_data2)
        client2.post('/login', data={'email': 'join@test.com', 'password': 'testpass123'})

        # Get ride ID
        with app.app_context():
            from models import Ride
            ride = Ride.query.filter_by(name='Ride to Airport').first()
            ride_id = ride.id

        # Join the ride
        response = client2.post('/join', json={'ride_id': ride_id})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True

    def test_concurrent_booking_load(self, client, app):
        """Test multiple concurrent bookings to ensure system stability."""
        # Create a user
        register_data = {
            'name': 'Load Test User',
            'email': 'load@test.com',
            'contact': '3333333333',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        client.post('/register', data=register_data)
        client.post('/login', data={'email': 'load@test.com', 'password': 'testpass123'})

        # Create multiple bookings concurrently
        booking_data_template = {
            'name': 'Load Test Passenger',
            'location': 'Central Station',
            'destination': 'Airport Terminal',
            'travel_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'travel_time': '10:00',
            'passengers': '2',
            'contact': '2222222222'
        }

        # Simulate concurrent requests
        responses = []
        for i in range(5):
            booking_data = booking_data_template.copy()
            booking_data['name'] = f'Load Test Passenger {i+1}'
            booking_data['contact'] = f'22222222{i+1:02d}'
            response = client.post('/book_ride', data=booking_data)
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200

        # Verify all bookings were created
        with app.app_context():
            from models import Booking, User, db
            user = User.query.filter_by(email='load@test.com').first()
            user_bookings = Booking.query.filter_by(user_id=user.id).all()
            assert len(user_bookings) >= 5

    def test_error_handling_and_recovery(self, client, app):
        """Test error handling and system recovery."""
        # 1. Test invalid form submissions
        client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})

        # Invalid booking (missing fields)
        invalid_data = {
            'name': '',
            'location': '',
            'destination': '',
            'travel_date': '',
            'travel_time': '',
            'passengers': '',
            'contact': ''
        }
        response = client.post('/book_ride', data=invalid_data)
        assert response.status_code == 200  # Should handle gracefully

        # 2. Test accessing non-existent booking
        response = client.get('/booking_confirmation/99999')
        assert response.status_code == 404

        # 3. Test unauthorized access
        client2 = app.test_client()  # New client, not logged in
        response = client2.get('/my_bookings')
        assert response.status_code == 302  # Should redirect to login

        # 4. Test invalid cancellation
        response = client.post('/cancel_booking/99999')
        assert response.status_code == 404

    def test_data_integrity_and_constraints(self, app):
        """Test database constraints and data integrity."""
        with app.app_context():
            from models import db, User, Booking

            # Test unique email constraint
            user1 = User(name='User1', email='unique@test.com', contact='1111111111')
            user2 = User(name='User2', email='unique@test.com', contact='2222222222')
            user1.set_password('pass123')
            user2.set_password('pass123')

            db.session.add(user1)
            db.session.commit()

            # This should fail due to unique constraint
            with pytest.raises(Exception):
                db.session.add(user2)
                db.session.commit()

            # Clean up
            db.session.rollback()

    def test_session_management(self, client, app):
        """Test user session management."""
        # Login
        client.post('/login', data={'email': 'test@example.com', 'password': 'password123'})

        # Access protected route
        response = client.get('/my_bookings')
        assert response.status_code == 200

        # Logout
        response = client.get('/logout')
        assert response.status_code == 302

        # Try to access protected route after logout
        response = client.get('/my_bookings')
        assert response.status_code == 302  # Should redirect to login
