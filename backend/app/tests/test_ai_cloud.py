"""Tests for the honest cloud provider stub."""

import asyncio

import pytest

from backend.app.services.ai.cloud import CloudProvider


def test_cloud_provider_fails_when_not_configured() -> None:
	with pytest.raises(ValueError, match="Cloud AI provider is not configured"):
		asyncio.run(
			CloudProvider().generate_insight(
				{"session_count": 3, "summary": "training data"}
			)
		)
