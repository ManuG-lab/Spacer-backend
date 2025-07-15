from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from routes.user_routes import user_bp
from models import db
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/spacer_db'
app.config['SECRET_KEY'] = 'your_secret_key'

# db.init_app(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# swagger config (initialization of swagger for bearer token)
swagger = Swagger(app, template={
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: **Bearer &lt;JWT&gt;**"
        }
    },
    "security": [{"Bearer": []}]
})


from models import User

# Registering Blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')

@app.route('/')
def home():
    return {"message": "Welcome to Spacer API"}

if __name__ == '__main__':
    app.run(debug=True)
