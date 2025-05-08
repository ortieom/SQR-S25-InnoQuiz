from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str


@router.get(
    "/ping", 
    response_model=HealthResponse,
    summary="Health Check Endpoint",
    description="Returns the current status of the API",
)
def health_check():
    """
    Check if the API is up and running.
    
    Returns:
        HealthResponse: Object containing the status "ok" if everything is working
    """
    return {"status": "ok"}
