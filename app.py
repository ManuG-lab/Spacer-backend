import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS
from dotenv import load_dotenv

from extensions import db, bcrypt
from routes.user_routes import user_bp
from routes.spaces_routes import spaces_bp
from routes.bookings_routes import bookings_bp
from routes.payments_routes import payments_bp

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# --------------------------
# Environment and Config
# --------------------------
flask_env = os.getenv("FLASK_ENV", "development")

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretjwtkey')

# Database configuration
if flask_env == "production":
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
else:
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'spacer.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Swagger configuration
app.config['SWAGGER'] = {
    'title': 'Spacer API',
    'uiversion': 3
}

# --------------------------
# Initialize Extensions
# --------------------------
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# --------------------------
# Swagger Setup with JWT
# --------------------------
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
            "description": "Enter: **Bearer <your JWT>**"
        }
    },
    "security": [{"Bearer": []}]
})

# --------------------------
# JWT Error Handlers
# --------------------------
@jwt.unauthorized_loader
def unauthorized_callback(msg):
    return jsonify({"error": "Missing or invalid JWT token"}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(msg):
    return jsonify({"error": "Invalid token"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has been revoked"}), 401

@jwt.user_lookup_error_loader
def user_lookup_error_callback(jwt_header, jwt_payload):
    return jsonify({"error": "User not found"}), 404

# --------------------------
# Register Blueprints
# --------------------------
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(spaces_bp, url_prefix='/api/spaces')
app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

# --------------------------
# Home Route
# --------------------------
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Spacer API 🎉"})

# Error handler example
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

# --------------------------
# Run App
# --------------------------
if __name__ == '__main__':
    debug_mode = True if flask_env == "development" else False
    app.run(debug=debug_mode)
