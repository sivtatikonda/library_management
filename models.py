# models.py

from datetime import datetime
from app import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    borrow_requests = db.relationship('BorrowRequest', backref='user', lazy=True)
    borrow_history = db.relationship('BorrowHistory', backref='user', lazy=True)


class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.String(120), unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    borrow_requests = db.relationship('BorrowRequest', backref='book', lazy=True)
    borrow_history = db.relationship('BorrowHistory', backref='book', lazy=True)


class BorrowRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    borrow_from = db.Column(db.DateTime, nullable=False)
    borrow_to = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pending')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BorrowHistory(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    borrow_from = db.Column(db.DateTime, nullable=False)
    borrow_to = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='borrowed')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
