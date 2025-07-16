from datetime import datetime
from extensions import db
from sqlalchemy.orm import relationship, backref 
from sqlalchemy_serializer import SerializerMixin

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_only = (
        'id', 'name', 'email', 'role', 'is_verified', 'created_at'
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('client','owner','admin', name='user_roles'), nullable=False, default='client')
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    spaces = db.relationship('Space', backref='owner', lazy=True)
    bookings = db.relationship('Booking', backref='client', lazy=True)
    payments = db.relationship('Payment', backref='client', lazy=True)
    invoices = db.relationship('Invoice', backref='client', lazy=True)
    serialize_rules = ('-password_hash', '-spaces.owner', '-bookings.client', '-payments.client', '-invoices.client')


    def __repr__(self):
        return f'<User {self.email}, {self.name}, {self.role}, Verified: {self.is_verified}>'

class Space(db.Model, SerializerMixin):
    __tablename__ = 'spaces'

    serialize_only = (
        'id', 'owner_id', 'title', 'description', 'location',
        'capacity', 'amenities', 'price_per_hour', 'price_per_day',
        'is_available', 'main_image_url', 'created_at'
    )

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
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

    bookings = db.relationship('Booking', backref='space', lazy=True)
    serialize_rules = ('-owner.password_hash', '-owner.spaces', '-bookings.space',)

    def __repr__(self):
        return f'<Space {self.title} by {self.owner.name}, {self.location}, Capacity: {self.capacity}>'

    

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
    payments = relationship('Payment', backref='booking', lazy=True)
    invoice = relationship('Invoice', backref='booking', uselist=False)


    serialize_rules = ('-client.password_hash', '-client.bookings', '-space.bookings',)

    def calculate_duration(self):
        delta = self.end_datetime - self.start_datetime
        self.duration_hours = int(delta.total_seconds() / 3600)

    def calculate_total_price(self):
        if self.space:
            hourly_price = self.space.price_per_hour
            self.total_price = round(hourly_price * self.duration_hours, 2)

    def __repr__(self):
        return f'<Booking {self.id} for {self.client.name} at {self.space.title}, Status: {self.status}>'

class Payment(db.Model, SerializerMixin):
    __tablename__ = 'payments'

    serialize_only = (
        'id', 'booking_id', 'amount', 'payment_method', 'payment_status', 'payment_date'
    )

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed', name='payment_status_enum'), default='pending')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    booking = relationship('Booking', backref='payments')
    serialize_rules = ('-booking.client.password_hash', '-booking.space.bookings',)

    def __repr__(self):
        return f'<Payment {self.id} for Booking {self.booking.id}, Amount: {self.amount}, Status: {self.payment_status}>'

class Invoice(db.Model, SerializerMixin):
    __tablename__ = 'invoices'

    serialize_only = (
        'id', 'booking_id', 'invoice_url', 'issued_at'
    )

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    invoice_url = db.Column(db.String(255), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    booking = relationship('Booking', backref='invoice')
    serialize_rules = ('-booking.client.password_hash', '-booking.space.bookings',)

    def __repr__(self):
        return f'<Invoice {self.id} for Booking {self.booking.id}, URL: {self.invoice_url}>'


