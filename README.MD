## Spacer Backend API
The Spacer Backend API powers the event space booking platform. It handles user authentication, space listings, bookings, payments, and invoices with role-based permissions and secure JWT authentication.

## Features
- User registration & login with JWT authentication
- Role-based access (Client / Owner / Admin)
- Manage event spaces (Create, Update, Delete)
- Booking system with approval/decline flow
- Payments & invoice generation
- Integrated Swagger UI for API documentation

## Tech Stack
- Backend Framework: Flask (Python)

- Database: PostgreSQL (Production), SQLite (Development)

- ORM: SQLAlchemy

- Authentication: Flask-JWT-Extended

- Documentation: Flasgger (Swagger UI)

- Migrations: Flask-Migrate

- Hashing: Bcrypt

## Project Structure
```bash

spacer-backend/
├── app.py               # Main Flask app entry point
├── extensions.py        # Extensions (DB, JWT, Bcrypt)
├── models.py            # Database models
├── routes/              # API route blueprints
│   ├── user_routes.py
│   ├── spaces_routes.py
│   ├── bookings_routes.py
│   └── payments_routes.py
├── migrations/          # Database migrations
├── seed.py              # Sample data seeding script
├── requirements.txt     # Python dependencies
└── .env                 # Environment configuration
```
## Setup & Installation
1. Clone the Repository
```bash

    git clone https://github.com/<your-username>/spacer-backend.git
    cd spacer-backend
```
2. Create a Virtual Environment & Install Dependencies
```bash

    python3 -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
```
3. Configure Environment Variables
  Create a .env file in the root directory:
```bash

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spacerdb
```
### Database Setup
▶️ Initialize and apply migrations:

```bash

flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
▶️ (Optional) Seed the database:

```bash

python seed.py
```
▶️ Run the Application
Start the Flask development server:

```bash
flask run

API will be available at:
http://127.0.0.1:5000

Swagger UI:
http://127.0.0.1:5000/apidocs
```

## Authentication
All protected endpoints require JWT tokens.
Include your token in the Authorization header:


    Authorization: Bearer <your_jwt_token>
## API Endpoints Overview
| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| POST   | `/api/users/register` | Register a new user      |
| POST   | `/api/users/login`    | Login & get JWT token    |
| GET    | `/api/users/profile`  | Get current user profile |

Example Login Request:

```bash

curl -X POST http://127.0.0.1:5000/api/users/login \
-H "Content-Type: application/json" \
-d '{"email": "user@example.com", "password": "Password123"}'
Response:

json

{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "client"
  }


Spaces

| Method | Endpoint                  | Description                   |
| ------ | ------------------------- | ----------------------------- |
| GET    | `/api/spaces/spaces`      | List all spaces               |
| POST   | `/api/spaces/spaces`      | Create new space (Owner only) |
| PATCH  | `/api/spaces/spaces/{id}` | Update a space (Owner only)   |
| DELETE | `/api/spaces/spaces/{id}` | Delete a space (Owner only)   |

Bookings

| Method | Endpoint                              | Description                       |
| ------ | ------------------------------------- | --------------------------------- |
| POST   | `/api/bookings/bookings`              | Create a new booking              |
| GET    | `/api/bookings/bookings`              | Get bookings for logged-in client |
| PATCH  | `/api/bookings/bookings/{id}/approve` | Approve booking (Owner only)      |
| PATCH  | `/api/bookings/bookings/{id}/decline` | Decline booking (Owner only)      |


Payments

| Method | Endpoint                 | Description        |
| ------ | ------------------------ | ------------------ |
| POST   | `/api/payments/payments` | Create new payment |
| GET    | `/api/payments/invoices` | Get all invoices   |
```

## Testing with Postman
Import endpoints into Postman

Register or login to get a JWT token

Add token to Authorization → Bearer Token

Test all protected routes


## Contributing
- Fork the repo

- Create a new branch:

```bash

git checkout -b feature/your-feature
```
- Commit your changes:

```bash


git commit -m "Add your feature"
```
- Push the branch:

```bash

git push origin feature/your-feature
```
- Open a Pull Request 

## License
This project is licensed under the MIT License.

