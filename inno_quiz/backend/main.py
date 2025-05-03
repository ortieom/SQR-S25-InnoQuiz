from fastapi import FastAPI

from .endpoints import router as api_router

app = FastAPI()

app.include_router(api_router)
