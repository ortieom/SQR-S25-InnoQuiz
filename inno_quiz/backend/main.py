from fastapi import FastAPI

from .endpoints import router as api_router
from .config import settings

app = FastAPI()

app.include_router(api_router)
