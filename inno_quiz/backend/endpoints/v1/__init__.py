from fastapi import APIRouter
from .quiz import router as quiz_router

router = APIRouter()
router.include_router(quiz_router)
