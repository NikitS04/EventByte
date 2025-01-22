# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(256))
    reset_token_expiration = db.Column(db.DateTime) 
    tickets = db.relationship('Ticket', backref='user', lazy=True)

    def __init__(self, email, username, password, is_superuser=False):
        self.email = email
        self.username = username
        self.is_superuser = is_superuser
        self.hash_password(password)
        self.reset_token = None
        self.reset_token_expiration = None

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    is_cancelled = db.Column(db.Boolean, default=False)
    tickets = db.relationship('Ticket', backref='event', lazy=True)

    def __init__(self, name, date, start_time, duration, capacity, location):
        self.name = name
        self.date = date
        self.start_time = start_time
        self.duration = duration
        self.capacity = capacity
        self.location = location

class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    ticket_value = db.Column(db.Integer, unique=True, nullable=False)
    is_cancelled = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, event_id, ticket_value):
        self.user_id = user_id
        self.event_id = event_id
        self.ticket_value = ticket_value
    
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50), nullable=False)  # e.g., 'Event Created', 'Ticket Allocated', 'Event Cancelled'

    def __init__(self, action, event_id, user_id):
        self.action = action
        self.event_id = event_id
        self.user_id = user_id


# def dbinit():
#     # super_user = User('superuser@example.com', 'superuser', 'password', True)

#     # # Add the user to the database
#     # db.session.add(super_user)
#     # db.session.commit()

def tickets_allocated(event_id):
    return Ticket.query.filter_by(event_id=event_id, is_cancelled=False).count()

def tickets_allocated_user(event_id, user_id):
    return Ticket.query.filter_by(event_id=event_id, user_id=user_id, is_cancelled=False).count()