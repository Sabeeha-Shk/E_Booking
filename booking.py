from flask import Blueprint, render_template, request, redirect, url_for, session
from app import db  # Your main db instance
from models.booking import Booking  # Import the Booking model

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/booking', methods=['GET', 'POST'])
def book_ticket():
    # Ensure only logged-in users can book tickets
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        service = request.form['service']
        booking_date = request.form['booking_date']  # Expected as 'YYYY-MM-DD'
        number_of_tickets = int(request.form['number_of_tickets'])

        new_booking = Booking(
            user_id=session['user_id'],
            service=service,
            booking_date=booking_date,
            number_of_tickets=number_of_tickets
        )
        db.session.add(new_booking)
        db.session.commit()

        # After booking, redirect to home or a confirmation page
        return redirect(url_for('home'))

    return render_template('booking.html')
