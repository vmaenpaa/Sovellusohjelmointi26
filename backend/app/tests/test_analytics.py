"""Pure analytics tests. Run from the repository root:

	python3 -m pytest backend/app/tests/test_analytics.py
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from backend.app.services.analytics import (
	MeasurementInput,
	SessionInput,
	SessionItemInput,
	build_streaks,
	build_weekly_series,
	summarize_sessions,
)


@pytest.fixture
def analytics_sessions() -> list[SessionInput]:
	return [
		SessionInput(
			session_at=datetime(2024, 1, 1, 9),
			intensity=6,
			items=(
				SessionItemInput(
					activity_type_slug="running",
					measurements=(
						MeasurementInput(
							"duration_min", Decimal("30"), Decimal("60")
						),
						MeasurementInput("distance_km", Decimal("5"), Decimal("9")),
					),
				),
			),
		),
		SessionInput(
			session_at=datetime(2024, 1, 2, 9),
			intensity=8,
			items=(
				SessionItemInput(
					activity_type_slug="running",
					measurements=(
						MeasurementInput(
							"duration_min", Decimal("40"), Decimal("70")
						),
						MeasurementInput("distance_km", Decimal("6"), Decimal("10")),
					),
				),
			),
		),
		SessionInput(
			session_at=datetime(2024, 1, 3, 9),
			intensity=7,
			items=(
				SessionItemInput(
					activity_type_slug="bench_press",
					measurements=(
						MeasurementInput("reps", Decimal("10"), set_index=1),
						MeasurementInput("weight_kg", Decimal("40"), set_index=1),
						MeasurementInput("reps", Decimal("8"), set_index=2),
						MeasurementInput("weight_kg", Decimal("45"), set_index=2),
					),
				),
			),
		),
		SessionInput(
			session_at=datetime(2024, 1, 3, 17),
			intensity=9,
			items=(
				SessionItemInput(
					activity_type_slug="bench_press",
					measurements=(
						MeasurementInput("reps", Decimal("8"), set_index=1),
						MeasurementInput("weight_kg", Decimal("50"), set_index=1),
					),
				),
			),
		),
		SessionInput(
			session_at=datetime(2024, 1, 15, 9),
			intensity=10,
			items=(
				SessionItemInput(
					activity_type_slug="running",
					measurements=(
						MeasurementInput(
							"duration_min", Decimal("45"), Decimal("90")
						),
						MeasurementInput("distance_km", Decimal("7"), Decimal("12")),
					),
				),
			),
		),
		SessionInput(
			session_at=None,
			intensity=10,
			items=(
				SessionItemInput(
					activity_type_slug="running",
					measurements=(
						MeasurementInput("duration_min", Decimal("999")),
						MeasurementInput("distance_km", Decimal("999")),
					),
				),
			),
		),
	]


# Checks scheduled-session totals, actual measurement values, and activity breakdowns.
def test_summarize_sessions_uses_scheduled_actual_measurements(
	analytics_sessions: list[SessionInput],
) -> None:
	assert summarize_sessions(analytics_sessions) == {
		"session_count": 5,
		"total_duration_min": 115.0,
		"total_distance_km": 18.0,
		"average_intensity": 8.0,
		"by_activity_type": [
			{
				"activity_type_slug": "bench_press",
				"session_count": 2,
				"total_distance_km": 0.0,
				"total_duration_min": 0.0,
			},
			{
				"activity_type_slug": "running",
				"session_count": 3,
				"total_distance_km": 18.0,
				"total_duration_min": 115.0,
			},
		],
	}


# Checks ISO-week totals, empty-week filling, and activity-type filtering.
def test_build_weekly_series_has_stable_iso_week_buckets(
	analytics_sessions: list[SessionInput],
) -> None:
	assert build_weekly_series(analytics_sessions, metric="duration_min") == [
		{"period_label": "2024-W01", "period_start": "2024-01-01", "value": 70.0},
		{"period_label": "2024-W02", "period_start": "2024-01-08", "value": 0.0},
		{"period_label": "2024-W03", "period_start": "2024-01-15", "value": 45.0},
	]
	assert build_weekly_series(analytics_sessions, metric="session_count") == [
		{"period_label": "2024-W01", "period_start": "2024-01-01", "value": 4.0},
		{"period_label": "2024-W02", "period_start": "2024-01-08", "value": 0.0},
		{"period_label": "2024-W03", "period_start": "2024-01-15", "value": 1.0},
	]
	assert build_weekly_series(
		analytics_sessions,
		metric="session_count",
		activity_type_slug="running",
	) == [
		{"period_label": "2024-W01", "period_start": "2024-01-01", "value": 2.0},
		{"period_label": "2024-W02", "period_start": "2024-01-08", "value": 0.0},
		{"period_label": "2024-W03", "period_start": "2024-01-15", "value": 1.0},
	]


# Checks current/longest day streaks, duplicate-day handling, and stale history.
def test_build_streaks_counts_calendar_days_and_ignores_unscheduled(
	analytics_sessions: list[SessionInput],
) -> None:
	assert build_streaks(analytics_sessions, today=date(2024, 1, 3)) == {
		"current": 3,
		"longest": 3,
	}
	assert build_streaks(analytics_sessions, today=date(2024, 1, 4)) == {
		"current": 3,
		"longest": 3,
	}
	assert build_streaks(analytics_sessions, today=date(2024, 1, 20)) == {
		"current": 0,
		"longest": 3,
	}


# Checks that every analytics function handles empty history without errors.
def test_empty_sessions_return_empty_analytics() -> None:
	assert summarize_sessions([]) == {
		"session_count": 0,
		"total_duration_min": 0.0,
		"total_distance_km": 0.0,
		"average_intensity": 0.0,
		"by_activity_type": [], 
	}
	assert build_weekly_series([]) == []
	assert build_streaks([], today=date(2024, 1, 3)) == {
		"current": 0,
		"longest": 0,
	}
