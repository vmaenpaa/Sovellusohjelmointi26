"""
No I/O.
Callers pass lists that are already filtered to a single user.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


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
