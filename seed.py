from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Creating tables
    db.create_all()

    # Hardcoded admin
    if not User.query.filter_by(email='admin@spacer.com').first():
        admin = User(
            name='Admin',
            email='admin@spacer.com',
            role='admin',
            password_hash=generate_password_hash('Admin123!')
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin already exists.")
