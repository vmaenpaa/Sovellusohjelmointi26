from __future__ import annotations

import json

import httpx

from ...core.config import Settings
from ...schemas.ai import InsightResponse
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
			'format': 'json',
			'stream': False,
		}
		async with httpx.AsyncClient(
			base_url=self.base_url,
			timeout=30.0,
			transport=self.transport,
		) as client:
			response = await client.post('/api/generate', json=payload)
			response.raise_for_status()
			model_response = response.json().get('response', '')

		return self._normalize_response(model_response)

	@staticmethod
	def _normalize_response(model_response: object) -> StructuredInsight:
		if not isinstance(model_response, str):
			return InsightResponse().model_dump()

		response_text = model_response.strip()
		if response_text.startswith('```') and response_text.endswith('```'):
			response_text = response_text[3:-3].strip()
			if response_text.lower().startswith('json'):
				response_text = response_text[4:].strip()

		try:
			parsed_response = json.loads(response_text)
		except json.JSONDecodeError:
			parsed_response = {}

		return InsightResponse.model_validate(parsed_response).model_dump()

	@staticmethod
	def _build_prompt(context: dict[str, object]) -> str:
		serialized_context = json.dumps(context, default=str, sort_keys=True)
		return (
			'Generate a concise training insight from the following context. '
			'Return only a valid JSON object with exactly these keys: '
			'"summary" (string), "strengths" (list of strings), '
			'"recommendations" (list of strings), and "caveats" (list of strings). '
			'Do not put all information in summary. Extract positive observations '
			'into strengths, actionable advice into recommendations, and risks, '
			'limitations, or missing data into caveats. Populate every list when '
			'the context supports it; use an empty string or list only when there '
			'is genuinely no relevant content. '
			f'Context: {serialized_context}'
		)
