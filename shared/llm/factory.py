from functools import lru_cache
from typing import Any

from .config import LLMSettings
from .errors import LLMConfigurationError
from .local import LocalRetrievalProvider
from .provider import LLMProvider


def create_provider(
    settings: LLMSettings,
    *,
    client: Any | None = None,
) -> LLMProvider:
    if settings.provider in {"none", "local"}:
        return LocalRetrievalProvider(name=settings.provider)
    if settings.provider == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(settings, client=client)
    raise LLMConfigurationError(
        f"Unsupported LLM_PROVIDER '{settings.provider}'. Use none, local, or openai."
    )


@lru_cache(maxsize=1)
def get_configured_provider() -> LLMProvider:
    return create_provider(LLMSettings.from_env())


def reset_provider_cache() -> None:
    get_configured_provider.cache_clear()
