import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from dotenv import load_dotenv

from extensions import db, bcrypt
from routes.user_routes import user_bp
from routes.spaces_routes import spaces_bp
from routes.bookings_routes import bookings_bp
from routes.payments_routes import payments_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
flask_env = os.getenv("FLASK_ENV", "development")

if flask_env == "production":
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///spacer.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {
    'title': 'Spacer API',
    'uiversion': 3
}

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Swagger setup with JWT Bearer authentication
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Spacer API",
        "description": "API documentation for the Spacer event space booking platform.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: **Bearer &lt;your JWT&gt;**"
        }
    },
    "security": [{"Bearer": []}]
})

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(spaces_bp, url_prefix='/api/spaces')
app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Spacer API 🎉"})

if __name__ == '__main__':
    app.run(debug=True)