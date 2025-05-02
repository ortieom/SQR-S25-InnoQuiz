# Inno Quiz

A thematic quiz application with FastAPI backend and Streamlit frontend.

## Project Structure

```
inno_quiz/
├── backend/          # FastAPI backend application
│   ├── app/          # Application code
|   ├── domain/       # Domain objects and DTOs
|   ├── models/       # SQLAlchemy ORM models
|   ├── gateways/     # Code for interaction with external services
│   ├── alembic/      # Database migrations
│   └── tests/        # Backend tests
└── frontend/         # Streamlit frontend application
    └── app/          # Frontend code
```

## Setup

Navigate to `inno_quiz/`

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Replace placeholders in .env with your configuration
```

3. Initialize the database:
```bash
cd backend
alembic upgrade head
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend:
```bash
cd frontend
streamlit run app/main.py
```

## Development

- Backend API will be available at: http://localhost:8000
- API documentation at: http://localhost:8000/docs
- Frontend will be available at: http://localhost:8501 

## Database

The application uses SQLite as its database, which is stored in `inno_quiz.db` in the backend directory. This makes the application portable and easy to set up without requiring a separate database server.