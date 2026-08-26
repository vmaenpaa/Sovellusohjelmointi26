from fastapi import APIRouter

from ..schemas.health import HealthResponse
from ..services.health import get_health_status

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["health"])
def read_health() -> HealthResponse:
	return get_health_status()