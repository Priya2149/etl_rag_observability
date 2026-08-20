import pytest

from shared.llm import LLMConfigurationError, LLMSettings, create_provider
from shared.llm.local import LocalRetrievalProvider


def test_provider_selection_defaults_to_free_local_path():
    provider = create_provider(LLMSettings(provider="none"))

    assert isinstance(provider, LocalRetrievalProvider)
    assert provider.name == "none"
    assert provider.capabilities.streaming is True
    assert provider.capabilities.tool_calling is False


def test_provider_selection_supports_explicit_local_path():
    provider = create_provider(LLMSettings(provider="LOCAL"))

    assert isinstance(provider, LocalRetrievalProvider)
    assert provider.name == "local"


def test_openai_provider_requires_an_api_key():
    settings = LLMSettings(provider="openai", openai_model="test-model")

    with pytest.raises(LLMConfigurationError, match="OPENAI_API_KEY"):
        create_provider(settings)


def test_openai_provider_requires_a_model():
    settings = LLMSettings(provider="openai", openai_api_key="test-key")

    with pytest.raises(LLMConfigurationError, match="OPENAI_MODEL"):
        create_provider(settings)


def test_unknown_provider_fails_with_supported_options():
    with pytest.raises(LLMConfigurationError, match="none, local, or openai"):
        create_provider(LLMSettings(provider="unknown"))
