"""
No I/O.
Callers pass lists that are already filtered to a single user.

Summary rules (single source of truth for the dashboard and /stats/summary):
- Duration and distance come from measurements by unit slug, ACTUAL values only
  (no planned fallback).
- Sessions with session_at=None are excluded from every number.
- Missing measurements count as 0; average intensity of an empty set is 0.
- Results are JSON-friendly (floats, lists, dicts).

Time series rules:
- Buckets use session_at; weeks are ISO weeks (Monday start, label "YYYY-Www").
- Sessions with null session_at are skipped.
- Empty weeks between the first and last session are included with value 0.
- session_at is bucketed in its own timezone; callers should normalize first.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Literal

Metric = Literal["session_count", "duration_min", "distance_km"]

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

# Helper functions for weekly time series aggregation.
def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())  # ISO Monday

# Returns the ISO week label for a given date.
def _week_label(d: date) -> str:
    iso_year, iso_week, _ = d.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"

# Returns the value of a session for a given metric and optional activity type filter.
def _session_value(
    session: SessionInput, metric: Metric, activity_type_slug: str | None
) -> Decimal:
    items = [
        i
        for i in session.items
        if activity_type_slug is None or i.activity_type_slug == activity_type_slug
    ]
    if metric == "session_count":
        # With a type filter, only sessions containing that type count.
        return Decimal(1 if items or activity_type_slug is None else 0)
    return sum((_item_total(i, metric) for i in items), Decimal(0))

# Builds a weekly time series for the given sessions, metric, and optional activity type filter.
def build_weekly_series(
    sessions: Iterable[SessionInput],
    metric: Metric = "session_count",
    activity_type_slug: str | None = None,
) -> list[dict]:
    """Chart points [{period_label, period_start, value}] per ISO week, oldest first."""
    if metric not in ("session_count", DURATION_SLUG, DISTANCE_SLUG):
        raise ValueError(f"Unsupported metric: {metric}")

    totals: dict[date, Decimal] = {}
    for s in _scheduled(sessions):  # skips null session_at
        start = _week_start(s.session_at.date())
        totals[start] = totals.get(start, Decimal(0)) + _session_value(
            s, metric, activity_type_slug
        )
    if not totals:
        return []

    points = []
    current, last = min(totals), max(totals)
    while current <= last:
        points.append(
            {
                "period_label": _week_label(current),
                "period_start": current.isoformat(),
                "value": float(totals.get(current, Decimal(0))),
            }
        )
        current += timedelta(days=7)
    return points
