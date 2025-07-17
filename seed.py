from app import app, db
from models import User, Space
from extensions import bcrypt

with app.app_context():
    db.create_all()

    
    if not User.query.filter_by(email='admin@spacer.com').first():
        admin = User(
            name='Admin',
            email='admin@spacer.com',
            role='admin',
            password_hash=bcrypt.generate_password_hash('Admin123!').decode('utf-8')
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin already exists.")

    
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
            price_per_day=4000,
            is_available=True,
            main_image_url="https://example.com/space1.jpg"
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
            main_image_url="https://example.com/space2.jpg"
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
            main_image_url="https://example.com/space3.jpg"
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
            main_image_url="https://example.com/space4.jpg"
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
            main_image_url="https://example.com/space5.jpg"
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
            main_image_url="https://example.com/space6.jpg"
        )


        db.session.add_all([space1, space2, space3, space4, space5, space6])
        db.session.commit()
        print("Spaces seeded successfully!")
    else:
        print("Spaces already exist.")
