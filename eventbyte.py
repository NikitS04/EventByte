from flask import Flask
from models import db
from flask import render_template, redirect, url_for, flash, send_file, request, send_from_directory, make_response
from models import User, Event, Ticket, Transaction, db, tickets_allocated, tickets_allocated_user
from datetime import datetime, timedelta
import random, string, secrets
from barcode import Code128
from barcode.writer import ImageWriter, SVGWriter
from flask import send_file
from io import BytesIO
from flask_mail import Mail, Message
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Password'
app.config['MAIL_SUPPRESS_SEND'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'

mail = Mail(app)
#login_manager = LoginManager(app)
db.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize the database (create tables)
with app.app_context():
    # db.drop_all()
    db.create_all()
    #dbinit()



@app.route('/')
def index():
    return render_template('login.html')
    

@app.route('/templates/<filename>')
def template_filename(filename):
    return render_template(f'{filename}.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            new_transaction = Transaction(action=f'User Login {user.username}', event_id=1003, user_id=user.id)
            db.session.add(new_transaction)
            db.session.commit()
            login_user(user)
            return redirect(url_for('homepage'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    user_id = current_user.id
    user = User.query.get(user_id)
    new_transaction = Transaction(action=f'User Logout {user.username}', event_id=1004, user_id=user.id)
    db.session.add(new_transaction)
    db.session.commit()
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('login'))




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': # Create a new user using the form created in the HTML
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        is_first_user = db.session.query(User).count() == 0

        if len(password) < 8:
            flash(f'Password must be at least 8 characters long.')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already registered. Please use a different username.', 'danger')
            return redirect(url_for('register'))
        else:
            new_user = User(email=email, username=username, password=password)
            if is_first_user:
                new_user.is_superuser = True
            new_user.hash_password(password)
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id
            new_transaction = Transaction(action='User Registration', event_id=1000, user_id=user_id)
            db.session.add(new_transaction)
            db.session.commit()

            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/continue_as_guest')
def continue_as_guest():
    guest_user = {
        'id': None,
        'username': 'Guest',
        'is_superuser': False
    }

    return render_template('homepage.html', user=guest_user)


@app.route('/homepage')
def homepage():
    if current_user.is_authenticated:
        user_id = current_user.id
        user = User.query.get(user_id)
        return render_template('homepage.html', user=user)
    else:
        guest_user = {
            'id': None,
            'username': 'Guest',
            'is_superuser': False
        }
        return render_template('homepage.html', user=guest_user)
    
@app.route('/images/<filename>')
def images(filename):
    # Used to load all the images to show
    return send_from_directory('static', 'images/' + filename)

    
@app.route('/cancelled_events')
def cancelled_events():
    events = Event.query.filter_by(is_cancelled=True).all()
    if current_user.is_authenticated:
        user_id = current_user.id
        user = User.query.get(user_id)
        return render_template('cancelled_events.html', events=events, user=user)
    else:
        guest_user = {
            'id': None,
            'username': 'Guest',
            'is_superuser': False
        }
        return render_template('cancelled_events.html', events=events, user=guest_user)

@app.route('/addevent', methods=['GET', 'POST'])
@login_required
def addevent():
    user_id = current_user.id
    user = User.query.get(user_id)

    if user is None or not user.is_superuser:
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        # Create a new event using the form created in the HTML
        name = request.form.get('event_name')
        date_str = request.form.get('event_date')
        start_time_str = request.form.get('start_time')
        duration = request.form.get('duration')
        capacity = request.form.get('capacity')
        location = request.form.get('location')

        if int(duration) > 720:
            flash('Events cannot go on for longer than 12 hours (720 minutes)')
            return redirect(url_for('addevent'))
        
        if int(capacity) > 10000:
            flash('Events cannot have a capacity greater than 10000 people')
            return redirect(url_for('addevent'))
        
        if int(capacity) <=0:
            flash('Events cannot have a capacity of 0 or less people')
            return redirect(url_for('addevent'))


        if int(duration) <=0:
            flash('Events cannot be less than 1 minute long')
            return redirect(url_for('addevent'))
        
        # Convert date and start time string to Python date object as it wasnt adding correctly to database before
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()

        # Adds a new event to the database

        new_event = Event(name=name,date=date,start_time=start_time,duration=duration,capacity=capacity,location=location)
        db.session.add(new_event)
        db.session.commit()

        # Adds a new transaction to the database

        new_transaction = Transaction(action='Event Created', event_id=new_event.id, user_id=user_id)
        db.session.add(new_transaction)
        db.session.commit()

        flash('Event created successfully!')
        return redirect(url_for('addevent'))
        
    return render_template('addevent.html', user=user, is_superuser=True)

@app.route('/viewallevents')
def viewallevents():
    events = Event.query.all()
    if current_user.is_authenticated:
        user_id = current_user.id
        user = User.query.get(user_id)
        return render_template('viewallevents.html', events=events, user=user, tickets_allocated=tickets_allocated, tickets_allocated_user=tickets_allocated_user)
    else: # Creates a guest account which can be checked in HTML to show the correct features
        guest_user = {
            'id': None,
            'username': 'Guest',
            'is_superuser': False
        }
        return render_template('viewallevents.html', events=events, user=guest_user, tickets_allocated=tickets_allocated)



@app.route('/remove_event/<int:event_id>', methods=['POST'])
@login_required
def remove_event(event_id):
    user_id = current_user.id
    user = User.query.get(user_id)

    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('viewallevents'))

    # Send an email to all ticket holders and set the ticket to cancelled
    tickets = Ticket.query.filter_by(event_id=event.id).all()
    for ticket in tickets:
        if ticket.is_cancelled == False:
            user_email = ticket.user.email
            subject = 'Event Cancellation: ' + event.name
            body = f'The event "{event.name}" has been canceled. So your ticket has been cancelled, we apologize for any inconvenience.'
            sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
            mail.send_message(sender=("NOREPLY",sender),subject=subject,body=body,recipients=[user_email])
        ticket.is_cancelled = True
        db.session.add(ticket)


    # Remove the event itself
    event.is_cancelled = True
    db.session.add(event)
    db.session.commit()

    # Adds a new event to the database

    new_transaction = Transaction(action='Event Deleted', event_id=event.id, user_id=user_id)
    db.session.add(new_transaction)
    db.session.commit()
    return redirect(url_for('viewallevents'))

@app.route('/modify_capacity/<int:event_id>', methods=['POST'])
@login_required
def modify_capacity(event_id):
    new_capacity = int(request.form.get('new_capacity'))
    user_id = current_user.id
    user = User.query.get(user_id)

    # Retrieve the event
    event = Event.query.get(event_id)

    if new_capacity > 10000:
            flash('Events cannot have a capacity greater than 10000 people')
            return redirect(url_for('addevent'))
    
    if new_capacity <= 0:
            flash('Events cannot have a capacity of 0 or less')
            return redirect(url_for('addevent'))


    if not event:
        return redirect(url_for('viewallevents'))

    tickets_allocated = Ticket.query.filter_by(event_id=event_id).count()

    if tickets_allocated > new_capacity:
        return redirect(url_for('viewallevents'))

    # Update the event's capacity
    event.capacity = new_capacity
    db.session.commit()

   # Adds a new transaction to db
    new_transaction = Transaction(action='Event Capacity Modified', event_id=event.id, user_id=user_id)
    db.session.add(new_transaction)
    db.session.commit()

    flash('Capacity modified successfully!', 'success')
    return redirect(url_for('viewallevents'))



def check_capacity_and_notify(event):
    tickets = Ticket.query.filter_by(event_id=event.id, is_cancelled=False).all()
    remaining_capacity = event.capacity - len(tickets)

    if remaining_capacity / event.capacity < 0.05:
        # Send an email to the superuser
        send_low_capacity_notification(event)

def send_low_capacity_notification(event):
    # Create the email message
    subject = 'Low Capacity Warning'
    body = f'The remaining capacity for the event "{event.name}" is less than 5%. Please take action.'
    sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
    user = User.query.filter_by(is_superuser=True).first()
    user_email = user.email
    # Send the email to the superuser
    mail.send_message(sender=("NOREPLY",sender),subject=subject,body=body,recipients=[user_email])



@app.route('/get_ticket/<int:event_id>', methods=['POST'])
@login_required
def get_ticket(event_id):
    user_id = current_user.id
    event = Event.query.get(event_id)
    user = User.query.get(user_id)

    if not event:
        return redirect(url_for('viewallevents'))

    tickets_allocated = Ticket.query.filter_by(event_id=event_id, is_cancelled=False).count()
    tickets = Ticket.query.filter_by(user_id=user_id, is_cancelled=False).all()

    if tickets_allocated >= event.capacity:
        return redirect(url_for('viewallevents'))
    
    # Creates a random unique ticket value which is also used in the barcode
    ticket_value = random.randint(1, 10000)
    while Ticket.query.filter_by(ticket_value=ticket_value).first():
        ticket_value = random.randint(1, 10000)


    new_ticket = Ticket(user_id=user_id, event_id=event.id, ticket_value=ticket_value)
    db.session.add(new_ticket)
    db.session.commit()

    
    new_transaction = Transaction(action=f'Ticket Allocated: {event.name}', event_id=event.id, user_id=user_id)
    db.session.add(new_transaction)
    db.session.commit()

    # Sends a booking confirmation email
    subject = 'Ticket Booked :' + event.name
    body = f'Thanks for booking a ticket for "{event.name}" You can cancel the event at any time.'
    email = current_user.email
    sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
    mail.send_message(sender=("NOREPLY",sender),subject=subject,body=body,recipients=[email])


    barcodeData=f'TicketID: {new_ticket.id}'
    barcodeImage = Code128(barcodeData, writer=SVGWriter())
    svgData = barcodeImage.render().decode()


    check_capacity_and_notify(event)

    flash('Ticket Allocated Successfully!', 'success')
    return redirect(url_for('mytickets', svgData=svgData, tickets=tickets, user=user))

@app.route('/cancel_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def cancel_ticket(ticket_id):
    user_id = current_user.id
    user = User.query.get(user_id)
    # Retrieve the ticket
    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('viewallevents'))

    # Cancel the ticket in the database
    ticket.is_cancelled = True
    db.session.commit()

    #Adds a transaction for ticket cancellation
    user_id = current_user.id
    event_name = ticket.event.name
    new_transaction = Transaction(action=f'Ticket Cancellation: {event_name}', event_id=ticket.event.id, user_id=user_id)
    db.session.add(new_transaction)
    db.session.commit()

    # Send a cancellation email to the user
    user_email = ticket.user.email
    event_name = ticket.event.name
    send_cancelation_email(user_email, event_name)

    flash('Ticket canceled successfully.', 'success')
    return redirect(url_for('mytickets'))

def send_cancelation_email(user_email, event_name):
    subject = f'Ticket Cancellation: {event_name}'
    body = f'Your ticket for the event "{event_name}" has been canceled. We apologize for any inconvenience.'
    sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
    # Send the email
    mail.send_message(sender=("NOREPLY",sender),subject=subject,body=body,recipients=[user_email])
    # msg = Message(subject, recipients=[user_email], body=body, sender=sender)
    # mail.send(msg)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user_id = current_user.id
    user = User.query.get(user_id)

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        check_new_password = request.form.get('check_new_password')

        if len(new_password) < 8:
            flash(f'Password must be at least 8 characters long.')
            return redirect(url_for('change_password'))

        # Verify current password
        if not current_user.check_password(current_password):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('change_password'))
        
        if check_new_password!=new_password:
            flash('The two passwords you entered werent the same', 'danger')
            return redirect(url_for('change_password'))

        # Update the password
        current_user.hash_password(new_password)
        db.session.commit()
        new_transaction = Transaction(action='Password Change', event_id=1001, user_id=user_id)
        db.session.add(new_transaction)
        db.session.commit()
        return redirect(url_for('homepage'))  # Redirect to the user's profile or another page

    return render_template('change_password.html', user=user)


@app.route('/mytickets')
@login_required
def mytickets():
    user_id = current_user.id
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    tickets = Ticket.query.filter_by(user_id=user.id).all()
    return render_template('mytickets.html', user=user, tickets=tickets)


@app.route('/transaction_log')
@login_required
def transaction_log():
    user_id = current_user.id
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    if current_user.is_superuser:
        transactions = Transaction.query.all()
        return render_template('transaction_log.html' , user=user, transactions=transactions)


@app.route('/barcode/<int:ticket_id>')
@login_required
def barcode(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    user_id = current_user.id
    user = User.query.get(user_id)

    if ticket is None:
        return 'Ticket not found', 404
    
    # Used to dynamically create a barcode
    barcodeData=f'TicketID: {ticket.ticket_value}'
    barcodeImage = Code128(barcodeData, writer=SVGWriter())
    svgData = barcodeImage.render().decode()

    return render_template('ticket_barcode.html', svgData=svgData, ticket=ticket, user=user)


def send_reset_email(email, token):
    reset_link = url_for('reset_password', token=token, _external=True)
    subject = 'Password Reset Request'
    body = f'Click the following link to reset your password: {reset_link}'
    sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
    mail.send_message(sender=("NOREPLY",sender),subject=subject,body=body,recipients=[email])
    # msg = Message(subject, recipients=[email], body=body, sender=sender)
    # mail.send(msg)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        # Used to create a unique link which has an expiration and is added to the database
        if user:
            user.reset_token = secrets.token_urlsafe(32)
            user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            send_reset_email(user.email, user.reset_token)

            flash('Check your email for instructions on resetting your password.')
            return redirect(url_for('login'))

        flash('No user found with that email address.')

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user and user.reset_token_expiration > datetime.utcnow(): # Used to check that expiration time hasnt passed
        flash('Invalid or expired reset token.')
        return redirect(url_for('login'))


    if not user:
        flash('User not found.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')

        if len(new_password) <= 8:
            flash('Password must be at least 8 characters long.')
            return redirect(url_for('reset_password', token=token))
        
        # Adds the new password to be stored in the db

        user.hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()

        flash('Your password has been successfully reset.')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


if __name__ == '__main__':
    app.run(debug=True)
