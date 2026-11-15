from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import InsightRequest, InsightResponse
from app.services.ai.base import AIProvider
from app.services.ai.factory import get_ai_provider
from app.services.ai.insights import generate_insight
from app.services.ai.ollama import OllamaUnavailableError


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
	"/insights",
	response_model=InsightResponse,
	description=(
		"Generate structured coaching insights from the authenticated user's "
		"training data for the selected period."
	),
)
async def create_insight(
	request: InsightRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	provider: AIProvider = Depends(get_ai_provider),
) -> InsightResponse:
	try:
		insight = await generate_insight(
			db,
			current_user.id,
			request.period,
			provider,
			focus=request.focus,
		)
	except OllamaUnavailableError as exc:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail=str(exc),
		) from exc
	return InsightResponse(**insight)
