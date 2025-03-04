# Theatre API

A Django REST API service for a theatre booking system that allows visitors to make online reservations and choose seats without physically going to the theatre.

## Features

- User registration and authentication with JWT tokens
- Browse plays, performances, and theatre halls
- Make reservations with specific seat selection
- Administrator interface to manage theatre resources
- Interactive API documentation with Swagger and ReDoc

## Models

- **Plays**: Theatrical performances with title and description
- **Theatre Halls**: Venues with configurable rows and seats
- **Performances**: Scheduled shows with play, venue, and time
- **Actors**: Performers linked to plays
- **Genres**: Categories for plays
- **Reservations**: Bookings made by users
- **Tickets**: Specific seats reserved for performances

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/plays/` | List or create plays (admin only) |
| `/api/actors/` | List or create actors (admin only) |
| `/api/genres/` | List or create genres (admin only) |
| `/api/theatre-halls/` | List or create theatre halls (admin only) |
| `/api/performances/` | List or create performances (admin only) |
| `/api/reservations/` | List user's reservations or create new ones |
| `/api/tickets/` | List or create tickets |
| `/api/users/` | List users (admin only) |
| `/api/register/` | Register new users |
| `/api/token/` | Obtain JWT token |
| `/api/token/refresh/` | Refresh JWT token |
| `/api/schema/` | API schema |
| `/api/schema/swagger-ui/` | Swagger UI documentation |
| `/api/schema/redoc/` | ReDoc documentation |
| `/admin/` | Django admin interface |

## Technology Stack

- **Django**: Web framework
- **Django REST framework**: API toolkit
- **Simple JWT**: JWT authentication
- **drf-spectacular**: API documentation
- **Docker & Docker Compose**: Containerization
- **SQLite**: Database (for development)

## Setup and Installation

### Using Docker

1. Clone the repository:
   ```
   git clone https://github.com/zaietsmo/theatre-api.git
   cd theatre-api
   ```

2. Create a `.env` file based on `.env.sample`:
   ```
   cp .env.sample .env
   ```

3. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

4. The API will be available at `http://localhost:8000/api/`

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/zaietsmo/theatre-api.git
   cd theatre-api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. The API will be available at `http://localhost:8000/api/`

## API Usage Examples

### Authentication

Register a new user:
```
POST /api/register/
{
  "username": "user123",
  "password": "securepassword",
  "email": "user@example.com"
}
```

Obtain token:
```
POST /api/token/
{
  "username": "user123",
  "password": "securepassword"
}
```

### Making a Reservation

1. Find available performances:
   ```
   GET /api/performances/
   ```

2. Create a reservation with specific seats:
   ```
   POST /api/reservations/
   {
     "performance_id": 1,
     "seats": [
       {"row": 5, "seat": 10},
       {"row": 5, "seat": 11}
     ]
   }
   ```

## Documentation

Interactive API documentation is available at:
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## License

[MIT License](LICENSE)