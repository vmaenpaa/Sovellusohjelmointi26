"""
No I/O.
Callers pass lists that are already filtered to a single user.

Summary rules (single source of truth for the dashboard and /stats/summary):
- Duration and distance come from measurements by unit slug, ACTUAL values only
  (no planned fallback).
- Sessions with session_at=None are excluded from every number.
- Missing measurements count as 0; average intensity of an empty set is 0.
- Results are JSON-friendly (floats, lists, dicts).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

DURATION_SLUG = "duration_min"
DISTANCE_SLUG = "distance_km"


@dataclass(frozen=True)
class MeasurementInput:
    """One measurement value, identified by unit slug (e.g. duration_min, distance_km)."""

    unit_slug: str
    actual_value: Decimal | None = None
    planned_value: Decimal | None = None
    set_index: int | None = None


@dataclass(frozen=True)
class SessionItemInput:
    """One activity within a session, with its measurements."""

    activity_type_slug: str
    measurements: tuple[MeasurementInput, ...] = ()


@dataclass(frozen=True)
class SessionInput:
    """A session as plain data; intensity is 1-10 or None."""

    session_at: datetime | None
    intensity: int | None = None
    status: str = "completed"
    items: tuple[SessionItemInput, ...] = ()

    def measurement_values(self, unit_slug: str) -> list[Decimal]:
        """Actual values for a unit slug across all items; None values skipped."""
        return [
            m.actual_value
            for item in self.items
            for m in item.measurements
            if m.unit_slug == unit_slug and m.actual_value is not None
        ]

#Returns only have scheduled sessions (session_at is not None). 
def _scheduled(sessions: Iterable[SessionInput]) -> list[SessionInput]:
    return [s for s in sessions if s.session_at is not None]

# Calculates total values for a given measurement unit within a session item.
def _item_total(item: SessionItemInput, unit_slug: str) -> Decimal:
    return sum(
        (
            m.actual_value
            for m in item.measurements
            if m.unit_slug == unit_slug and m.actual_value is not None
        ),
        Decimal(0),
    )

#Counts all sessions and sums distance and duration per activity type.
def summarize_by_activity_type(sessions: Iterable[SessionInput]) -> list[dict]:
    """Per-type session count (distinct sessions), distance and duration; sorted by slug."""
    totals: dict[str, dict] = {}
    for session in _scheduled(sessions):
        #Seen activity types within this session to avoid double-counting session_count
        seen: set[str] = set()
        for item in session.items:
            entry = totals.setdefault(
                item.activity_type_slug,
                {
                    "activity_type_slug": item.activity_type_slug,
                    "session_count": 0,
                    "total_distance_km": Decimal(0),
                    "total_duration_min": Decimal(0),
                },
            )
            if item.activity_type_slug not in seen:
                seen.add(item.activity_type_slug)
                entry["session_count"] += 1
            entry["total_distance_km"] += _item_total(item, DISTANCE_SLUG)
            entry["total_duration_min"] += _item_total(item, DURATION_SLUG)
    return [
        {
            **entry,
            "total_distance_km": float(entry["total_distance_km"]),
            "total_duration_min": float(entry["total_duration_min"]),
        }
        for _, entry in sorted(totals.items())
    ]

# Summarizes all scheduled sessions, including total duration, distance, and average intensity.
def summarize_sessions(sessions: Iterable[SessionInput]) -> dict:
    """Period summary; intensity is averaged over sessions that have one, 0 if none."""
    scheduled = _scheduled(sessions)
    duration = sum((sum(s.measurement_values(DURATION_SLUG), Decimal(0)) for s in scheduled), Decimal(0))
    distance = sum((sum(s.measurement_values(DISTANCE_SLUG), Decimal(0)) for s in scheduled), Decimal(0))
    intensities = [s.intensity for s in scheduled if s.intensity is not None]
    average = round(sum(intensities) / len(intensities), 2) if intensities else 0
    return {
        "session_count": len(scheduled),
        "total_duration_min": float(duration),
        "total_distance_km": float(distance),
        "average_intensity": float(average),
        "by_activity_type": summarize_by_activity_type(scheduled),
    }
