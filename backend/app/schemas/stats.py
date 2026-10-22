from enum import Enum

from pydantic import BaseModel, Field


class ProgressMetric(str, Enum):
    """session_count counts sessions; the rest are unit slugs (sum of actual values)."""

    session_count = "session_count"
    duration_min = "duration_min"
    distance_km = "distance_km"
    reps = "reps"
    weight_kg = "weight_kg"


class ProgressGranularity(str, Enum):
    week = "week"
    month = "month"


class ProgressPoint(BaseModel):
    period_label: str = Field(description='ISO week "YYYY-Www" or month "YYYY-MM".')
    period_start: str = Field(description="ISO date of the first day of the bucket.")
    value: float


class ProgressSeries(BaseModel):
    metric: ProgressMetric
    granularity: ProgressGranularity
    activity_type_id: int | None = None
    points: list[ProgressPoint]


class ActivityTypeSummary(BaseModel):
    activity_type_slug: str
    session_count: int = Field(description="Distinct sessions containing this activity type.")
    total_distance_km: float
    total_duration_min: float


class StatsSummary(BaseModel):
    session_count: int = Field(description="Scheduled sessions (non-null session_at) in the range.")
    total_duration_min: float = Field(description="Sum of actual duration_min measurements.")
    total_distance_km: float = Field(description="Sum of actual distance_km measurements.")
    average_intensity: float = Field(description="Mean intensity of sessions that have one; 0 if none.")
    by_activity_type: list[ActivityTypeSummary]


class StreakStats(BaseModel):
    current: int = Field(
        description=(
            "Current consecutive-day streak across all history. Today counts if "
            "active; otherwise the streak is anchored to yesterday."
        )
    )
    longest: int = Field(
        description="Longest consecutive-day streak across all history."
    )
