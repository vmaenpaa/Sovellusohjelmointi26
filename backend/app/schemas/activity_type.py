from pydantic import BaseModel, ConfigDict, Field


class ActivityTypeUnitLinkCreate(BaseModel):
	unit_type_id: int
	sort_order: int
	is_required: bool
	per_set: bool


class UnitTypeRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	name: str
	slug: str
	label: str | None = Field(validation_alias="unit_label")


class ActivityTypeUnitLinkRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	unit_type_id: int
	sort_order: int
	is_required: bool
	per_set: bool
	unit_type: UnitTypeRead


class ActivityTypeCreate(BaseModel):
	name: str = Field(min_length=1)
	slug: str | None = None
	unit_links: list[ActivityTypeUnitLinkCreate] = Field(min_length=1)


class ActivityTypeRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	slug: str
	is_system: bool
	user_id: int | None
	unit_links: list[ActivityTypeUnitLinkRead]
