from flask import render_template, current_app
from flask_mail import Mail, Message
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with the app."""
    mail.init_app(app)

def send_booking_confirmation_email(booking):
    """Send booking confirmation email to user."""
    try:
        subject = f"Booking Confirmed - Travel Company #{booking.id}"

        # Render HTML template
        html_body = render_template(
            'emails/booking_confirmation.html',
            booking=booking
        )

        # Create message
        msg = Message(
            subject=subject,
            recipients=[booking.contact if '@' in booking.contact else f"{booking.contact}@temp.com"],  # For demo purposes
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # Send email
        mail.send(msg)
        current_app.logger.info(f"Booking confirmation email sent for booking {booking.id}")

    except Exception as e:
        current_app.logger.error(f"Failed to send booking confirmation email: {str(e)}")
        # Don't raise exception to avoid breaking the booking flow

def send_booking_cancellation_email(booking):
    """Send booking cancellation email to user."""
    try:
        subject = f"Booking Cancelled - Travel Company #{booking.id}"

        # Render HTML template
        html_body = render_template(
            'emails/booking_cancellation.html',
            booking=booking
        )

        # Create message
        msg = Message(
            subject=subject,
            recipients=[booking.contact if '@' in booking.contact else f"{booking.contact}@temp.com"],  # For demo purposes
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # Send email
        mail.send(msg)
        current_app.logger.info(f"Booking cancellation email sent for booking {booking.id}")

    except Exception as e:
        current_app.logger.error(f"Failed to send booking cancellation email: {str(e)}")

def send_admin_booking_notification(booking):
    """Send booking notification to admin."""
    try:
        subject = f"New Booking Received - Travel Company #{booking.id}"

        # Render HTML template
        html_body = render_template(
            'emails/admin_booking_notification.html',
            booking=booking
        )

        # Create message
        msg = Message(
            subject=subject,
            recipients=[current_app.config['ADMIN_EMAIL']],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # Send email
        mail.send(msg)
        current_app.logger.info(f"Admin booking notification sent for booking {booking.id}")

    except Exception as e:
        current_app.logger.error(f"Failed to send admin booking notification: {str(e)}")

def send_registration_welcome_email(user):
    """Send welcome email to new user."""
    try:
        subject = "Welcome to Travel Company!"

        # Render HTML template
        html_body = render_template(
            'emails/welcome.html',
            user=user
        )

        # Create message
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # Send email
        mail.send(msg)
        current_app.logger.info(f"Welcome email sent to user {user.email}")

    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email: {str(e)}")

def send_payment_success_email(booking, payment_details):
    """Send payment success email."""
    try:
        subject = f"Payment Successful - Travel Company #{booking.id}"

        # Render HTML template
        html_body = render_template(
            'emails/payment_success.html',
            booking=booking,
            payment_details=payment_details
        )

        # Create message
        msg = Message(
            subject=subject,
            recipients=[booking.contact if '@' in booking.contact else f"{booking.contact}@temp.com"],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # Send email
        mail.send(msg)
        current_app.logger.info(f"Payment success email sent for booking {booking.id}")

    except Exception as e:
        current_app.logger.error(f"Failed to send payment success email: {str(e)}")

def send_ride_join_notification(ride, joining_user):
    """Send notification when someone joins a ride."""
    try:
        subject = f"New Passenger Joined Your Ride - Travel Company"

        # Render HTML template
        html_body = render_template(
            'emails/ride_join_notification.html',
            ride=ride,
            joining_user=joining_user
        )

        # Create message
        msg = Message(
            subject=subject,
            recipients=[ride.driver.email],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        # Send email
        mail.send(msg)
        current_app.logger.info(f"Ride join notification sent for ride {ride.id}")

    except Exception as e:
        current_app.logger.error(f"Failed to send ride join notification: {str(e)}")
