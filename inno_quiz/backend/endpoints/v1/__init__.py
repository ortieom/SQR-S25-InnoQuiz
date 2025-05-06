from fastapi import APIRouter
from .quiz import router as quiz_router
from .users import router as users_router
from .quiz_api import router as quiz_api_router

router = APIRouter(prefix="/v1")
router.include_router(users_router)
router.include_router(quiz_router)
router.include_router(quiz_api_router)
