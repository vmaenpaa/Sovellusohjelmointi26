from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.session import SessionStatus


class CalendarSessionRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	session_at: datetime
	status: SessionStatus
	plan_id: int | None
