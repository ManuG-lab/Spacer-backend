from flask import Blueprint, request, jsonify
from models import User, db
from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps
from app import app

user_bp = Blueprint('users', __name__)
bcrypt = Bcrypt(app)

SECRET_KEY = app.config['SECRET_KEY']

# JWT decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({"message": "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Register route
@user_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
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
      403:
        description: Cannot create admin account
    """
    data = request.json
    if 'role' in data and data['role'] == 'admin':
        return jsonify({"error": "Cannot create admin account"}), 403
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(name=data['name'], email=data['email'], password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

# Login route
@user_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "user@example.com"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Login successful, returns JWT token
        schema:
          type: object
          properties:
            token:
              type: string
            role:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, SECRET_KEY)
    return jsonify({"token": token, "role": user.role}), 200

# Profile route
@user_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    """
    Get Current User Profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: Returns user profile data
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
            role:
              type: string
      401:
        description: Unauthorized or invalid token
    """
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    })

