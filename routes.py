from flask import Blueprint, jsonify, request
from models import db, Payment, Invoice
from flask_jwt_extended import jwt_required

bp = Blueprint('api', __name__)

# Example: Create a payment
@bp.route('/payments', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json()
    payment = Payment(
        booking_id=data['booking_id'],
        amount=data['amount'],
        payment_method=data.get('payment_method', 'card'),
        payment_status=data.get('payment_status', 'pending')
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({"message": "Payment created"}), 201

# Example: Get all invoices
@bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    invoices = Invoice.query.all()
    return jsonify([{
        "id": inv.id,
        "booking_id": inv.booking_id,
        "invoice_url": inv.invoice_url,
        "issued_at": inv.issued_at
    } for inv in invoices])
