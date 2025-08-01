
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Space, User
import cloudinary.uploader
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


spaces_bp = Blueprint('spaces', __name__)

@spaces_bp.route('/spaces/my', methods=['GET'])
@jwt_required()
def get_my_spaces():
    owner_id = int(get_jwt_identity())  
    
    
    my_spaces = Space.query.filter_by(owner_id=owner_id).all()
    
    return jsonify([space.to_dict() for space in my_spaces]), 200


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
      content:
        application/json:
          schema:
            type: object
            properties:
              title:
                type: string
              description:
                type: string
              location:
                type: string
              capacity:
                type: integer
              amenities:
                type: array
                items:
                  type: string
              price_per_hour:
                type: number
              price_per_day:
                type: number
              is_available:
                type: boolean
              main_image_url:
                type: string
    responses:
      201:
        description: Space created
      400:
        description: Missing required fields
      403:
        description: Only owners can create spaces
    """

    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can create spaces"}), 403

    try:
        data = request.get_json()
        print("Incoming data:", data)  # Debug

        # Extract fields
        title = data.get('title')
        description = data.get('description')
        location = data.get('location')
        capacity = data.get('capacity')
        amenities = data.get('amenities')  # Expecting a list
        price_per_hour = data.get('price_per_hour')
        price_per_day = data.get('price_per_day')
        is_available = data.get('is_available', True)
        main_image_url = data.get('main_image_url')

        # Validate required fields
        if not all([title, description, location, capacity, price_per_hour, price_per_day]):
            return jsonify({"error": "Missing required fields"}), 400
        
         # Upload image to Cloudinary if provided
        if main_image_url:
            try:
                upload_result = cloudinary.uploader.upload(
                    main_image_url,
                    folder="spacer/spaces"
                )
                main_image_url = upload_result.get("secure_url")
            except Exception as e:
                return jsonify({"error": f"Image upload failed: {str(e)}"}), 500

        # ✅ Convert amenities list to JSON string
        import json
        if isinstance(amenities, list):
            amenities = json.dumps(amenities)

        # ✅ Create new space
        new_space = Space(
            owner_id=identity,
            title=title,
            description=description,
            location=location,
            capacity=capacity,
            amenities=amenities,
            price_per_hour=price_per_hour,
            price_per_day=price_per_day,
            is_available=is_available,
            main_image_url=main_image_url,
            # created_at=datetime.utcnow(),
            # updated_at=datetime.utcnow()
        )

        db.session.add(new_space)
        db.session.commit()

        return jsonify({
            "message": "Space created successfully",
            "space": {
                "id": new_space.id,
                "title": new_space.title,
                "description": new_space.description,
                "location": new_space.location,
                "capacity": new_space.capacity,
                "amenities": json.loads(new_space.amenities),  # Convert back to list for response
                "price_per_hour": new_space.price_per_hour,
                "price_per_day": new_space.price_per_day,
                "is_available": new_space.is_available,
                "main_image_url": new_space.main_image_url
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


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
    user = User.query.get(identity)
    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can update spaces"}), 403

    if space.owner_id != user.id:
        return jsonify({"error": "Unauthorized: You don't own this space"}), 403

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
    user = User.query.get(identity)
    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can delete spaces"}), 403

    if space.owner_id != user.id:
        return jsonify({"error": "Unauthorized: You don't own this space"}), 403
    
    if space.bookings:  # Check for related bookings
        return jsonify({"error": "Cannot delete space with existing bookings."}), 400
    
    db.session.delete(space)
    db.session.commit()
    return jsonify({"message": "Space deleted successfully"}), 200
