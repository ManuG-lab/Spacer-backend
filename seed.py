from app import app, db
from models import User
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

