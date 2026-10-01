from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Period = Literal["week", "month"]


class GoalCreate(BaseModel):
    unit_type_id: int
    activity_type_id: int | None = None
    target_value: Decimal = Field(gt=0)
    period: Period
    active: bool = True


class GoalUpdate(BaseModel):
    unit_type_id: int | None = None
    activity_type_id: int | None = None
    target_value: Decimal | None = Field(default=None, gt=0)
    period: Period | None = None
    active: bool | None = None

    @field_validator("unit_type_id", "target_value", "period", "active", mode="before")
    @classmethod
    def reject_null_for_required_fields(cls, value):
        # activity_type_id is the only nullable column; other fields cannot be cleared to null
        if value is None:
            raise ValueError("Field cannot be null")
        return value


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    unit_type_id: int
    activity_type_id: int | None
    target_value: Decimal
    period: Period
    active: bool
    created_at: datetime
