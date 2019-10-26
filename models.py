from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

atends = db.Table('atends',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                  db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
                  )


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    profile_image = db.Column(
        db.String(64), nullable=True, default='../static/images/default.jpg')

    email = db.Column(db.String(64), unique=True, index=True)

    username = db.Column(db.String(64), unique=True, index=True)

    password_hash = db.Column(db.String(128))

    attending = db.relationship(
        'Event', secondary='atends', backref=db.backref('attendees', lazy='dynamic'))

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"{self.username}"


class Event(db.Model):

    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    description = db.Column(db.String(250), nullable=False, default='Lorem ipsum dolor sit amet, ' \
                                                                    'consectetur adipiscing elit, sed do ' \
                                                                    'eiusmod tempor incididunt ut labore et ' \
                                                                    'dolore magna aliqua. Ut enim ad minim' \
                                                                    ' veniam, quis nostrud exercitation ' \
                                                                    'ullamco laboris nisi ut aliquip ex ' \
                                                                    'ea commodo consequat. Duis aute ' \
                                                                    'irure do')
    
    created_at = db.Column(
        db.DateTime, default=datetime.now)

    starts_at = db.Column(db.DateTime, nullable=False)

    ends_at = db.Column(db.DateTime, nullable=False)
    
    created_by = db.Column(db.String(64))

    def __init__(self, title, description, starts_at, ends_at, username):
        self.title = title
        self.description = description
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.created_by = username
