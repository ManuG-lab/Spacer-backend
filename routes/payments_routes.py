from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Payment, Invoice

payments_bp = Blueprint('payments', __name__)



@payments_bp.route('/payments', methods=['POST'])
@jwt_required()
def create_payment():
    """
    Create a new payment
    ---
    tags: [Payments]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: payment
        required: true
        schema:
          properties:
            booking_id:
              type: integer
            amount:
              type: number
            payment_method:
              type: string
    responses:
      201:
        description: Payment created
    """
    data = request.get_json()
    payment = Payment(
        booking_id=data['booking_id'],
        amount=data['amount'],
        payment_method=data['payment_method']
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({
    'message': 'Payment created successfully',
    'payment': payment.to_dict()
}), 201



@payments_bp.route('/payments', methods=['GET'])
@jwt_required()
def get_all_payments():
    """
    Get all payments
    ---
    tags: [Payments]
    security:
      - Bearer: []
    responses:
      200:
        description: List of payments
    """
    payments = Payment.query.all()
    return jsonify([{
        'id': p.id,
        'booking_id': p.booking_id,
        'amount': p.amount,
        'payment_method': p.payment_method,
        'payment_status': p.payment_status,
        'payment_date': p.payment_date.isoformat()
    } for p in payments]), 200


@payments_bp.route('/payments/<int:id>', methods=['GET'])
@jwt_required()
def get_payment(id):
    """
    Get a payment by ID
    ---
    tags: [Payments]
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Payment data
    """
    payment = Payment.query.get_or_404(id)
    return jsonify({
        'id': payment.id,
        'booking_id': payment.booking_id,
        'amount': payment.amount,
        'payment_method': payment.payment_method,
        'payment_status': payment.payment_status,
        'payment_date': payment.payment_date.isoformat()
    })



@payments_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    """
    Create a new invoice
    ---
    tags: [Invoices]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: invoice
        required: true
        schema:
          properties:
            booking_id:
              type: integer
            invoice_url:
              type: string
    responses:
      201:
        description: Invoice created
    """
    data = request.get_json()
    invoice = Invoice(
        booking_id=data['booking_id'],
        invoice_url=data['invoice_url']
    )
    db.session.add(invoice)
    db.session.commit()
    return jsonify({'message': 'Invoice created successfully'}), 201


@payments_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_all_invoices():
    """
    Get all invoices
    ---
    tags: [Invoices]
    security:
      - Bearer: []
    responses:
      200:
        description: List of invoices
    """
    invoices = Invoice.query.all()
    return jsonify([{
        'id': i.id,
        'booking_id': i.booking_id,
        'invoice_url': i.invoice_url,
        'issued_at': i.issued_at.isoformat()
    } for i in invoices]), 200


@payments_bp.route('/invoices/<int:id>', methods=['GET'])
@jwt_required()
def get_invoice(id):
    """
    Get invoice by ID
    ---
    tags: [Invoices]
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Invoice data
    """
    invoice = Invoice.query.get_or_404(id)
    return jsonify({
        'id': invoice.id,
        'booking_id': invoice.booking_id,
        'invoice_url': invoice.invoice_url,
        'issued_at': invoice.issued_at.isoformat()
    })
