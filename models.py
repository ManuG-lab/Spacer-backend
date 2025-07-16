
# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from flask_sqlalchemy import SQLAlchemy

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

class Space(db.Model, SerializerMixin):
    __tablename__ = 'spaces'

    serialize_only = (
        'id', 'owner_id', 'title', 'description', 'location',
        'capacity', 'amenities', 'price_per_hour', 'price_per_day',
        'is_available', 'main_image_url', 'created_at'
    )

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    amenities = db.Column(db.Text, nullable=True)
    price_per_hour = db.Column(db.Float, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    main_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

