from app import app, db
from models import User, Space
from extensions import bcrypt

with app.app_context():
    db.create_all()

    #  Seed Admin
    
    if not User.query.filter_by(email='admin@spacer.com').first():
        admin = User(
            name='Admin',
            email='admin@spacer.com',
            role='admin',
            password_hash=bcrypt.generate_password_hash('Admin123!').decode('utf-8')
        )
        db.session.add(admin)
        print(" Admin user created successfully!")
    else:
        print("⚠️ Admin already exists.")

    #  Seed Owners
    owners = [
        {"name": f"Owner {i}", "email": f"owner{i}@example.com", "password": "password123"}
        for i in range(1, 8)
    ]
    for o in owners:
        if not User.query.filter_by(email=o["email"]).first():
            owner = User(
                name=o["name"],
                email=o["email"],
                role='owner',
                password_hash=bcrypt.generate_password_hash(o["password"]).decode('utf-8')
            )
            db.session.add(owner)

    # Seed Clients
    clients = [
        {"name": f"Client {i}", "email": f"client{i}@example.com", "password": "password123"}
        for i in range(1, 8)
    ]
    for c in clients:
        if not User.query.filter_by(email=c["email"]).first():
            client = User(
                name=c["name"],
                email=c["email"],
                role='client',
                password_hash=bcrypt.generate_password_hash(c["password"]).decode('utf-8')
            )
            db.session.add(client)

    db.session.commit()
    print(" Owners and Clients seeded successfully!")
    
    admin = User.query.filter_by(email='admin@spacer.com').first()

    
    if Space.query.count() == 0:
        space1 = Space(
            owner_id=admin.id,
            title="Cozy Coworking Hub",
            description="A quiet coworking space with fast Wi-Fi and coffee.",
            location="Nairobi CBD",
            capacity=20,
            amenities="Wi-Fi, Coffee, Printer",
            price_per_hour=500,
            price_per_day=7000,
            is_available=True,
            main_image_url="https://www.pexels.com/photo/group-of-people-in-conference-room-1181304/"
        )

        space2 = Space(
            owner_id=admin.id,
            title="Open Green Garden Venue",
            description="Perfect for outdoor events and meetups.",
            location="Karen",
            capacity=50,
            amenities="Garden, Stage, Parking",
            price_per_hour=800,
            price_per_day=6000,
            is_available=True,
            main_image_url="https://www.pexels.com/photo/white-wooden-rectangular-table-159213/"
        )
        space3 = Space(
            owner_id=admin.id,
            title="Modern Meeting Room",
            description="Ideal for team meetings with projector and AC.",
            location="Westlands",
            capacity=10,
            amenities="Wi-Fi, Projector, AC, Whiteboard",
            price_per_hour=700,
            price_per_day=5000,
            is_available=True,
            main_image_url="https://www.pexels.com/photo/group-of-women-gathered-inside-conference-room-1181611/"
        )

        space4 = Space(
            owner_id=admin.id,
            title="Photography Studio Loft",
            description="Fully equipped photo studio with lighting gear.",
            location="Kilimani",
            capacity=5,
            amenities="Studio lights, Backdrops, Changing room",
            price_per_hour=1200,
            price_per_day=9000,
            is_available=True,
            main_image_url="https://www.pexels.com/photo/square-beige-wooden-table-with-chairs-260928/"
        )

        space5 = Space(
            owner_id=admin.id,
            title="Event Hall - 100 Pax",
            description="Spacious event hall for conferences and celebrations.",
            location="Thika Road",
            capacity=100,
            amenities="Stage, Sound System, Parking, Catering",
            price_per_hour=2500,
            price_per_day=18000,
            is_available=True,
            main_image_url="https://www.pexels.com/photo/red-theater-chair-lot-near-white-concrete-pillars-269140/"
        )

        space6 = Space(
            owner_id=admin.id,
            title="Private Office Space",
            description="Secure and private office unit, ideal for startups.",
            location="Upper Hill",
            capacity=4,
            amenities="Wi-Fi, Desks, Lockable door, Printer",
            price_per_hour=1000,
            price_per_day=7500,
            is_available=True,
            main_image_url="https://www.pexels.com/photo/conference-room-236730/"
        )


        db.session.add_all([space1, space2, space3, space4, space5, space6])
        db.session.commit()
        print("Spaces seeded successfully!")
    else:
        print("Spaces already exist.")
