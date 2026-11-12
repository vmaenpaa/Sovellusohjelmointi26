from typing import Literal

from pydantic import BaseModel, Field, field_validator


class InsightRequest(BaseModel):
	period: Literal["week", "month"] = Field(
		description="Reporting period used to build the user's training context."
	)
	focus: str | None = Field(
		default=None,
		max_length=200,
		description="Optional coaching emphasis, such as recovery or running volume.",
	)

	@field_validator("focus")
	@classmethod
	def normalize_focus(cls, value: str | None) -> str | None:
		if value is None:
			return None
		value = value.strip()
		if not value:
			raise ValueError("focus must not be blank")
		return value


class InsightResponse(BaseModel):
	summary: str
	strengths: list[str]
	recommendations: list[str]
	caveats: list[str]
