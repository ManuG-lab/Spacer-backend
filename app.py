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
    app.run(debug=True)
