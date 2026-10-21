from pydantic import BaseModel, Field


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
