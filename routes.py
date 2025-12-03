from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from models_fixed import db, User, Ride, Booking
from forms import RegisterForm, LoginForm, RideForm, BookingForm
from datetime import datetime, timedelta

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    form = RideForm()
    return render_template('index.html', form=form)

@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered", "warning")
            return redirect(url_for('main.register'))
        user = User(username=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # Note: In production, use password hashing
            login_user(user, remember=form.remember.data)
            flash("Logged in successfully.", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash("Invalid email or password", "danger")
    return render_template('login.html', form=form)

@main_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))

@main_routes.route('/dashboard')
@login_required
def dashboard():
    # Get user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', bookings=bookings)

@main_routes.route('/find_rides', methods=['GET', 'POST'])
def find_rides():
    form = RideForm()
    rides = Ride.query
    if form.validate_on_submit():
        # Create a ride
        ride = Ride(
            origin=form.location.data,
            destination=form.destination.data,
            date=datetime.combine(form.travel_date.data, form.travel_time.data) if hasattr(form, 'travel_date') else datetime.now()
        )
        db.session.add(ride)
        db.session.commit()
        flash("Ride created successfully.", "success")
        return redirect(url_for('main.dashboard') if current_user.is_authenticated else url_for('main.index'))

    # Filtering by destination/location if provided in GET params
    dest = request.args.get('destination')
    loc = request.args.get('location')
    if dest:
        rides = rides.filter(Ride.destination.ilike(f"%{dest}%"))
    if loc:
        rides = rides.filter(Ride.origin.ilike(f"%{loc}%"))

    rides = rides.order_by(Ride.date.desc()).all()
    return render_template('find_rides.html', form=form, rides=rides)

@main_routes.route('/book_ride', methods=['GET', 'POST'])
def book_ride():
    form = BookingForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            booking = Booking(
                user_id=current_user.id if current_user.is_authenticated else None,
                ride_id=request.form.get('ride_id', 1),  # Default to first ride, adjust as needed
                status='Pending'
            )
            db.session.add(booking)
            db.session.commit()

            flash("Your ride has been booked successfully!", "success")
            return jsonify({
                'success': True,
                'message': 'Ride booked successfully!',
                'booking_id': booking.id
            })
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field.title()}: {error}")
            return jsonify({
                'success': False,
                'message': 'Please correct the following errors: ' + ', '.join(errors)
            })
    return render_template('book_ride.html', form=form)

@main_routes.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.timestamp.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)

@main_routes.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'})

    # Only allow cancellation if more than 2 hours away
    if booking.ride and booking.ride.date > datetime.now() + timedelta(hours=2):
        booking.status = 'Cancelled'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    else:
        return jsonify({'success': False, 'message': 'Cannot cancel booking less than 2 hours before travel'})

@main_routes.route('/booking_confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    # Check if user owns this booking or is admin
    if current_user.is_authenticated and (booking.user_id == current_user.id or current_user.id == 1):
        return render_template('booking_confirmation.html', booking=booking)
    elif not current_user.is_authenticated and booking.user_id is None:
        return render_template('booking_confirmation.html', booking=booking)
    else:
        flash("You don't have permission to view this booking.", "danger")
        return redirect(url_for('main.index'))

@main_routes.route('/join', methods=['POST'])
@login_required
def join():
    data = request.form or request.json
    ride_id = data.get('ride_id')
    ride = Ride.query.get(ride_id)
    if ride:
        # Create booking for this user and ride
        booking = Booking(user_id=current_user.id, ride_id=ride.id, status='Joined')
        db.session.add(booking)
        db.session.commit()
        return jsonify({"success": True, "message": "Successfully joined the ride"})
    return jsonify({"success": False, "message": "Ride not found"})

@main_routes.route('/groups')
def groups():
    rides = Ride.query.all()
    groups = {}
    for ride in rides:
        dest = ride.destination
        if dest not in groups:
            groups[dest] = []
        groups[dest].append({
            "id": ride.id,
            "origin": ride.origin,
            "destination": ride.destination,
            "date": ride.date.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(groups)

@main_routes.route('/submit', methods=['POST'])
def submit():
    data = request.json
    ride = Ride(
        origin=data.get('location'),
        destination=data.get('destination'),
        date=datetime.now()  # Adjust as needed
    )
    db.session.add(ride)
    db.session.commit()
    return jsonify({"message": "Ride created successfully"})
