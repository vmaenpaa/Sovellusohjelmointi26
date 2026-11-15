from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


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
	summary: str = ""
	strengths: list[str] = Field(default_factory=list)
	recommendations: list[str] = Field(default_factory=list)
	caveats: list[str] = Field(default_factory=list)

	@model_validator(mode="before")
	@classmethod
	def normalize_sections(cls, value: object) -> dict[str, object]:
		if not isinstance(value, dict):
			return {}

		normalized: dict[str, object] = {
			"summary": (
				value.get("summary", "")
				if isinstance(value.get("summary", ""), str)
				else ""
			),
		}
		for section in ("strengths", "recommendations", "caveats"):
			section_value = value.get(section, [])
			normalized[section] = (
				[section_value]
				if isinstance(section_value, str)
				else [item for item in section_value if isinstance(item, str)]
				if isinstance(section_value, list)
				else []
			)
		return normalized
