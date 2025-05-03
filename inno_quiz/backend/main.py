from fastapi import FastAPI

# Use relative imports when running from backend directory
from endpoints import router as api_router

app = FastAPI()

app.include_router(api_router)
