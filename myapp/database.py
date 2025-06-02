from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import pbkdf2_sha256

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('chats', lazy=True))
    
    # Use a callable to produce a new empty list by default
    chat_list = db.Column(db.JSON, nullable=False, default=lambda: [])

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    
    # room_id should be unique and not nullable
    room_id = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relationship to all ChatMessage instances for this room
    messages = db.relationship('ChatMessage', backref='message', lazy=True, cascade="all, delete-orphan")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400), nullable=False)
    
    # DateTime for timestamp, default to current time
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    sender_id = db.Column(db.Integer, nullable=False)
    sender_username = db.Column(db.String(50), nullable=False)
    
    # Foreign key points to messages.room_id
    room_id = db.Column(db.String(50), db.ForeignKey('messages.room_id'), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
