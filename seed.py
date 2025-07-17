from app import app, db
from models import User
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
