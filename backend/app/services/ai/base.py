from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class StructuredInsight(TypedDict):
	"""Structured insight returned by an AI provider."""

	summary: str
	strengths: list[str]
	recommendations: list[str]
	caveats: list[str]


class AIProvider(ABC):
	"""Vendor-neutral interface for generating structured insights."""

	@abstractmethod
	async def generate_insight(self, context: dict[str, object]) -> StructuredInsight:
		"""Generate an insight from the supplied context."""
		raise NotImplementedError
