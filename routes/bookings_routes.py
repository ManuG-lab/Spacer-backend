from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Booking, Space, User
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__)

# ✅ Create Booking (Client Only)
@bookings_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Create a new booking (client)
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user or user.role != 'client':
        return jsonify({"error": "Only clients can create bookings"}), 403

    data = request.get_json() or {}
    space = Space.query.get(data.get("space_id"))
    if not space:
        return jsonify({"error": "Space not found"}), 404

    try:
        start_datetime = datetime.fromisoformat(data.get('start_datetime'))
        end_datetime = datetime.fromisoformat(data.get('end_datetime'))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format"}), 400

    if start_datetime >= end_datetime:
        return jsonify({"error": "End time must be after start time"}), 400

    new_booking = Booking(
        client_id=user.id,
        space_id=space.id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        toal_price=0,  # This will be calculated later
    )

    # Calculate duration & total price
    new_booking.calculate_duration()
    new_booking.calculate_total_price()

    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "message": "Booking created successfully",
        "booking": new_booking.to_dict()
    }), 201


# ✅ Get Client's Bookings
@bookings_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_client_bookings():
    """
    Get bookings made by the logged-in client
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)
    print("JWT Identity:", get_jwt_identity())


    if not user or user.role != 'client':
        return jsonify({"error": "Only clients can view their bookings"}), 403

    bookings = Booking.query.filter_by(client_id=user.id).all()
    return jsonify([booking.to_dict() for booking in bookings]), 200


# ✅ Get Owner's Bookings
@bookings_bp.route('/owner/bookings', methods=['GET'])
@jwt_required()
def get_owner_bookings():
    """
    Get all bookings for spaces owned by the logged-in owner
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user or user.role != 'owner':
        return jsonify({"error": "Only owners can view bookings for their spaces"}), 403

    bookings = Booking.query.join(Space).filter(Space.owner_id == user.id).all()
    return jsonify([b.to_dict() for b in bookings]), 200


# ✅ Approve Booking
@bookings_bp.route('/owner/bookings/<int:id>/approve', methods=['PATCH'])
@jwt_required()
def approve_booking(id):
    """
    Approve a booking request (owner only)
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

    return jsonify({"message": "Booking approved", "booking": booking.to_dict()}), 200


# ✅ Decline Booking
@bookings_bp.route('/owner/bookings/<int:id>/decline', methods=['PATCH'])
@jwt_required()
def decline_booking(id):
    """
    Decline a booking request (owner only)
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
