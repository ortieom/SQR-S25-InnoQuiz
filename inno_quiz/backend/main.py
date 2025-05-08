from fastapi import FastAPI

from backend.endpoints import router as api_router

app = FastAPI(
    title="InnoQuiz API",
    description="""
    # InnoQuiz API

    This API allows users to create and participate in thematic quizzes.

    ## Features

    * **Authentication** - Register and login to access protected endpoints
    * **Quiz Creation** - Create quizzes with custom questions or import from external sources
    * **Quiz Participation** - Take quizzes and submit answers
    * **Leaderboard** - View top scores for each quiz

    ## Authentication

    Most endpoints require authentication using JWT tokens.
    Register a new account at `/v1/users/create` and login at `/v1/users/login` to get your token.

    ## External Data

    The API integrates with Open Trivia DB to import questions for quizzes.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "InnoQuiz Support",
        "email": "support@innoquiz.example.com",
    },
    license_info={
        "name": "MIT License",
    },
    openapi_tags=[
        {
            "name": "users",
            "description": "User registration, authentication and profile management",
        },
        {
            "name": "quiz",
            "description": "Quiz creation and management operations",
        },
        {
            "name": "quiz_api",
            "description": "Quiz participation, questions and leaderboard operations",
        },
        {
            "name": "question",
            "description": "Question creation and management",
        },
        {
            "name": "Health",
            "description": "API health check endpoints",
        },
    ]
)

app.include_router(api_router)
