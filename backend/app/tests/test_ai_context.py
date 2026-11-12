import json
from datetime import datetime, timedelta
from decimal import Decimal

from backend.app.services.ai.context import MAX_SESSIONS, build_context
from backend.app.services.analytics import (
	MeasurementInput,
	SessionInput,
	SessionItemInput,
)


REFERENCE_TIME = datetime(2026, 11, 12, 12)


def _session(
	session_at: datetime | None,
	*,
	duration: str = "30",
	planned_duration: str = "60",
) -> SessionInput:
	return SessionInput(
		session_at=session_at,
		intensity=7,
		status="completed",
		items=(
			SessionItemInput(
				activity_type_id=4,
				activity_type_slug="running",
				measurements=(
					MeasurementInput(
						"duration_min",
						Decimal(duration),
						Decimal(planned_duration),
					),
				),
			),
		),
	)


def test_build_context_filters_current_period_and_packs_actual_values() -> None:
	context = build_context(
		[
			_session(datetime(2026, 11, 9, 8), duration="30"),
			_session(datetime(2026, 11, 16, 8), duration="90"),
			_session(None, duration="999"),
		],
		[
			{
				"unit_type_id": 1,
				"activity_type_id": 4,
				"target_value": Decimal("120.0"),
				"period": "week",
				"active": True,
			},
			{
				"unit_type_id": 2,
				"activity_type_id": None,
				"target_value": Decimal("10"),
				"period": "month",
				"active": True,
			},
			{
				"unit_type_id": 3,
				"activity_type_id": None,
				"target_value": Decimal("20"),
				"period": "week",
				"active": False,
			},
		],
		"week",
		reference_time=REFERENCE_TIME,
	)

	assert context["window"] == {
		"start": "2026-11-09T00:00:00",
		"end": "2026-11-16T00:00:00",
	}
	assert len(context["sessions"]) == 1
	assert context["sessions"][0]["session_at"] == "2026-11-09T08:00:00"
	assert context["sessions"][0]["activities"][0]["measurements"] == {
		"duration_min": {"total": 30.0, "count": 1}
	}
	assert context["goals"] == [
		{
			"unit_type_id": 1,
			"activity_type_id": 4,
			"target_value": 120.0,
			"period": "week",
		}
	]
	assert context["stats"]["summary"]["total_duration_min"] == 30.0
	assert json.dumps(context)


def test_build_context_uses_calendar_month_and_bounds_sessions() -> None:
	sessions = [
		_session(datetime(2026, 10, 31, 23, 59)),
		*(_session(datetime(2026, 11, day, 8)) for day in range(1, 30)),
		_session(datetime(2026, 12, 1, 0)),
	]

	context = build_context(
		sessions,
		[],
		"month",
		reference_time=REFERENCE_TIME,
	)

	assert context["window"] == {
		"start": "2026-11-01T00:00:00",
		"end": "2026-12-01T00:00:00",
	}
	assert len(context["sessions"]) == 29
	assert context["sessions"][0]["session_at"] == "2026-11-01T08:00:00"
	assert context["sessions"][-1]["session_at"] == "2026-11-29T08:00:00"
	assert context["stats"]["summary"]["session_count"] == 29


def test_build_context_caps_large_session_history() -> None:
	context = build_context(
		[
			_session(datetime(2026, 11, 1) + timedelta(hours=hour))
			for hour in range(MAX_SESSIONS + 5)
		],
		[],
		"month",
		reference_time=REFERENCE_TIME,
	)

	assert len(context["sessions"]) == MAX_SESSIONS
	assert context["stats"]["summary"]["session_count"] == MAX_SESSIONS + 5
