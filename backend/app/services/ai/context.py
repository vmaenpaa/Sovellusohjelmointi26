from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Literal

from ..analytics import (
	GRANULARITIES,
	SessionInput,
	build_series,
	build_streaks,
	summarize_sessions,
)

Period = Literal["week", "month"]

MAX_SESSIONS = 50
MAX_ACTIVITIES_PER_SESSION = 20
MAX_UNITS_PER_ACTIVITY = 10


def _period_window(period: Period, reference_time: datetime) -> tuple[datetime, datetime]:
	if period not in GRANULARITIES:
		raise ValueError(f"Unsupported period: {period}")

	period_start = reference_time.replace(hour=0, minute=0, second=0, microsecond=0)
	if period == "week":
		period_start -= timedelta(days=period_start.weekday())
		period_end = period_start + timedelta(days=7)
	else:
		period_start = period_start.replace(day=1)
		if period_start.month == 12:
			period_end = period_start.replace(
				year=period_start.year + 1, month=1, day=1
			)
		else:
			period_end = period_start.replace(month=period_start.month + 1, day=1)
	return period_start, period_end


def _default_reference_time() -> datetime:
	return datetime.now(timezone.utc)


def _field(value: object, name: str, default: Any = None) -> Any:
	if isinstance(value, Mapping):
		return value.get(name, default)
	return getattr(value, name, default)


def _json_number(value: Decimal | int | float | None) -> float | int | None:
	if value is None:
		return None
	if isinstance(value, Decimal):
		return float(value)
	return value


def _pack_session(session: SessionInput) -> dict[str, Any]:
	activities: list[dict[str, Any]] = []
	for item in session.items[:MAX_ACTIVITIES_PER_SESSION]:
		measurements: dict[str, dict[str, float | int]] = {}
		for measurement in item.measurements:
			if measurement.actual_value is None:
				continue
			summary = measurements.setdefault(
				measurement.unit_slug,
				{"total": 0.0, "count": 0},
			)
			summary["total"] += float(measurement.actual_value)
			summary["count"] += 1
		activities.append(
			{
				"activity_type_id": item.activity_type_id,
				"activity_type_slug": item.activity_type_slug,
				"measurements": dict(
					sorted(measurements.items())[:MAX_UNITS_PER_ACTIVITY]
				),
			}
		)

	return {
		"session_at": session.session_at.isoformat(),
		"intensity": session.intensity,
		"status": str(session.status),
		"activities": activities,
	}


def _pack_goal(goal: object) -> dict[str, Any]:
	return {
		"unit_type_id": _field(goal, "unit_type_id"),
		"activity_type_id": _field(goal, "activity_type_id"),
		"target_value": _json_number(_field(goal, "target_value")),
		"period": _field(goal, "period"),
	}


def build_context(
	sessions: Iterable[SessionInput],
	goals: Iterable[object],
	period: Period,
	*,
	reference_time: datetime | None = None,
) -> dict[str, Any]:
	"""Build a compact, JSON-friendly context pack from already scoped data."""
	reference_time = reference_time or _default_reference_time()
	period_start, period_end = _period_window(period, reference_time)
	period_sessions = sorted(
		(
			session
			for session in sessions
			if session.session_at is not None
			and period_start <= session.session_at < period_end
		),
		key=lambda session: session.session_at,
	)
	packed_sessions = period_sessions[-MAX_SESSIONS:]

	matching_goals = sorted(
		(
			goal
			for goal in goals
			if _field(goal, "active", True) and _field(goal, "period") == period
		),
		key=lambda goal: (
			_field(goal, "unit_type_id"),
			_field(goal, "activity_type_id") or 0,
		),
	)
	return {
		"period": period,
		"window": {
			"start": period_start.isoformat(),
			"end": period_end.isoformat(),
		},
		"sessions": [_pack_session(session) for session in packed_sessions],
		"goals": [_pack_goal(goal) for goal in matching_goals],
		"stats": {
			"summary": summarize_sessions(period_sessions),
			"progress": build_series(
				period_sessions,
				metric="session_count",
				granularity=period,
			),
			"streaks": build_streaks(
				period_sessions,
				today=reference_time.date(),
			),
		},
	}


def build_context_for_user(
	db: Any,
	user_id: int,
	period: Period,
	*,
	reference_time: datetime | None = None,
) -> dict[str, Any]:
	"""Load only one user's period data and build its context pack."""
	from ...repositories.goal import list_for_user as list_goals_for_user
	from ...repositories.session import list_scheduled_in_range
	from ..stats import _to_input

	reference_time = reference_time or _default_reference_time()
	period_start, period_end = _period_window(period, reference_time)
	sessions = list_scheduled_in_range(
		db,
		user_id,
		session_from=period_start,
		session_to=period_end - timedelta(microseconds=1),
	)
	goals = list_goals_for_user(db, user_id, active=True)
	return build_context(
		[_to_input(session) for session in sessions],
		goals,
		period,
		reference_time=reference_time,
	)
