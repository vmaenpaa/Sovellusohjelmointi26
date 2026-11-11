from __future__ import annotations

from .base import AIProvider, StructuredInsight


class CloudProvider(AIProvider):
	"""Stub for a future cloud AI provider.

	Future configuration may use environment variables such as
	``CLOUD_API_KEY`` and ``CLOUD_MODEL``. No credentials, SDK calls, or
	cloud requests are made until that integration is intentionally configured.
	"""

	async def generate_insight(self, context: dict[str, object]) -> StructuredInsight:
		"""Fail clearly until a cloud provider is configured."""
		raise ValueError("Cloud AI provider is not configured")
