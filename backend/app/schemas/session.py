from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SessionStatus(str, Enum):
	planned = "planned"
	in_progress = "in_progress"
	completed = "completed"


class SessionMeasurementCreate(BaseModel):
	unit_type_id: int
	planned_value: Decimal | None = None
	actual_value: Decimal | None = None
	set_index: int | None = Field(default=None, ge=0)


class SessionItemCreate(BaseModel):
	activity_type_id: int
	sort_order: int
	notes: str | None = None
	measurements: list[SessionMeasurementCreate] = Field(default_factory=list)


class SessionCreate(BaseModel):
	name: str = Field(min_length=1, max_length=200)
	session_at: datetime | None = None
	status: SessionStatus = SessionStatus.planned
	notes: str | None = None
	intensity: int | None = Field(default=None, ge=1, le=10)
	plan_id: int | None = None
	items: list[SessionItemCreate] = Field(default_factory=list)


class SessionUpdate(BaseModel):
	name: str | None = Field(default=None, min_length=1, max_length=200)
	session_at: datetime | None = None
	status: SessionStatus | None = None
	notes: str | None = None
	intensity: int | None = Field(default=None, ge=1, le=10)
	plan_id: int | None = None
	items: list[SessionItemCreate] | None = None

	@field_validator("name", "status", "items", mode="before")
	@classmethod
	def reject_null_for_required_fields(cls, value):
		if value is None:
			raise ValueError("Field cannot be null")
		return value


class SessionMeasurementRead(SessionMeasurementCreate):
	model_config = ConfigDict(from_attributes=True)

	id: int


class SessionItemRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	activity_type_id: int
	sort_order: int
	notes: str | None
	measurements: list[SessionMeasurementRead]


class SessionRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	user_id: int
	plan_id: int | None
	name: str
	session_at: datetime | None
	status: SessionStatus
	notes: str | None
	intensity: int | None
	source_session_id: int | None
	created_at: datetime
	updated_at: datetime
	items: list[SessionItemRead]
