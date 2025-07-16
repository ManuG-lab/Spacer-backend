from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from models import db
from routes.spaces_routes import spaces_bp
from routes.bookings_routes import bookings_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://youruser:yourpassword@localhost:5432/spacer_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Spacer API",
        "description": "API documentation for the Spacer event space booking platform.",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: **Bearer &lt;your-JWT-token&gt;**"
        }
    },
    "security": [{"Bearer": []}]
})

app.register_blueprint(spaces_bp, url_prefix='/api')
app.register_blueprint(bookings_bp, url_prefix='/api')


@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Spacer API 🎉"})

if __name__ == '__main__':
    app.run(debug=True)
