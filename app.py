from flask import Flask
from flask_migrate import Migrate
from flasgger import Swagger
from extensions import db, bcrypt
from routes.user_routes import user_bp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Build database URI from individual variables
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

# Swagger setup
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Spacer API",
        "description": "API documentation for Spacer project",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: **Bearer <JWT>**"
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
    app.run(debug=True)
