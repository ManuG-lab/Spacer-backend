# routes/bookings_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Booking, Space, User, Payment, Invoice
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Create a new booking (client)
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    requestBody:
      required: true
    responses:
      201:
        description: Booking created
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)
    
    if not user or user.role != 'client':
        return jsonify({"error": "Only clients can create bookings"}), 403

    data = request.get_json()

    space = Space.query.get(data.get("space_id"))
    if not space:
        return jsonify({"error": "Space not found"}), 404

    try:
        start_datetime = datetime.fromisoformat(data['start_datetime'])
        end_datetime = datetime.fromisoformat(data['end_datetime'])
    except:
        return jsonify({"error": "Invalid date format"}), 400

    new_booking = Booking(
        client_id=user.id,
        space_id=space.id,
        start_datetime=start_datetime,
        duration_hours=(end_datetime - start_datetime).seconds // 3600,
        end_datetime=end_datetime
    )

    new_booking.space = space  

    new_booking.calculate_duration()
    new_booking.calculate_total_price()

    db.session.add(new_booking)
    db.session.commit()

    return jsonify({"message": "Booking created successfully", "booking_id": new_booking.id}), 201


@bookings_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_client_bookings():
    """
    Get bookings made by the logged-in client
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    responses:
      200:
        description: List of client's bookings
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user or user.role != 'client':
        return jsonify({"error": "Only clients can view their bookings"}), 403
    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can view their bookings"}), 403

    bookings = Booking.query.filter_by(client_id=user.id).all()
    return jsonify([booking.to_dict() for booking in bookings]), 200


@bookings_bp.route('/owner/bookings', methods=['GET'])
@jwt_required()
def get_owner_bookings():
    """
    Get all bookings made on owner's spaces
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    responses:
      200:
        description: List of bookings for spaces owned by the user
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can view bookings for their spaces"}), 403

    bookings = Booking.query.join(Space).filter(Space.owner_id == user.id).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@bookings_bp.route('/owner/bookings/<int:id>/approve', methods=['PATCH'])
@jwt_required()
def approve_booking(id):
    """
    Approve a booking request (owner)
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Booking approved
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can approve bookings"}), 403

    booking = Booking.query.get_or_404(id)

    if booking.space.owner_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403

    booking.status = 'confirmed'
    db.session.commit()

    return jsonify({"message": "Booking approved"}), 200


@bookings_bp.route('owner/bookings/<int:id>/decline', methods=['PATCH'])
@jwt_required()
def decline_booking(id):
    """
    Decline a booking request (owner)
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Booking declined
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can decline bookings"}), 403

    booking = Booking.query.get_or_404(id)

    if booking.space.owner_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403

    booking.status = 'declined'
    db.session.commit()

    return jsonify({"message": "Booking declined"}), 200

@bookings_bp.route('/admin/bookings', methods=['GET']) 
@jwt_required()
def get_all_bookings():
    """
    Get all bookings (admin)
    ---
    tags:
      - Bookings
    security:
      - Bearer: []
    responses:
      200:
        description: List of all bookings
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user or user.role != 'admin':
        return jsonify({"error": "Only admins can view all bookings"}), 403

    bookings = Booking.query.all()
    return jsonify([booking.to_dict() for booking in bookings]), 200 
