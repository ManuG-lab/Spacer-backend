
from flask import Flask
from flask_migrate import Migrate
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from extensions import db, bcrypt
from routes.user_routes import user_bp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Build database URI dynamically from .env
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretjwtkey')  # For JWT
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Swagger setup


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from models import db
from routes import payments_bp

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spacer.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key' 
app.config['SWAGGER'] = {
    'title': 'Spacer Payments & Invoices API',
    'uiversion': 3
}


db.init_app(app)
jwt = JWTManager(app)
swagger = Swagger(app)


app.register_blueprint(payments_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Just for first-time setup

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


from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flasgger import Swagger
from models import db
from routes.spaces_routes import spaces_bp

app = Flask(__name__)

# Database config (update this for your actual credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/spacer_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Swagger with JWT Bearer auth


swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Spacer API",

        "description": "API documentation for Spacer project",
        "version": "1.0.0"


        "description": "API documentation for the Spacer event space booking platform.",

        "description": "API for managing space rentals",

        "version": "1.0"

    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",

            "description": "Enter: **Bearer <JWT>**"


            "description": "Enter: **Bearer &lt;your-JWT-token&gt;**"

            "description": "Enter: **Bearer &lt;your JWT&gt;**"


        }
    },
    "security": [{"Bearer": []}]
})


# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')

@app.route('/')
def home():
    return {"message": "Welcome to Spacer API"}

if __name__ == '__main__':


app.register_blueprint(spaces_bp, url_prefix='/api')
app.register_blueprint(bookings_bp, url_prefix='/api')


@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Spacer API 🎉"})

# Register Blueprints
app.register_blueprint(spaces_bp, url_prefix='/api')

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Spacer API"})


if __name__ == '__main__':


    app.run(debug=True)
