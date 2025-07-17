# routes/spaces_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Space

spaces_bp = Blueprint('spaces', __name__)

@spaces_bp.route('/spaces', methods=['GET'])
def get_spaces():
    """
    Get all available spaces
    ---
    tags:
      - Spaces
    responses:
      200:
        description: A list of spaces
    """
    spaces = Space.query.filter_by(is_available=True).all()
    return jsonify([s.to_dict() for s in spaces]), 200

@spaces_bp.route('/spaces/<int:id>', methods=['GET'])
def get_space(id):
    """
    Get a specific space by ID
    ---
    tags:
      - Spaces
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: A space object
    """
    space = Space.query.get_or_404(id)
    return jsonify(space.to_dict()), 200

@spaces_bp.route('/spaces', methods=['POST'])
@jwt_required()
def create_space():
    """
    Create a new space (owners only)
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

@spaces_bp.route('/spaces/<int:id>', methods=['PATCH'])
@jwt_required()
def update_space(id):
    """
    Update a space (owners only)
    ---
    tags:
      - Spaces
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: Updated space
    """
    space = Space.query.get_or_404(id)
    identity = get_jwt_identity()
    if identity['id'] != space.owner_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    for field in ['title', 'description', 'location', 'capacity', 'amenities',
                  'price_per_hour', 'price_per_day', 'is_available', 'main_image_url']:
        if field in data:
            setattr(space, field, data[field])

    db.session.commit()
    return jsonify(space.to_dict()), 200

@spaces_bp.route('/spaces/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_space(id):
    """
    Delete a space (owners only)
    ---
    tags:
      - Spaces
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: Space deleted
    """
    space = Space.query.get_or_404(id)
    identity = get_jwt_identity()
    if identity['id'] != space.owner_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(space)
    db.session.commit()
    return jsonify({"message": "Space deleted successfully"}), 200
