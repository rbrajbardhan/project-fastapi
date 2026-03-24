# Employee Management API

A robust REST API for managing employees and users built with **FastAPI**, featuring JWT authentication, SQLite database, and CORS support.

## Features

- ✅ **User Management** - Create and manage user accounts with secure password handling
- ✅ **Employee Management** - Add, update, and track employee information
- ✅ **JWT Authentication** - Secure endpoints with JWT tokens
- ✅ **CORS Support** - Cross-origin requests configured for flexibility
- ✅ **Database Persistence** - SQLite database with SQLAlchemy ORM
- ✅ **OAuth2** - OAuth2 password bearer authentication flow
- ✅ **API Documentation** - Auto-generated interactive docs with Swagger UI

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT, OAuth2, Passlib, python-jose
- **Validation**: Pydantic
- **Server**: Uvicorn

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project-fastapi
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Project Structure

```
project-fastapi/
├── main.py                 # Main application file with models, schemas, and endpoints
├── requirements.txt        # Python dependencies
├── app.db                  # SQLite database (auto-created)
├── venv/                   # Virtual environment
├── Notes/                  # Project documentation and notes
└── README.md              # This file
```

## Database Models

### User
- `id`: Integer (Primary Key)
- `fullname`: String
- `email`: String (Unique)
- `password`: String (Hashed)
- `employs`: Relationship to Employee records

### Employee
- `id`: Integer (Primary Key)
- `name`: String
- `email`: String (Unique)
- `isOnProject`: Boolean
- `experience`: Integer
- `completed`: Integer
- `description`: String
- `user_id`: Foreign Key (References User)

## Authentication

The API uses JWT-based authentication with the following flow:

1. User provides credentials (email and password)
2. Server validates and returns a JWT access token
3. Client includes token in Authorization header: `Authorization: Bearer <token>`
4. Protected endpoints verify the token before processing requests

## Environment Variables

Configure the following (currently hardcoded in main.py):

- `DATABASE_URL`: SQLite database path (default: `sqlite:///./app.db`)
- `SECRET_KEY`: JWT secret key (for production, use a strong secret)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## CORS Configuration

Currently allows requests from all origins (`["*"]`). **For production**, update the `allow_origins` list to include only trusted domains:

```python
allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
```

## Development Notes

- See `Notes/` folder for detailed documentation on:
  - REST architecture principles
  - FastAPI best practices
  - Authentication implementation
  - API versioning strategies

## Future Improvements

- [ ] Move configuration to `.env` file
- [ ] Implement proper logging
- [ ] Add request validation improvements
- [ ] Implement pagination for list endpoints
- [ ] Add email verification
- [ ] Implement refresh tokens
- [ ] Add unit and integration tests
- [ ] Use PostgreSQL instead of SQLite for production

## License

This project is open source. See the LICENSE file for details.

## Support

For issues, questions, or contributions, please refer to the project documentation in the `Notes/` folder.