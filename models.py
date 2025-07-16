# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

class Booking(db.Model, SerializerMixin):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'declined', name='booking_status'), default='pending')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship('User', backref='bookings')
    space = relationship('Space', backref='bookings')

    serialize_rules = ('-client.password_hash', '-client.bookings', '-space.bookings',)

    def calculate_duration(self):
        delta = self.end_datetime - self.start_datetime
        self.duration_hours = int(delta.total_seconds() / 3600)

    def calculate_total_price(self):
        if self.space:
            hourly_price = self.space.price_per_hour
            self.total_price = round(hourly_price * self.duration_hours, 2)
