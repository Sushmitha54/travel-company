import os
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, redirect, url_for, flash,
    request, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user, UserMixin
)
from flask_cors import CORS

# -------------------------
#  DATABASE INITIALIZATION
# -------------------------

db = SQLAlchemy()
login_manager = LoginManager()

# -------------------------
#        MODELS (MODEL B)
# -------------------------

# Many-to-Many table between users and rides
user_ride = db.Table(
    'user_ride',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('ride_id', db.Integer, db.ForeignKey('ride.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    # rides created by this user
    my_rides = db.relationship(
        'Ride',
        backref='driver',
        lazy=True,
        foreign_keys='Ride.driver_id'
    )

    # rides this user joined
    joined_rides = db.relationship(
        'Ride',
        secondary=user_ride,
        backref='joined_users',
        lazy=True
    )

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    destination = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    destination = db.Column(db.String(150), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    travel_time = db.Column(db.Time, nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')


# -------------------------
#         WTForms
# -------------------------

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    DateField, TimeField, IntegerField, SelectField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange
)


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=10, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RideForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    location = StringField('Location', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired(), Length(min=10, max=50)])
    submit = SubmitField('Create Ride')


class BookingForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=150)])
    location = SelectField(
        'Current Location/Station',
        choices=[
            ('', '-- Select Location --'),
            ('Central Station', 'Central Station'),
            ('North Station', 'North Station'),
            ('South Station', 'South Station'),
            ('East Station', 'East Station'),
            ('West Station', 'West Station'),
            ('Airport Terminal', 'Airport Terminal'),
            ('Bus Depot', 'Bus Depot'),
            ('Metro Station', 'Metro Station')
        ],
        validators=[DataRequired()]
    )
    destination = StringField('Destination', validators=[DataRequired(), Length(min=2, max=150)])
    travel_date = DateField('Date of Travel', validators=[DataRequired()])
    travel_time = TimeField('Time of Travel', validators=[DataRequired()])
    passengers = IntegerField('Number of Passengers', validators=[DataRequired(), NumberRange(min=1, max=8)])
    contact = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Book Ride')


# -------------------------
#        APP FACTORY
# -------------------------

def create_app(*args, **kwargs):
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Config
    app.config['SECRET_KEY'] = "super-secret-key"
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///travel.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    CORS(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    # -------------------------
    #          ROUTES
    # -------------------------

    @app.route('/')
    def index():
        form = RideForm()
        return render_template('index.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash("Email already registered", "warning")
                return redirect(url_for('register'))

            user = User(
                name=form.name.data,
                email=form.email.data,
                contact=form.contact.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for('login'))

        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password", "danger")

        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully.", "info")
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        my_rides = Ride.query.filter_by(driver_id=current_user.id).all()
        joined = current_user.joined_rides
        return render_template('dashboard.html', my_rides=my_rides, joined=joined)

    @app.route('/find_rides', methods=['GET', 'POST'])
    def find_rides():
        form = RideForm()
        rides = Ride.query

        if form.validate_on_submit():
            ride = Ride(
                driver_id=current_user.id if current_user.is_authenticated else None,
                name=form.name.data,
                location=form.location.data,
                destination=form.destination.data,
                contact=form.contact.data
            )
            db.session.add(ride)
            db.session.commit()
            flash("Ride posted successfully.", "success")
            return redirect(url_for('dashboard'))

        dest = request.args.get('destination')
        loc = request.args.get('location')
        if dest:
            rides = rides.filter(Ride.destination.ilike(f"%{dest}%"))
        if loc:
            rides = rides.filter(Ride.location.ilike(f"%{loc}%"))

        rides = rides.order_by(Ride.created_at.desc()).all()
        return render_template('find_rides.html', form=form, rides=rides)

    @app.route('/join', methods=['POST'])
    @login_required
    def join():
        data = request.form or request.json
        ride_id = data.get('ride_id')

        ride = Ride.query.get(ride_id)
        if ride and current_user not in ride.joined_users:
            ride.joined_users.append(current_user)
            db.session.commit()

        return jsonify({"success": True})

    @app.route('/book_ride', methods=['GET', 'POST'])
    def book_ride():
        form = BookingForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                booking = Booking(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    name=form.name.data,
                    location=form.location.data,
                    destination=form.destination.data,
                    travel_date=form.travel_date.data,
                    travel_time=form.travel_time.data,
                    passengers=form.passengers.data,
                    contact=form.contact.data
                )
                db.session.add(booking)
                db.session.commit()

                flash("Ride booked successfully!", "success")
                return jsonify({
                    'success': True,
                    'booking_id': booking.id
                })
            else:
                return jsonify({'success': False, 'message': 'Invalid form input'})

        return render_template('book_ride.html', form=form)

    @app.route('/booking_confirmation/<int:booking_id>')
    def booking_confirmation(booking_id):
        booking = Booking.query.get_or_404(booking_id)

        if current_user.is_authenticated and (
            booking.user_id == current_user.id or current_user.id == 1
        ):
            return render_template('booking_confirmation.html', booking=booking)

        flash("You do not have permission to view this booking.", "danger")
        return redirect(url_for('index'))

    @app.route('/my_bookings')
    @login_required
    def my_bookings():
        bookings = Booking.query.filter_by(
            user_id=current_user.id
        ).order_by(Booking.created_at.desc()).all()
        return render_template('my_bookings.html', bookings=bookings)

    @app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
    @login_required
    def cancel_booking(booking_id):
        booking = Booking.query.get_or_404(booking_id)

        if booking.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Permission denied'})

        booking_datetime = datetime.combine(
            booking.travel_date, booking.travel_time
        )
        time_diff = booking_datetime - datetime.now()

        if time_diff > timedelta(hours=2):
            booking.status = 'cancelled'
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'message': 'Cannot cancel within 2 hours of travel'
            })

    # ----- API ROUTES -----

    @app.route('/submit', methods=['POST'])
    def submit():
        data = request.json
        ride = Ride(
            name=data.get('name'),
            location=data.get('location'),
            destination=data.get('destination'),
            contact=data.get('contact')
        )
        db.session.add(ride)
        db.session.commit()
        return jsonify({"message": "Ride created successfully"})

    @app.route('/groups', methods=['GET'])
    def groups():
        rides = Ride.query.all()
        groups = {}

        for r in rides:
            if r.destination not in groups:
                groups[r.destination] = []

            groups[r.destination].append({
                "name": r.name,
                "location": r.location,
                "contact": r.contact
            })

        return jsonify(groups)

    # Simple test route for Gunicorn
    @app.route("/test")
    def test():
        return "App running successfully!"

    return app
