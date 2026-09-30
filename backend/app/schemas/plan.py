from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.session import SessionStatus


class PlanCreate(BaseModel):
	name: str = Field(min_length=1, max_length=200)
	notes: str | None = None
	start_date: date | None = None
	length_weeks: int | None = Field(default=None, ge=1)


class PlanUpdate(BaseModel):
	name: str | None = Field(default=None, min_length=1, max_length=200)
	notes: str | None = None
	start_date: date | None = None
	length_weeks: int | None = Field(default=None, ge=1)

	@field_validator("name", mode="before")
	@classmethod
	def reject_null_for_required_fields(cls, value):
		if value is None:
			raise ValueError("Field cannot be null")
		return value


class PlanSessionSummary(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	session_at: datetime | None
	status: SessionStatus


class PlanRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	user_id: int
	name: str
	notes: str | None
	start_date: date | None
	length_weeks: int | None
	created_at: datetime
	updated_at: datetime


class PlanDetail(PlanRead):
	sessions: list[PlanSessionSummary]
