from app import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)  # assumed FK
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed', name='payment_status_enum'), default='pending')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)  # assumed FK
    invoice_url = db.Column(db.String(255))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
