from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models import User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
import re

user_bp = Blueprint('users', __name__)

# Utility: Check if current user is admin
def is_admin():
    claims = get_jwt()
    return claims.get('role') == 'admin'

@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": "Logged out successfully"})
    #unset_jwt_cookies(response)  # Use this if you're storing tokens in cookies
    return response, 200
# --------------------------
# Register a new user
# --------------------------
@user_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error or email exists
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validation
    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(name=name, email=email, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# --------------------------
# Login and return JWT
# --------------------------
@user_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user and return JWT token
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity={
        "id": user.id,
        "role": user.role,
    }, expires_delta=timedelta(days=1))
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
    })

# --------------------------
# Get current user's profile
# --------------------------
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    Get current user's profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
    """
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })


#  Get all users (Admin only)
@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Get all users (Admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: List of users
      403:
        description: Admins only
    """
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role
    } for u in users])


#  Get user by ID (Admin only)
@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get a user by ID (Admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    """
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })


# Update user (Admin only)
@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update a user (Admin or self)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    """
    current_user_id = get_jwt_identity()
    if user_id != current_user_id and not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    if 'password' in data:
        user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    db.session.commit()
    return jsonify({
    "message": "User updated successfully",
    "user": {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
})


#  Delete user (Admin only)
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete a user (Admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    """
    if not is_admin():
        return jsonify({"error": "Admins only"}), 403
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})
