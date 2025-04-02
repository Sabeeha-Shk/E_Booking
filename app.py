import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Flask App Configuration
app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sql-404@localhost/e_booking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Database Setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# User Model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))


# Booking Model
class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(50), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", backref="bookings")


# User Booking Model (For storing entered booking details)
class UserBooking(db.Model):
    __tablename__ = "user_bookings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    booking_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Homepage Route
@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('home.html', user=user)
    return redirect(url_for('login'))


# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    today = datetime.today().date()

    upcoming_bookings = Booking.query.filter(
        Booking.user_id == user.id, Booking.date >= today
    ).all()

    past_bookings = Booking.query.filter(
        Booking.user_id == user.id, Booking.date < today
    ).all()

    return render_template('dashboard.html', user=user, upcoming_bookings=upcoming_bookings,
                           past_bookings=past_bookings)


# Booking Page Route (Handles User Booking Data)
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        booking_type = request.form.get('booking_type')
        details = request.form.get('details')
        price = request.form.get('price')

        new_booking = UserBooking(
            name=name,
            email=email,
            phone_number=phone,
            booking_type=booking_type,
            details=details,
            price=price
        )
        db.session.add(new_booking)
        db.session.commit()

        flash("Booking confirmed successfully!", "success")
        return redirect(url_for('payment'))

    # Handling GET request for pre-filled booking details
    name = request.args.get('name', '')
    time = request.args.get('time', '')
    price = request.args.get('price', '')
    booking_type = request.args.get('type', '')

    return render_template('booking.html', name=name, time=time, price=price, booking_type=booking_type)


# Payment Page Route
@app.route('/payment', methods=['GET'])
def payment():
    name = request.args.get('name', '')
    email = request.args.get('email', '')
    phone = request.args.get('phone', '')
    price = request.args.get('price', '')
    return render_template('payment.html', name=name, email=email, phone=phone, price=price)



# Profile Route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    user = User.query.get(user_id)
    success_message = None

    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']

        if user:
            user.name = full_name
            user.email = email
            user.phone_number = phone_number
            db.session.commit()
            success_message = "Profile updated successfully!"

    return render_template('profile.html', user=user, success_message=success_message)


# Travel Page Route
@app.route('/travel')
def travel():
    return render_template('travel.html')


# Movies Page Route
@app.route('/movies')
def movies():
    return render_template('movies.html')


# Events Page Route
@app.route('/events')
def events():
    return render_template('events.html')


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            return "Email already registered!"

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials"
    return render_template('login.html')

@app.route('/home')
def go_home():
    return render_template('home.html')

@app.route('/book')
def book():
    travel_type = request.args.get('travel_type', 'unknown')
    return render_template('booking.html', travel_type=travel_type)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080)) # Railway provides a PORT
    app.run(host="0.0.0.0", port=port, debug=False)