import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import RegisterForm, LoginForm, RideForm
from models import db, User, Ride
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me-secret')
    database_url = os.getenv("DATABASE_URL", "sqlite:///instance/app.db")
    # If using Heroku/Render style DATABASE_URL that starts with postgres:// convert to postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_first_request
    def create_tables():
        db.create_all()

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
            user = User(name=form.name.data, email=form.email.data, contact=form.contact.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.", "success")
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
                flash("Logged in successfully.", "success")
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            flash("Invalid email or password", "danger")
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
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
            # create a ride
            ride = Ride(driver_id=current_user.id if current_user.is_authenticated else None,
                        name=form.name.data,
                        location=form.location.data,
                        destination=form.destination.data,
                        contact=form.contact.data)
            db.session.add(ride)
            db.session.commit()
            flash("Ride created successfully.", "success")
            return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('index'))
        # filtering by destination/location if provided in GET params
        dest = request.args.get('destination')
        loc = request.args.get('location')
        if dest:
            rides = rides.filter(Ride.destination.ilike(f"%{dest}%"))
        if loc:
            rides = rides.filter(Ride.location.ilike(f"%{loc}%"))
        rides = rides.order_by(Ride.created_at.desc()).all()
        return render_template('find_rides.html', form=form, rides=rides)

    return app

if __name__ == "__main__":
    app = create_app()
