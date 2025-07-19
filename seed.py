from app import app, db
from models import User, Space, Booking, Payment, Invoice
from extensions import bcrypt
from datetime import datetime, timedelta

with app.app_context():
    db.create_all()

    # Seed Admin
    if not User.query.filter_by(email='admin@spacer.com').first():
        admin = User(
            name='Admin',
            email='admin@spacer.com',
            role='admin',
            password_hash=bcrypt.generate_password_hash('Admin123!').decode('utf-8')
        )
        db.session.add(admin)
        print("Admin user created successfully!")
    else:
        admin = User.query.filter_by(email='admin@spacer.com').first()
        print("⚠️ Admin already exists.")

    # Seed Owners
    owners = []
    for i in range(1, 4):
        email = f"owner{i}@example.com"
        owner = User.query.filter_by(email=email).first()
        if not owner:
            owner = User(
                name=f"Owner {i}",
                email=email,
                role='owner',
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
            )
            db.session.add(owner)
        owners.append(owner)
    db.session.commit()

    # Seed Clients
    clients = []
    for i in range(1, 4):
        email = f"client{i}@example.com"
        client = User.query.filter_by(email=email).first()
        if not client:
            client = User(
                name=f"Client {i}",
                email=email,
                role='client',
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
            )
            db.session.add(client)
        clients.append(client)
    db.session.commit()

    # Seed Spaces
    if Space.query.count() == 0:
        spaces = [
            Space(
                owner_id=owner.id,
                title="Cozy Coworking Hub",
                description="A quiet coworking space with fast Wi-Fi and coffee.",
                location="Nairobi CBD",
                capacity=20,
                amenities="Wi-Fi, Coffee, Printer",
                price_per_hour=500,
                price_per_day=7000,
                is_available=True,
                main_image_url="https://www.pexels.com/photo/group-of-people-in-conference-room-1181304/"
            ),
            Space(
                owner_id=owner.id,
                title="Open Green Garden Venue",
                description="Perfect for outdoor events and meetups.",
                location="Karen",
                capacity=50,
                amenities="Garden, Stage, Parking",
                price_per_hour=800,
                price_per_day=6000,
                is_available=True,
                main_image_url="https://www.pexels.com/photo/white-wooden-rectangular-table-159213/"
            ),
            Space(
                owner_id=owner.id,
                title="Modern Meeting Room",
                description="Ideal for team meetings with projector and AC.",
                location="Westlands",
                capacity=10,
                amenities="Wi-Fi, Projector, AC, Whiteboard",
                price_per_hour=700,
                price_per_day=5000,
                is_available=True,
                main_image_url="https://www.pexels.com/photo/group-of-women-gathered-inside-conference-room-1181611/"
            ),
        ]
        db.session.add_all(spaces)
        db.session.commit()
        print("Spaces seeded successfully!")
    else:
        spaces = Space.query.all()
        print("Spaces already exist.")
        

    # Seed Bookings
    if Booking.query.count() == 0:
        bookings = []
        now = datetime.now()
        for i, client in enumerate(clients):
            booking = Booking(
                client_id=client.id,
                space_id=spaces[i % len(spaces)].id,
                start_datetime=now + timedelta(days=i),
                end_datetime=now + timedelta(days=i, hours=2),
                duration_hours=2,
                total_price=spaces[i % len(spaces)].price_per_hour * 2,
                status='confirmed',
                created_at=now + timedelta(days=i),
                updated_at=now + timedelta(days=i)
            )
            db.session.add(booking)
            bookings.append(booking)
        db.session.commit()
        print("Bookings seeded successfully!")
    else:
        bookings = Booking.query.all()
        print("Bookings already exist.")

    # Seed Payments
    if Payment.query.count() == 0:
        payments = []
        for booking in bookings:
            payment = Payment(
                booking_id=booking.id,
                client_id=booking.client_id,
                amount=booking.total_price,
                payment_method="mpesa",
                payment_status="completed",
                payment_date=booking.created_at
            )
            db.session.add(payment)
            payments.append(payment)
        db.session.commit()
        print("Payments seeded successfully!")
    else:
        payments = Payment.query.all()
        print("Payments already exist.")

    # Seed Invoices
    if Invoice.query.count() == 0:
        for booking in bookings:
            invoice = Invoice(
                booking_id=booking.id,
                client_id=booking.client_id,
                invoice_url=f"https://invoices.example.com/invoice_{booking.id}.pdf",
                issued_at=booking.created_at
            )
            db.session.add(invoice)
        db.session.commit()
        print("Invoices seeded successfully!")
    else:
        print("Invoices already exist.")
