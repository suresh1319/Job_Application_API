# Job Application Management API

A Django REST Framework based API for managing job applications, built as an assignment.

## Features

- User authentication using JWT
- CRUD operations for Jobs and Applicants
- Application management with status tracking
- File upload support for resumes
- Search and filtering capabilities
- Pagination for list views
- API documentation using Swagger/ReDoc

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd jobportal
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|-------------------------|
| /api/token/ | POST | Get JWT token | No |
| /api/token/refresh/ | POST | Refresh JWT token | No |
| /api/applicants/ | GET, POST | List or create applicants | GET: Yes, POST: No |
| /api/applicants/{id}/ | GET, PUT, DELETE | Get, update, or delete an applicant | Yes |
| /api/jobs/ | GET, POST | List or create jobs | Yes |
| /api/jobs/{id}/ | GET, PUT, DELETE | Get, update, or delete a job | Yes |
| /api/apply/ | POST | Apply for a job | No |
| /api/applications/ | GET | List all applications | Yes |
| /api/applications/{id}/status/ | PATCH | Update application status | Admin only |

## Authentication

1. Get an access token:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "yourpassword"}'
   ```

2. Use the access token in your requests:
   ```
   Authorization: Bearer your.access.token.here
   ```

## API Documentation

- Swagger UI: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/

## Testing

Run the test suite:
```bash
python manage.py test
```

## Running with Docker

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The API will be available at http://localhost:8000/

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Enable debug mode | False |
| SECRET_KEY | Django secret key | - |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts | localhost,127.0.0.1 |
| DATABASE_URL | Database connection URL | sqlite:///db.sqlite3 |

## License

MIT
