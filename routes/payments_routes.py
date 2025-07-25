from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Payment, Invoice, Booking, User, Space
from datetime import datetime
import os
from mailjet_rest import Client


MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
MAILJET_SENDER_EMAIL = os.getenv("MAILJET_SENDER_EMAIL")
MAILJET_SENDER_NAME = os.getenv("MAILJET_SENDER_NAME")

payments_bp = Blueprint('payments', __name__)


def send_invoice_email(user, space,booking, invoice_url, name, email):
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')

    html_template = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
        <h2 style="color: #4CAF50;">📄 Invoice for Booking #{space.id}</h2>
        <p>Hello {user.name},</p>
        <p>Thank you for booking <strong>{space.title}</strong> at {space.location}.</p>
        <hr>
        <p><strong>Booking Date:</strong> {datetime.utcnow().strftime('%B %d, %Y')}</p>
        <p><strong>Capacity:</strong> {space.capacity}</p>
        <p><strong>Total Price:</strong> KSH{booking.amount:.2f}</p>
        <hr>
        <p>You can view your invoice <a href="{invoice_url}" style="color: #4CAF50;">here</a>.</p>
        <p>Kind regards,<br><strong>Spacer Team</strong></p>
    </div>
    """

    data = {
      'Messages': [
        {
          "From": {
            "Email": MAILJET_SENDER_EMAIL,
            "Name": MAILJET_SENDER_NAME
          },
          "To": [
            {
              "Email": email,
              "Name": name
            }
          ],
          "Subject": f"Your Invoice for Booking #{space.id}",
          "HTMLPart": html_template
        }
      ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        current_app.logger.error(f"Failed to send email: {result.json()}")

def send_payment_confirmation_email(name, email, space):
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')

    email_data = {
        'Messages': [
            {
                "From": {
                    "Email": MAILJET_SENDER_EMAIL,
                    "Name": MAILJET_SENDER_NAME
                },
                "To": [
                    {
                        "Email": email,
                        "Name": name
                    }
                ],
                "Subject": "Payment Confirmed for Your Booking",
                "TextPart": f"Hi {name}, your payment for '{space.title}' has been confirmed.",
                "HTMLPart": f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #4CAF50;">Hello {name},</h2>
                    <p>We're excited to let you know that your payment for the booking at <strong>{space.title}</strong> has been <span style="color:green;"><strong>confirmed</strong></span>.</p>
                    <p>Booking Details:</p>
                    <ul>
                        <li><strong>Space:</strong> {space.title}</li>
                        <li><strong>Location:</strong> {space.location}</li>
                        <li><strong>Payment Status:</strong> Confirmed</li>
                        <li><strong>Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</li>
                    </ul>
                    <p>Thank you for using <strong>Spacer</strong>!</p>
                    <br/>
                    <p style="font-size: 0.9em; color: #888;">This is an automated message. Please do not reply.</p>
                </div>
                """
            }
        ]
    }

    result = mailjet.send.create(data=email_data)
    if result.status_code != 200:
        current_app.logger.error(f"Failed to send email: {result.json()}")

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
    identity = get_jwt_identity()
    user = User.query.get(identity)
    
    if not user or user.role != 'client':
        return jsonify({"error": "Only clients can create payments"}), 403

    data = request.get_json()

    booking = Booking.query.get(data['booking_id'])

    if not booking or booking.client_id != user.id:
        return jsonify({"error": "Unauthorized or invalid booking"}), 403
    
    payment = Payment(
        booking_id=data['booking_id'],
        amount=data['amount'],
        payment_method=data['payment_method'],
        client_id=user.id,
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
    identity = get_jwt_identity()
    user = User.query.get(identity)
    

    if user.role == 'admin':
        # Admin can view all payments
        payments = Payment.query.all()
    elif user.role == 'client':
        # Clients can view only their payments
        payments = Payment.query.join(Booking).filter(Booking.client_id == user.id).all()
    elif user.role == 'owner':
        # Owners can view payments related to their spaces
        space_ids = [space.id for space in Space.query.filter_by(owner_id=user.id).all()]
        payments = Payment.query.join(Booking).filter(Booking.space_id.in_(space_ids)).all()
    else:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify([p.to_dict() for p in payments]), 200


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
    identity = get_jwt_identity()
    user = User.query.get(identity)

    payment = Payment.query.get_or_404(id)
    booking = Booking.query.get(payment.booking_id)

    if user.role == 'admin' or (user.role == 'client' and booking.client_id == user.id):
        return jsonify(payment.to_dict()), 200

    return jsonify({"error": "Unauthorized"}), 403

@payments_bp.route('/payments/<int:id>/confirm', methods=['PATCH'])
@jwt_required()
def confirm_payment(id):
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user or user.role != 'owner':
        return jsonify({"error": "Only space owners can confirm payments"}), 403

    payment = Payment.query.get_or_404(id)
    booking = Booking.query.get(payment.booking_id)
    space = Space.query.get(booking.space_id)

    if space.owner_id != user.id:
        return jsonify({"error": "Unauthorized: not your space"}), 403

    payment.payment_status = 'completed'
    payment.payment_date = datetime.utcnow()
    db.session.commit()
    # Get the client details
    client = User.query.get(booking.client_id)
    send_payment_confirmation_email(client.name, client.email, space)

    return jsonify({"message": "Payment confirmed and email sent", "payment": payment.to_dict()}), 200

    

@payments_bp.route('/owner/payments', methods=['GET'])

@jwt_required()
def get_owner_payments():
    user_id = get_jwt_identity()
    owner = User.query.get(user_id)

    if not owner or owner.role != 'owner':
        return jsonify({"error": "Unauthorized access"}), 403
    
    

    # Get all spaces owned by this user
    owner_space_ids = [space.id for space in Space.query.filter_by(owner_id=owner.id).all()]

    # Get all bookings for those spaces
    bookings = Booking.query.filter(Booking.space_id.in_(owner_space_ids)).all()
    booking_ids = [booking.id for booking in bookings]

    # Get invoices related to those bookings
    invoices = Invoice.query.filter(Invoice.booking_id.in_(booking_ids)).all()

    result = []
    for invoice in invoices:
        result.append({
            "invoice_id": invoice.id,
            "booking_id": invoice.booking_id,
            "client_id": invoice.client_id,
            "invoice_url": invoice.invoice_url,
            "issued_at": invoice.issued_at.strftime('%Y-%m-%d %H:%M'),
            "total_price": Booking.query.get(invoice.booking_id).total_price
        })

    return jsonify(result), 200


@payments_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    """
    Create a new invoice and send it via email
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
    responses:
      201:
        description: Invoice created
      400:
        description: Booking not confirmed or invalid
      409:
        description: Invoice already exists
    """
    data = request.get_json()
    booking_id = data.get('booking_id')
    issued_at = datetime.utcnow()
    if not booking_id:
        return jsonify({'message': 'Missing booking_id'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'message': 'Invalid or unconfirmed booking'}), 400

    # Check for existing invoice
    if Invoice.query.filter_by(booking_id=booking_id).first():
        return jsonify({'message': 'Invoice already exists'}), 409

    # Generate invoice_url (fake for now, real would be PDF or view route)
    invoice_url = f"https://spacer.com/invoice/{booking_id}"

    invoice = Invoice(
        booking_id=booking_id,
        invoice_url=invoice_url,
        client_id=booking.client_id,
        issued_at=issued_at
    )
    db.session.add(invoice)
    db.session.commit()
    client = User.query.get(booking.client_id)
    send_invoice_email(client, booking.space, invoice_url, client.name, client.email)

    # Send email using Mailjet
     

   
    return jsonify({'message': 'Invoice created and sent successfully'}), 201

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
