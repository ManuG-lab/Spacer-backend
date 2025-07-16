from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed', name='payment_status_enum'), default='pending')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)
    invoice_url = db.Column(db.String(255), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
