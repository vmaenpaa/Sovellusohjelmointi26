from typing import Any

from sqlalchemy.orm import Session

from .base import AIProvider, StructuredInsight
from .context import Period, build_context_for_user


async def generate_insight(
	db: Session,
	user_id: int,
	period: Period,
	provider: AIProvider,
	*,
	focus: str | None = None,
) -> StructuredInsight:
	context: dict[str, Any] = build_context_for_user(db, user_id, period)
	if focus is not None:
		context["focus"] = focus
	return await provider.generate_insight(context)