from __future__ import annotations

import json

import httpx

from ...core.config import Settings
from .base import AIProvider, StructuredInsight


class OllamaProvider(AIProvider):
	
	def __init__(
		self,
		settings: Settings | None = None,
		*,
		transport: httpx.AsyncBaseTransport | None = None,
	) -> None:
		provider_settings = settings or Settings()
		self.base_url = provider_settings.ollama_base_url.rstrip('/')
		self.model = provider_settings.ollama_model
		self.transport = transport

	async def generate_insight(self, context: dict[str, object]) -> StructuredInsight:
		if not self.model:
			raise ValueError('OLLAMA_MODEL must be configured')

		payload = {
			'model': self.model,
			'prompt': self._build_prompt(context),
			'stream': False,
		}
		async with httpx.AsyncClient(
			base_url=self.base_url,
			timeout=30.0,
			transport=self.transport,
		) as client:
			response = await client.post('/api/generate', json=payload)
			response.raise_for_status()
			model_response = response.json()['response']

		return {
			'summary': model_response,
			'strengths': [],
			'recommendations': [],
			'caveats': [],
		}

	@staticmethod
	def _build_prompt(context: dict[str, object]) -> str:
		serialized_context = json.dumps(context, default=str, sort_keys=True)
		return (
			'Generate a concise training insight from the following context. '
			f'Context: {serialized_context}'
		)
