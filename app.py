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


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app


# Create the app instance for Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
