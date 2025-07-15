from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flasgger import Swagger
from models import db, Space

app = Flask(__name__)

# PostgreSQL Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/spacer_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'

# Extensions
db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Swagger with JWT bearer config
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Spacer API - Spaces",
        "description": "Endpoints for managing spaces",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Use format: Bearer <JWT token>"
        }
    },
    "security": [{"Bearer": []}]
})

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Spacer API (Spaces)"})

@app.route('/api/spaces', methods=['GET'])
def get_spaces():
    """
    Get all available spaces
    ---
    tags:
      - Spaces
    responses:
      200:
        description: List of all available spaces
    """
    spaces = Space.query.filter_by(is_available=True).all()
    return jsonify([space.to_dict() for space in spaces]), 200

@app.route('/api/spaces/<int:id>', methods=['GET'])
def get_space(id):
    """
    Get a specific space by ID
    ---
    tags:
      - Spaces
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Space details
    """
    space = Space.query.get_or_404(id)
    return jsonify(space.to_dict()), 200

@app.route('/api/spaces', methods=['POST'])
@jwt_required()
def create_space():
    """
    Create a new space (owner only)
    ---
    tags:
      - Spaces
    security:
      - Bearer: []
    requestBody:
      required: true
    responses:
      201:
        description: Space created
    """
    identity = get_jwt_identity()
    if identity['role'] != 'owner':
        return jsonify({"error": "Only owners can create spaces"}), 403

    data = request.get_json()
    space = Space(
        owner_id=identity['id'],
        title=data['title'],
        description=data['description'],
        location=data['location'],
        capacity=data['capacity'],
        amenities=data.get('amenities'),
        price_per_hour=data['price_per_hour'],
        price_per_day=data['price_per_day'],
        is_available=data.get('is_available', True),
        main_image_url=data.get('main_image_url')
    )
    db.session.add(space)
    db.session.commit()
    return jsonify(space.to_dict()), 201

@app.route('/api/spaces/<int:id>', methods=['PATCH'])
@jwt_required()
def update_space(id):
    """
    Update an existing space (owner only)
    ---
    tags:
      - Spaces
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
    security:
      - Bearer: []
    responses:
      200:
        description: Space updated
    """
    space = Space.query.get_or_404(id)
    identity = get_jwt_identity()
    if identity['id'] != space.owner_id:
        return jsonify({"error": "Unauthorized to update this space"}), 403

    data = request.get_json()
    space.title = data.get('title', space.title)
    space.description = data.get('description', space.description)
    space.location = data.get('location', space.location)
    space.capacity = data.get('capacity', space.capacity)
    space.amenities = data.get('amenities', space.amenities)
    space.price_per_hour = data.get('price_per_hour', space.price_per_hour)
    space.price_per_day = data.get('price_per_day', space.price_per_day)
    space.is_available = data.get('is_available', space.is_available)
    space.main_image_url = data.get('main_image_url', space.main_image_url)

    db.session.commit()
    return jsonify(space.to_dict()), 200

@app.route('/api/spaces/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_space(id):
    """
    Delete a space (owner only)
    ---
    tags:
      - Spaces
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
    security:
      - Bearer: []
    responses:
      200:
        description: Space deleted
    """
    space = Space.query.get_or_404(id)
    identity = get_jwt_identity()
    if identity['id'] != space.owner_id:
        return jsonify({"error": "Unauthorized to delete this space"}), 403

    db.session.delete(space)
    db.session.commit()
    return jsonify({"message": "Space deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
