import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS
from dotenv import load_dotenv
from models import db
from extensions import db, bcrypt
from routes.user_routes import user_bp
from routes.spaces_routes import spaces_bp
from routes.bookings_routes import bookings_bp
from routes.payments_routes import payments_bp
# from routes.admin import admin_bp
# Load environment variables from .env
load_dotenv()

def create_app(testing=True):
    app = Flask(__name__)

    # Determine environment
    flask_env = os.getenv("FLASK_ENV", "development")

    # Security and config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key')

    # Database configuration
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
    TESTING = True 

    # Swagger configuration
    app.config['SWAGGER'] = {
        'title': 'Spacer API',
        'uiversion': 3
    }

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    CORS(app)
    

    #  Handle JWT errors globally
@jwt.unauthorized_loader
def handle_missing_token(err):
    return jsonify({"error": "Authorization token is missing"}), 401

@jwt.invalid_token_loader
def handle_invalid_token(err):
    return jsonify({"error": "Invalid token"}), 422

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401

    # Swagger setup with JWT Bearer authentication
    Swagger(app, template={
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

    
    # with app.app_context():
    #     db.create_all()

    # Register Blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(spaces_bp, url_prefix='/api')
    app.register_blueprint(bookings_bp, url_prefix='/api')
    app.register_blueprint(payments_bp, url_prefix='/api')
    app.register_blueprint(admin_bp)


    # Home route
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Spacer API"})

    # Error handler example
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    return app

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_ENV", "development") == "development"
    app.run(debug=debug_mode)
