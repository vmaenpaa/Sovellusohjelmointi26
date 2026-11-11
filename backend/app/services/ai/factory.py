from fastapi import Depends

from ...core.config import Settings, get_settings
from .base import AIProvider
from .cloud import CloudProvider
from .ollama import OllamaProvider


def create_ai_provider(settings: Settings) -> AIProvider:
	provider_name = settings.ai_provider.strip().lower()

	if provider_name == 'ollama':
		return OllamaProvider(settings)
	if provider_name == 'cloud':
		return CloudProvider()

	raise ValueError(
		f"Unknown AI provider '{settings.ai_provider}'. "
		"Supported providers are: ollama, cloud"
	)


def get_ai_provider(settings: Settings = Depends(get_settings)) -> AIProvider:
	return create_ai_provider(settings)
