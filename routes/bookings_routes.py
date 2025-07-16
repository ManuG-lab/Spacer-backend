# routes/bookings_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Booking, Space
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
    data = request.get_json()

    space = Space.query.get_or_404(data['space_id'])

    new_booking = Booking(
        client_id=identity['id'],
        space_id=space.id,
        start_datetime=datetime.fromisoformat(data['start_datetime']),
        end_datetime=datetime.fromisoformat(data['end_datetime']),
    )

    new_booking.calculate_duration()
    new_booking.space = space
    new_booking.calculate_total_price()

    db.session.add(new_booking)
    db.session.commit()
    return jsonify(new_booking.to_dict()), 201


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
    bookings = Booking.query.filter_by(client_id=identity['id']).all()
    return jsonify([b.to_dict() for b in bookings]), 200


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
    bookings = Booking.query.join(Space).filter(Space.owner_id == identity['id']).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@bookings_bp.route('/bookings/<int:id>/approve', methods=['PATCH'])
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
    booking = Booking.query.get_or_404(id)

    if booking.space.owner_id != identity['id']:
        return jsonify({"error": "Unauthorized"}), 403

    booking.status = 'confirmed'
    db.session.commit()

    # Optional: Send email logic here
    return jsonify({"message": "Booking approved"}), 200


@bookings_bp.route('/bookings/<int:id>/decline', methods=['PATCH'])
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
    booking = Booking.query.get_or_404(id)

    if booking.space.owner_id != identity['id']:
        return jsonify({"error": "Unauthorized"}), 403

    booking.status = 'declined'
    db.session.commit()
    return jsonify({"message": "Booking declined"}), 200
