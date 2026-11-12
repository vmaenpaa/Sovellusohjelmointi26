from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import InsightRequest, InsightResponse
from app.services.ai.base import AIProvider
from app.services.ai.factory import get_ai_provider
from app.services.ai.insights import generate_insight


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
	return InsightResponse(
		**await generate_insight(
			db,
			current_user.id,
			request.period,
			provider,
			focus=request.focus,
		)
	)
